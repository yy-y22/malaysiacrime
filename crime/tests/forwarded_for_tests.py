from django.http import HttpRequest
from django.test import TestCase

from malaysiacrime import SetRemoteAddrFromForwardedFor


class ForwardedForTestCase(TestCase):
    def setUp(self):
        self.middleware = SetRemoteAddrFromForwardedFor()
        self.request = HttpRequest()
        self.request.META['REMOTE_ADDR'] = '127.0.0.1'

    def test_missing_forwarded_address_keeps_remote_addr(self):
        self.middleware.process_request(self.request)

        self.assertEqual(self.request.META['REMOTE_ADDR'], '127.0.0.1')

    def test_valid_forwarded_address_is_used(self):
        self.request.META['HTTP_X_FORWARDED_FOR'] = '203.0.113.10'

        self.middleware.process_request(self.request)

        self.assertEqual(self.request.META['REMOTE_ADDR'], '203.0.113.10')

    def test_first_address_in_forwarded_list_is_used(self):
        self.request.META['HTTP_X_FORWARDED_FOR'] = '203.0.113.10, 10.0.0.1'

        self.middleware.process_request(self.request)

        self.assertEqual(self.request.META['REMOTE_ADDR'], '203.0.113.10')

    def test_invalid_forwarded_address_does_not_replace_remote_addr(self):
        invalid_addresses = (
            'not-an-ip',
            '203.0.113.256',
            '203.0.113',
            '203.000.113.10',
        )

        for address in invalid_addresses:
            self.request.META['HTTP_X_FORWARDED_FOR'] = address
            self.middleware.process_request(self.request)
            self.assertEqual(self.request.META['REMOTE_ADDR'], '127.0.0.1')
