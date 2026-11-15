# Security Maintenance Record

This document records the corrective and preventive maintenance changes made
for this repository. The project is a legacy Django 1.3 application using
Python 2.7 and South migrations.

## 1. Client IP forwarding

### Problem

The project middleware in [`__init__.py`](./__init__.py) copied the first value
from `X-Forwarded-For` directly into `REMOTE_ADDR` without checking whether it
was a valid IP address. Malformed or attacker-controlled header values could
therefore be treated as client addresses by code that trusts `REMOTE_ADDR`.

### Fix

The middleware now validates the first comma-separated value as canonical IPv4:

- It requires four decimal octets.
- Each octet must be between 0 and 255, without leading zeroes.
- Missing or invalid values leave the original `REMOTE_ADDR` unchanged.
- For a valid list, the existing convention of using the left-most address is
  retained.

Focused cases are covered in
[`crime/tests/forwarded_for_tests.py`](./crime/tests/forwarded_for_tests.py).

### Deployment consideration

Syntax validation does **not** make an untrusted forwarding header trustworthy.
Only enable this middleware when the application is behind a trusted proxy that
strips or safely replaces client-supplied forwarding headers. This implementation
accepts IPv4 addresses only.

## 2. CSRF protection

### Problem

`CsrfViewMiddleware` was commented out in the default settings, leaving
state-changing POST requests without Django's CSRF enforcement. The app-level
monitor unsubscribe form also did not contain a CSRF token. In this legacy Django
version, simply adding `{% csrf_token %}` was not enough: views supplied a
`RequestContext` as the positional template dictionary, so template context
processors did not reliably provide a rendered token.

### Fix

- Enabled `django.middleware.csrf.CsrfViewMiddleware` in the default settings
  and the ignored local `settings.py` copy.
- Added the CSRF context processor.
- Added `{% csrf_token %}` to the missing monitor unsubscribe form. The other
  POST forms in the root, crime, and monitor template trees already had tokens.
- Changed the crime, monitor, and main view render calls to pass
  `RequestContext` through the `context_instance` argument. This ensures
  context processors run and the token tag emits its hidden input.
- Added a test that checks both rendered token markup and rejection of a POST
  without a token.

The relevant templates are under [`templates/`](./templates),
[`crime/templates/`](./crime/templates), and
[`monitor/templates/`](./monitor/templates).

## 3. Environment-based Django secret

### Problem

The settings contained a hardcoded placeholder `SECRET_KEY`, which was shared
by every installation and did not provide a unique signing secret.

### Fix

- `settings_default.py` reads `SECRET_KEY` from the process environment and
  raises a clear `RuntimeError` if the value is absent or empty.
- `docker-compose.yml` passes the variable into the web container and refuses
  to start Compose without it.
- The ignored local `settings.py` was synchronized with the default settings.
  It is not tracked by Git.

### Configure before starting

Generate and export a private value locally; do not commit it:

```sh
export SECRET_KEY="$(openssl rand -hex 32)"
docker compose up --build
```

For an existing deployment, also ensure its local `settings.py` has the
environment-based setting. The container copies `settings_default.py` only
when `settings.py` does not already exist, so an older local copy will not
automatically be replaced.

## 4. Report edit-password hashing

### Problem

Crime report edit passwords were stored as plaintext in the database, and form
validation compared the submitted value directly with the stored value. The
model's 20-character limit was also too short for a secure encoded hash.

### Fix

- Added [`crime/passwords.py`](./crime/passwords.py), which creates salted
  PBKDF2-HMAC-SHA256 hashes with 600,000 iterations, a 16-byte random salt,
  and a 32-byte derived key.
- Report creation and updates now store a fresh salted hash. Report updates
  verify the submitted password against the stored hash before saving.
- Malformed hash values fail verification, and digest comparison is performed
  in constant time.
- Expanded `Crime.password` to 128 characters.
- Added South migration `0004` to widen the column, followed by data migration
  `0005` to hash existing plaintext database values. The data migration avoids
  re-hashing values already in the new format and updates only the password
  column. Its backwards migration deliberately fails: a one-way password hash
  cannot be converted back into plaintext.
- Replaced plaintext password values in the crime, main, and monitor test
  fixtures with hashes. The fixture password remains `123456` for tests.
- Added hash creation/verification tests and adjusted create/update tests to
  assert passwords are not stored in plaintext.

### Upgrade existing databases

Back up the database before applying schema or data migrations. With
`SECRET_KEY` configured and the application settings available, run:

```sh
python manage.py migrate crime
```

South applies the column-width migration and then hashes existing report
passwords. Afterward, existing users continue to use their original password
when editing a report; only its database representation changes.

## Verification performed

- Eight direct middleware cases covered missing, valid, chained, malformed,
  out-of-range, abbreviated, leading-zero, and non-ASCII address inputs.
- The legacy-container crime suite passed: 17 tests.
- The legacy-container crime and monitor suites passed: 27 tests.
- The South data migration was exercised against a plaintext password and the
  resulting hash successfully verified the original password.
- All POST forms were checked for CSRF template tags; all eight fixture
  passwords were checked as valid hashes.
- Docker Compose configuration resolved the `SECRET_KEY` environment value.
- A broader crime/main/monitor run had one unrelated existing failure:
  `main.tests.MainTestCase.test_get_sitemap` could not find `sitemap.xml`.
