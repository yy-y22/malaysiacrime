from datetime import datetime, timedelta
from xml.dom import minidom
from xml.etree import ElementTree

from django.conf import settings
from django.contrib.comments.models import Comment
from django.contrib.contenttypes.models import ContentType
from django.test import TestCase

from crime.models import Crime


class MainTestCase(TestCase):
    """
    Test accessing and browsing crime reports.
    """
    fixtures = ['main/fixtures/crimes', 'main/fixtures/comments']

    def setUp(self):
        pass

    def test_get_index(self):
        """
        Test accessing index page.
        """
        response = self.client.get('/')
        self.assertTemplateUsed(response, 'main/index.html')

        self.assertEquals(len(response.context['crimes']), 3)
        self.assertEquals(response.context['crimes'][0].id, 1)
        self.assertEquals(response.context['crimes'][1].id, 2)
        self.assertEquals(response.context['crimes'][2].id, 3)

    def test_get_recent_updated(self):
        """
        Test accessing most updated page.
        """
        response = self.client.get('/recent/updated/')
        self.assertTemplateUsed(response, 'main/recent_updated.html')

        self.assertEquals(len(response.context['crimes']), 3)
        self.assertEquals(response.context['crimes'][0].id, 3)
        self.assertEquals(response.context['crimes'][1].id, 2)
        self.assertEquals(response.context['crimes'][2].id, 1)

    def test_get_recent_commented(self):
        """
        Test accessing most commented page.
        """
        response = self.client.get('/recent/commented/')
        self.assertTemplateUsed(response, 'main/recent_commented.html')

        self.assertEquals(len(response.context['crimes']), 2)
        self.assertEquals(response.context['crimes'][0].id, 2)
        self.assertEquals(response.context['crimes'][1].id, 1)

    def test_get_sitemap(self):
        """
        Test accessing sitemap.xml.
        """
        response = self.client.get('/sitemap.xml')

        self.assertEquals(response.status_code, 200)
        root = ElementTree.fromstring(response.content)
        namespace = '{http://www.sitemaps.org/schemas/sitemap/0.9}'
        self.assertEquals(root.tag, namespace + 'urlset')
        self.assertEquals(
            [entry.find(namespace + 'loc').text for entry in root],
            [entry['location'] for entry in response.context['urlset']]
        )
        self.assertEquals(
            [entry.find(namespace + 'lastmod').text for entry in root],
            ['2009-04-01', '2009-04-30', '2009-05-01']
        )
        self.assertEquals(root.findall('.//' + namespace + 'priority'), [])

        self.assertEquals(response.context['urlset'][0]['location'], "http://example.com/crime/title/terrible-crime-2/")
        self.assertEquals(response.context['urlset'][1]['location'], "http://example.com/crime/title/kidnap-of-dpm/")
        self.assertEquals(response.context['urlset'][2]['location'], "http://example.com/crime/title/daylight-extortion/")

        self.assertEquals(response.context['urlset'][0]['lastmod'], datetime(2009,4,1))
        self.assertEquals(response.context['urlset'][1]['lastmod'], datetime(2009,4,30))
        self.assertEquals(response.context['urlset'][2]['lastmod'], datetime(2009,5,1))

    def tearDown(self):
        pass


def make_crimes(count, prefix='crime', **fields):
    crimes = []
    for i in range(count):
        crime = Crime(headline='%s %d' % (prefix, i), date=datetime(2010, 1, 1),
                      location='Kuala Lumpur', icon='gun', lat=3.1, lng=101.7, zoom=10,
                      details='details', author='author', password='secret', **fields)
        crime.save()
        crimes.append(crime)
    return crimes

def comment_on(object_pk, minute):
    """Comment `minute` minutes after a fixed time; a larger minute is more recent."""
    return Comment.objects.create(
        content_type=ContentType.objects.get_for_model(Crime), object_pk=str(object_pk),
        site_id=settings.SITE_ID, user_name='tester', comment='comment',
        submit_date=datetime(2010, 1, 1) + timedelta(minutes=minute))


class RecentCommentedTestCase(TestCase):
    """
    /recent/commented/: non-removed crimes ordered by latest comment, taken from the
    500 most recent comments, at most 200 crimes. Missing and removed crimes are
    skipped before the 200 limit is applied.
    """
    def commented(self):
        response = self.client.get('/recent/commented/')
        self.assertEquals(response.status_code, 200)
        self.assertContains(response, 'Recent Commented Malaysia Crimes')
        return [crime.pk for crime in response.context['crimes']]

    def test_no_comments(self):
        make_crimes(2)
        self.assertEquals(self.commented(), [])

    def test_duplicate_comments_listed_once_by_latest_comment(self):
        a, b = make_crimes(2)
        comment_on(a.pk, 1)
        comment_on(b.pk, 2)
        comment_on(a.pk, 3)
        self.assertEquals(self.commented(), [a.pk, b.pk])

    def test_exactly_200_commented_crimes(self):
        crimes = make_crimes(200)
        for minute, crime in enumerate(crimes):
            comment_on(crime.pk, minute)
        self.assertEquals(self.commented(), [c.pk for c in reversed(crimes)])

    def test_201_commented_crimes_returns_latest_200(self):
        """Original code raised KeyError: it loaded 200 crimes but iterated all 201 ids."""
        crimes = make_crimes(201)
        for minute, crime in enumerate(crimes):
            comment_on(crime.pk, minute)
        self.assertEquals(self.commented(), [c.pk for c in reversed(crimes)][:200])

    def test_comment_on_missing_crime_is_skipped(self):
        """Original code raised KeyError for a comment whose crime no longer exists."""
        crime = make_crimes(1)[0]
        comment_on(crime.pk, 1)
        comment_on(99999, 2)
        self.assertEquals(self.commented(), [crime.pk])

    def test_removed_crime_is_excluded(self):
        crime = make_crimes(1)[0]
        removed = make_crimes(1, prefix='removed', is_removed=True)[0]
        comment_on(crime.pk, 1)
        comment_on(removed.pk, 2)
        self.assertEquals(self.commented(), [crime.pk])

    def test_non_numeric_object_pk_is_skipped(self):
        """Original code raised ValueError from int('invalid-id')."""
        crime = make_crimes(1)[0]
        comment_on(crime.pk, 1)
        comment_on('invalid-id', 2)
        comment_on('99999999999999999999', 3)  # numeric, but too large for a database integer
        self.assertEquals(self.commented(), [crime.pk])

    def test_limit_counts_only_valid_crimes(self):
        """The newest comments point at a missing and a removed crime; 200 valid ones still show."""
        crimes = make_crimes(201)
        for minute, crime in enumerate(crimes):
            comment_on(crime.pk, minute)
        removed = make_crimes(1, prefix='removed', is_removed=True)[0]
        comment_on(removed.pk, 300)
        comment_on(99999, 301)
        self.assertEquals(self.commented(), [c.pk for c in reversed(crimes)][:200])

    def test_only_latest_500_comments_are_considered(self):
        a, b = make_crimes(2)
        comment_on(b.pk, 0)
        for minute in range(1, 501):
            comment_on(a.pk, minute)
        self.assertEquals(self.commented(), [a.pk])


class CommentedFeedTestCase(TestCase):
    """/feeds/commented.xml: same rules as the page, with a 10-comment window and 10 items."""
    def feed_links(self):
        response = self.client.get('/feeds/commented.xml')
        self.assertEquals(response.status_code, 200)
        self.assertTrue(response['Content-Type'].startswith('application/rss+xml'))
        items = minidom.parseString(response.content).getElementsByTagName('item')
        return [item.getElementsByTagName('link')[0].firstChild.data for item in items]

    def link(self, crime):
        return 'http://example.com' + crime.get_absolute_url()

    def test_no_comments(self):
        make_crimes(1)
        self.assertEquals(self.feed_links(), [])

    def test_lists_10_most_recently_commented(self):
        crimes = make_crimes(11)
        for minute, crime in enumerate(crimes):
            comment_on(crime.pk, minute)
        self.assertEquals(self.feed_links(), [self.link(c) for c in reversed(crimes)][:10])

    def test_skips_missing_and_removed_crimes(self):
        """Original code raised KeyError for the comment on a missing crime."""
        crime = make_crimes(1)[0]
        removed = make_crimes(1, prefix='removed', is_removed=True)[0]
        comment_on(crime.pk, 1)
        comment_on(removed.pk, 2)
        comment_on(99999, 3)
        comment_on('invalid-id', 4)
        self.assertEquals(self.feed_links(), [self.link(crime)])


class IndexPaginationTestCase(TestCase):
    """
    Homepage: active crimes, 20 per page, newest first with id as tie-breaker.
    Invalid page values give 404; an empty dataset still has a page 1.
    """
    def setUp(self):
        crimes = make_crimes(45)
        # All share one timestamp except the first, so ordering must fall back to -id.
        Crime.objects.update(created_at=datetime(2010, 1, 1))
        Crime.objects.filter(pk=crimes[0].pk).update(created_at=datetime(2011, 1, 1))
        # Newest of all, but removed: must never appear.
        make_crimes(1, prefix='removed', is_removed=True)
        self.expected = [crimes[0].pk] + [c.pk for c in reversed(crimes[1:])]

    def get(self, query):
        response = self.client.get('/' + query)
        self.assertEquals(response.status_code, 200)
        self.assertContains(response, 'id="map_index"')  # real template, not the stub
        return response

    def test_pages_are_ordered_and_sized(self):
        for query, expected in [('', self.expected[:20]), ('?page=1', self.expected[:20]),
                                ('?page=2', self.expected[20:40]), ('?page=3', self.expected[40:])]:
            response = self.get(query)
            self.assertEquals([c.pk for c in response.context['crimes']], expected)
            # The (WP3 Leaflet) map receives the same page of crimes as the list.
            self.assertEquals(response.content.count('markerLayer.addLayer(createMarker('), len(expected))

    def test_navigation_links(self):
        first, middle, last = self.get('?page=1'), self.get('?page=2'), self.get('?page=3')
        self.assertContains(first, 'href="?page=2"')
        self.assertNotContains(first, 'href="?page=0"')
        self.assertContains(first, 'Page 1 of 3')
        self.assertContains(middle, 'href="?page=1"')
        self.assertContains(middle, 'href="?page=3"')
        self.assertContains(last, 'href="?page=2"')
        self.assertNotContains(last, 'href="?page=4"')
        self.assertContains(last, 'Page 3 of 3')

    def test_invalid_pages_return_404(self):
        for query in ['?page=4', '?page=0', '?page=-1', '?page=abc', '?page=', '?page=1.5']:
            self.assertEquals(self.client.get('/' + query).status_code, 404, query)

    def test_total_counts_only_browsable_reports(self):
        """45 active and 1 removed: the page must say 45, the number a user can browse."""
        response = self.get('')
        self.assertEquals(response.context['crime_total'], 45)
        self.assertContains(response, 'Showing <strong>20</strong> of <strong>45</strong>')

    def test_empty_dataset_has_valid_first_page(self):
        Crime.objects.all().delete()
        response = self.get('')
        self.assertEquals(list(response.context['crimes']), [])
        self.assertContains(response, 'Page 1 of 1')
        self.assertNotContains(response, 'href="?page=')
        self.assertEquals(self.client.get('/?page=2').status_code, 404)
