import django
from datetime import datetime

from django.conf import settings
from django.core import mail
from django.core.management import call_command
from django.test import TestCase

from crime.models import Crime
from models import Moniton


class MonitonTestCase(TestCase):
    """
    Test operations for crime areas monitoring.
    """
    urls = 'monitor.urls'
    fixtures = ['monitor/fixtures/monitons.json', 'monitor/fixtures/crimes.json']

    def setUp(self):
        # App-local templates match this test's isolated URL configuration.
        original_dirs = settings.TEMPLATE_DIRS
        self.addCleanup(setattr, settings, 'TEMPLATE_DIRS', original_dirs)
        settings.TEMPLATE_DIRS = ()

    def test_get_subscribe(self):
        """
        Test accessing subscribe page.
        """
        response = self.client.get('/subscribe/')
        self.assertTemplateUsed(response, 'monitor/subscribe.html')

    def test_post_subscribe(self):
        """
        Test subscribing to monitor.
        """
        inputs = {
            'email': 'kegan@kegan.info',
            'lat': 1.1234,
            'lng': 1.1234,
            'top': 1.1234,
            'right': 1.1234,
            'bottom': 1.1234,
            'left': 1.1234,
            'zoom': 9,
        }
        response = self.client.post('/subscribe/', inputs)

        self.assertTrue(mail.outbox)
        self.assertEquals(mail.outbox[0].to, [inputs['email']])
        self.assertEquals(mail.outbox[0].subject, 'Malaysia Crime Monitor subscription')
        self.assertRedirects(response, '/subscribe/done/')

    def test_post_subscribe_email_invalid(self):
        """
        Test subscribing to monitor.
        """
        inputs = {
            'email': 'xxx',
            'top': 1.1234,
            'right': 1.1234,
            'bottom': 1.1234,
            'left': 1.1234,
            'zoom': 9,
        }
        response = self.client.post('/subscribe/', inputs, follow=True)
        self.assertFormError(response, 'form', 'email', 'Enter a valid e-mail address.')

    def test_get_unsubscribe_uuid_invalid(self):
        """
        Test getting unsubscription with invalid uuid.
        """
        response = self.client.get('/unsubscribe/%s/' % 'xxx')
        self.assertTemplateUsed(response, '404.html')

    def test_get_unsubscribe(self):
        """
        Test getting an unsubscription.
        """
        response = self.client.get('/unsubscribe/%s/' % '4ad2302c454311de8b3387c74347e6f7')
        self.assertTemplateUsed(response, 'monitor/unsubscribe.html')
        self.assertEquals(response.context['moniton'].email, 'zul@example.com')

    def test_post_unsubscribe_uuid_invalid(self):
        """
        Test unsubscription with invalid uuid.
        """
        response = self.client.post('/unsubscribe/%s/' % 'xxx')
        self.assertTemplateUsed(response, '404.html')

    def test_post_unsubscribe(self):
        """
        Test unsubscription.
        """
        response = self.client.post('/unsubscribe/%s/' % '5432a3fc49ff11de854c1730b0756f01', follow=True)
        self.assertTemplateUsed(response, 'monitor/unsubscribe_done.html')
        self.assertRaises(django.core.exceptions.ObjectDoesNotExist, Moniton.objects.get, email='leremy@example.com')

    def test_get_information(self):
        """
        Test showing the area of subscription.
        """
        response = self.client.get('/info/%s/' % '03619ac2453211de8c651fabc0151a16')
        self.assertTemplateUsed(response, 'monitor/information.html')
        self.assertEquals(response.context['moniton'], Moniton.objects.get(pk=1))

    def test_notification(self):
        """
        Test the correctness of notifications.
        """
        call_command("send_all", 2009, 1, 3, 0, 0, 0) # 2009-01-03 midnight

        self.assertEquals(len(mail.outbox), 3)

        self.assertEquals(mail.outbox[0].to, ['kegan@example.com'])
        self.assertNotEquals(mail.outbox[0].body.rfind('Terrible Crime Middle In Date'), -1)
        self.assertNotEquals(mail.outbox[0].body.rfind('Terrible Crime East'), -1)
        self.assertNotEquals(mail.outbox[0].body.rfind('Terrible Crime West'), -1)

        self.assertEquals(mail.outbox[1].to, ['zul@example.com'])
        self.assertNotEquals(mail.outbox[1].body.rfind('Terrible Crime Middle In Date'), -1)
        self.assertNotEquals(mail.outbox[1].body.rfind('Terrible Crime East'), -1)

        self.assertEquals(mail.outbox[2].to, ['leremy@example.com'])
        self.assertNotEquals(mail.outbox[2].body.rfind('Terrible Crime Middle In Date'), -1)
        self.assertNotEquals(mail.outbox[2].body.rfind('Terrible Crime West'), -1)

    def test_notification_none(self):
        """
        Test the correctness of notifications with no crimes in last 24 hours.
        """
        call_command("send_all", 2009, 1, 20, 0, 0, 0) # 2009-01-20 midnight
        self.assertFalse(mail.outbox)

    def tearDown(self):
        pass


class AreaNotificationTestCase(TestCase):
    """Send alerts only for reports inside or on the subscribed rectangle."""
    fixtures = ['monitor/fixtures/monitons.json', 'monitor/fixtures/crimes.json']

    def setUp(self):
        # Keep one subscriber and one report from the last 24 hours.
        Moniton.objects.exclude(pk=1).delete()
        Moniton.objects.filter(pk=1).update(
            lat=4.0, lng=102.0,
            top=5.0, bottom=3.0, left=100.0, right=105.0,
        )
        Crime.objects.exclude(pk=2).delete()

    def _notify_at(self, lat, lng):
        Crime.objects.filter(pk=2).update(lat=lat, lng=lng)
        call_command('send_all', 2009, 1, 3, 0, 0, 0)

    def test_report_inside_area_sends_notification(self):
        self._notify_at(4.0, 102.0)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, ['kegan@example.com'])
        self.assertIn('Terrible Crime Middle In Date', mail.outbox[0].body)

    def test_report_south_of_area_sends_no_notification(self):
        self._notify_at(2.9, 102.0)
        self.assertEqual(len(mail.outbox), 0)

    def test_report_north_of_area_sends_no_notification(self):
        self._notify_at(5.1, 102.0)
        self.assertEqual(len(mail.outbox), 0)

    def test_report_west_of_area_sends_no_notification(self):
        self._notify_at(4.0, 99.9)
        self.assertEqual(len(mail.outbox), 0)

    def test_report_east_of_area_sends_no_notification(self):
        self._notify_at(4.0, 105.1)
        self.assertEqual(len(mail.outbox), 0)

    def test_report_on_south_boundary_sends_notification(self):
        self._notify_at(3.0, 102.0)
        self.assertEqual(len(mail.outbox), 1)

    def test_report_on_north_boundary_sends_notification(self):
        self._notify_at(5.0, 102.0)
        self.assertEqual(len(mail.outbox), 1)

    def test_report_on_west_boundary_sends_notification(self):
        self._notify_at(4.0, 100.0)
        self.assertEqual(len(mail.outbox), 1)

    def test_report_on_east_boundary_sends_notification(self):
        self._notify_at(4.0, 105.0)
        self.assertEqual(len(mail.outbox), 1)

    def test_area_with_negative_longitudes_sends_notification(self):
        Moniton.objects.filter(pk=1).update(
            lng=-102.0, left=-105.0, right=-100.0,
        )
        self._notify_at(4.0, -102.0)
        self.assertEqual(len(mail.outbox), 1)
