from datetime import datetime, timedelta
from email.utils import parsedate
from xml.etree import ElementTree

from django.conf import settings
from django.contrib.comments.models import Comment
from django.contrib.contenttypes.models import ContentType
from django.test import TestCase

from crime.models import Crime


class FeedTestCase(TestCase):
    """Exercise the public RSS endpoints and parse their actual XML output."""

    def setUp(self):
        self.first = self._create_report('Report A', 0)
        self.second = self._create_report('Report B', 1)
        self.third = self._create_report('Report C', 2)
        # Creation order and update order must be distinguishable.
        Crime.objects.filter(pk=self.first.pk).update(
            updated_at=datetime(2009, 2, 3))
        Crime.objects.filter(pk=self.second.pk).update(
            updated_at=datetime(2009, 2, 2))
        Crime.objects.filter(pk=self.third.pk).update(
            updated_at=datetime(2009, 2, 1))

    def _create_report(self, headline, day):
        timestamp = datetime(2009, 1, 1) + timedelta(days=day)
        report = Crime.objects.create(
            headline=headline, date=timestamp.date(),
            location='Kuala Lumpur', icon='G_DEFAULT_ICON',
            lat=3.1, lng=101.7, zoom=12,
            details='**Important** report.', author='Reporter',
            password='test-password',
        )
        Crime.objects.filter(pk=report.pk).update(
            created_at=timestamp, updated_at=timestamp)
        return report

    def _comment(self, report, day):
        return Comment.objects.create(
            content_type=ContentType.objects.get_for_model(Crime),
            object_pk=str(report.pk), site_id=settings.SITE_ID,
            user_name='Reader', user_email='reader@example.com',
            comment='A comment',
            submit_date=datetime(2009, 3, 1) + timedelta(days=day),
            is_public=True, is_removed=False,
        )

    def _feed(self, name):
        response = self.client.get('/feeds/%s.xml' % name)
        self.assertEqual(response.status_code, 200)
        self.assertIn('xml', response['Content-Type'])
        root = ElementTree.fromstring(response.content)
        self.assertEqual(root.tag, 'rss')
        self.assertEqual(root.get('version'), '2.0')
        channel = root.find('channel')
        self.assertIsNotNone(channel)
        return channel

    def _titles(self, channel):
        return [item.find('title').text for item in channel.findall('item')]

    def test_latest_orders_reports_by_creation_date(self):
        channel = self._feed('latest')
        self.assertEqual(channel.find('title').text,
                         'Malaysia Crime Latest Reports')
        self.assertEqual(self._titles(channel),
                         ['Report C', 'Report B', 'Report A'])

    def test_updated_orders_reports_by_update_date(self):
        channel = self._feed('updated')
        self.assertEqual(channel.find('title').text,
                         'Malaysia Crime Recent Updated Reports')
        self.assertEqual(self._titles(channel),
                         ['Report A', 'Report B', 'Report C'])

    def test_commented_orders_reports_and_removes_duplicates(self):
        self._comment(self.first, 0)
        self._comment(self.second, 1)
        self._comment(self.second, 2)
        channel = self._feed('commented')
        self.assertEqual(channel.find('title').text,
                         'Malaysia Crime Recent Commented Reports')
        self.assertEqual(self._titles(channel), ['Report B', 'Report A'])

    def test_latest_excludes_removed_reports(self):
        Crime.objects.filter(pk=self.third.pk).update(is_removed=True)
        self.assertEqual(self._titles(self._feed('latest')),
                         ['Report B', 'Report A'])

    def test_updated_excludes_removed_reports(self):
        Crime.objects.filter(pk=self.first.pk).update(is_removed=True)
        self.assertEqual(self._titles(self._feed('updated')),
                         ['Report B', 'Report C'])

    def test_commented_excludes_removed_reports(self):
        self._comment(self.first, 0)
        self._comment(self.second, 1)
        Crime.objects.filter(pk=self.second.pk).update(is_removed=True)
        self.assertEqual(self._titles(self._feed('commented')), ['Report A'])

    def test_latest_limits_results_to_fifty_reports(self):
        for day in range(3, 55):
            self._create_report('Report %02d' % day, day)
        titles = self._titles(self._feed('latest'))
        self.assertEqual(len(titles), 50)
        self.assertEqual(titles[0], 'Report 54')
        self.assertEqual(titles[-1], 'Report 05')

    def test_updated_limits_results_to_ten_reports(self):
        for day in range(3, 15):
            self._create_report('Report %02d' % day, day)
        self.assertEqual(len(self._feed('updated').findall('item')), 10)

    def test_commented_limits_results_to_ten_reports(self):
        reports = [self.first, self.second, self.third]
        for day in range(3, 15):
            reports.append(self._create_report('Report %02d' % day, day))
        for day, report in enumerate(reports):
            self._comment(report, day)
        titles = self._titles(self._feed('commented'))
        self.assertEqual(len(titles), 10)
        self.assertEqual(titles[0], 'Report 14')
        self.assertEqual(titles[-1], 'Report 05')

    def test_commented_feed_is_empty_without_comments(self):
        self.assertEqual(self._feed('commented').findall('item'), [])

    def test_feeds_are_valid_and_empty_without_reports(self):
        Crime.objects.all().delete()
        for name in ('latest', 'updated', 'commented'):
            self.assertEqual(self._feed(name).findall('item'), [])

    def test_items_include_links_dates_authors_categories_and_coordinates(self):
        self._comment(self.first, 0)
        expected_titles = {
            'latest': 'Report C', 'updated': 'Report A', 'commented': 'Report A',
        }
        for name in ('latest', 'updated', 'commented'):
            item = self._feed(name).find('item')
            report = Crime.objects.get(headline=expected_titles[name])
            self.assertEqual(item.find('link').text,
                             'http://example.com' + report.get_absolute_url())
            self.assertEqual(item.find('category').text, 'G_DEFAULT_ICON')
            creator = item.find('{http://purl.org/dc/elements/1.1/}creator')
            self.assertEqual(creator.text, 'Reporter')
            self.assertEqual(parsedate(item.find('pubDate').text)[:6],
                             report.updated_at.timetuple()[:6])
            point = item.find('{http://www.georss.org/georss}point')
            self.assertEqual([float(value) for value in point.text.split()],
                             [report.lat, report.lng])

    def test_titles_with_xml_characters_remain_valid(self):
        headline = 'Report & <example>'
        Crime.objects.filter(pk=self.first.pk).update(headline=headline)
        self._comment(self.first, 0)
        for name in ('latest', 'updated', 'commented'):
            self.assertIn(headline, self._titles(self._feed(name)))

    def test_latest_description_contains_location_and_formatted_details(self):
        description = self._feed('latest').find('item/description').text
        self.assertIn('Kuala Lumpur', description)
        self.assertIn('<strong>Important</strong>', description)

    def test_unknown_feed_returns_not_found(self):
        self.assertEqual(self.client.get('/feeds/missing.xml').status_code, 404)

