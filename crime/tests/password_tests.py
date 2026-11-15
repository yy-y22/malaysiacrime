from django.test import TestCase

from crime.passwords import (
    check_report_password,
    is_report_password_hash,
    make_report_password,
)


class ReportPasswordTestCase(TestCase):
    def test_password_hash_is_salted_and_verifiable(self):
        first_hash = make_report_password('correct horse')
        second_hash = make_report_password('correct horse')

        self.assertNotEqual(first_hash, second_hash)
        self.assertTrue(is_report_password_hash(first_hash))
        self.assertTrue(check_report_password('correct horse', first_hash))
        self.assertFalse(check_report_password('wrong password', first_hash))

    def test_malformed_hash_is_rejected(self):
        self.assertFalse(is_report_password_hash('plaintext'))
        self.assertFalse(check_report_password('plaintext', 'plaintext'))
