import binascii
import hashlib
import os

try:
    text_type = unicode
except NameError:
    text_type = str


ALGORITHM = 'pbkdf2_sha256'
ITERATIONS = 600000
SALT_BYTES = 16
KEY_BYTES = 32
MAX_ITERATIONS = 1000000


def _password_bytes(raw_password):
    if isinstance(raw_password, text_type):
        return raw_password.encode('utf-8')
    return raw_password


def _is_hex(value, length):
    return len(value) == length and all(
        character in '0123456789abcdefABCDEF' for character in value
    )


def _parse_report_password(encoded):
    if isinstance(encoded, bytes):
        try:
            encoded = encoded.decode('ascii')
        except UnicodeDecodeError:
            return None

    try:
        algorithm, rounds, salt, digest = encoded.split('$')
        rounds = int(rounds)
    except (AttributeError, TypeError, ValueError):
        return None

    if algorithm != ALGORITHM or rounds < 1 or rounds > MAX_ITERATIONS:
        return None
    if not _is_hex(salt, SALT_BYTES * 2) or not _is_hex(digest, KEY_BYTES * 2):
        return None

    return rounds, binascii.unhexlify(salt.encode('ascii')), digest.lower()


def _constant_time_compare(left, right):
    if len(left) != len(right):
        return False

    difference = 0
    for left_character, right_character in zip(left, right):
        if not isinstance(left_character, int):
            left_character = ord(left_character)
        if not isinstance(right_character, int):
            right_character = ord(right_character)
        difference |= left_character ^ right_character
    return difference == 0


def make_report_password(raw_password):
    salt = os.urandom(SALT_BYTES)
    digest = hashlib.pbkdf2_hmac(
        'sha256', _password_bytes(raw_password), salt, ITERATIONS, KEY_BYTES
    )
    return '%s$%s$%s$%s' % (
        ALGORITHM,
        ITERATIONS,
        binascii.hexlify(salt).decode('ascii'),
        binascii.hexlify(digest).decode('ascii'),
    )


def check_report_password(raw_password, encoded):
    parsed = _parse_report_password(encoded)
    if parsed is None:
        return False

    rounds, salt, expected_digest = parsed
    actual_digest = binascii.hexlify(hashlib.pbkdf2_hmac(
        'sha256', _password_bytes(raw_password), salt, rounds, KEY_BYTES
    )).decode('ascii')
    return _constant_time_compare(actual_digest, expected_digest)


def is_report_password_hash(encoded):
    return _parse_report_password(encoded) is not None
