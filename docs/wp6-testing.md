# WP6: tests and corrective maintenance

## Changes

- Replace the arithmetic examples in `feeds/tests.py` with 15 RSS endpoint tests.
  They parse the generated XML and cover latest, updated and commented feeds:
  ordering, duplicate comments, removed reports, item limits, empty results,
  links, publication dates, author/category metadata, GeoRSS coordinates,
  XML escaping, formatted descriptions and unknown feed names.
- Register `feeds` in `settings_default.py` so the test runner discovers its
  tests. No feed-query implementation is changed; comment-query refactoring
  remains WP7's work.
- Fix the notification rectangle check in `send_all.py`. Latitude is compared
  with bottom/top and longitude with left/right. All four edges are included.
- Add 10 notification-area tests: inside, outside on each side, each boundary,
  and an area with negative longitudes. On the old implementation, the south
  exclusion test and negative-longitude inclusion test both failed.
- Remove import-time changes to `TEMPLATE_DIRS`. The crime and monitor view
  tests temporarily select their app-local templates and register cleanup to
  restore the previous setting, including when a test fails.
- Add the missing sitemap template and verify the rendered XML namespace and
  report links in the existing sitemap test.
- Add `.github/workflows/tests.yml` to build WP1's Docker image and run all four
  applications' tests on pushes and pull requests.

Maintenance types: **Corrective** (notification and sitemap fixes),
**Preventive** (regression tests, configuration isolation and CI).

## Run the complete suite

With the web container running:

```sh
docker compose exec web python manage.py test crime main monitor feeds --settings=malaysiacrime.settings_default --noinput
```

Use the tracked `settings_default` module explicitly. WP1 generates an ignored
`settings.py` only when it does not already exist, so an older local copy will
not automatically acquire the newly registered `feeds` application. Do not
commit `settings.py` or `dev.db`.

To run only the new tests:

```sh
docker compose exec web python manage.py test feeds --settings=malaysiacrime.settings_default --noinput
docker compose exec web python manage.py test monitor.AreaNotificationTestCase --settings=malaysiacrime.settings_default --noinput
```

## CI command (no running web server required)

```sh
docker compose build web
docker compose run --rm --no-deps -T web sh -ec '
  if [ ! -f settings.py ]; then
    cp settings_default.py settings.py
  fi
  python manage.py test crime main monitor feeds --settings=malaysiacrime.settings_default --noinput
'
```

Django creates a separate test database and captures test email in memory.
The command does not require initializing the development database or starting
the web server.

## Validation

- Original baseline: 24 tests; 23 passed and the sitemap template was missing.
- Before the notification fix: the 10 new area tests had two failures,
  demonstrating both unwanted notifications and missed notifications.
- After the changes: **49 tests passed** (24 existing, 10 area, 15 RSS).
- The Docker build and CI test command also passed from a clean source copy
  without local `settings.py` or `dev.db` (49 tests).
- Template cleanup was also checked with a different test order; the original
  `TEMPLATE_DIRS` value was restored after the suite.

The workflow still needs its first run on GitHub after the branch is pushed.
Local verification of the Docker commands is separate from a hosted CI result.
