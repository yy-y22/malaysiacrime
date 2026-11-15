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
  applications' tests on pushes and pull requests. CI generates a temporary
  `SECRET_KEY` for WP5's Docker configuration.

Maintenance types: **Corrective** (notification and sitemap fixes),
**Preventive** (regression tests, configuration isolation and CI).

## Run the complete suite without starting the web server

```sh
export SECRET_KEY="$(openssl rand -hex 32)"
docker compose build web
docker compose run --rm --no-deps -T web sh -ec '
  if [ ! -f settings.py ]; then
    cp settings_default.py settings.py
  fi
  python manage.py test crime main monitor feeds --settings=malaysiacrime.settings_default --noinput
'
```

Django creates a separate test database and captures test email in memory.
The test runner selects the tracked `settings_default` so an older local
`settings.py` cannot hide the newly registered `feeds` application. Keep
`settings.py` and `dev.db` out of commits.

## Validation

- Original baseline: 24 tests; 23 passed and the sitemap template was missing.
- Before the notification fix: the 10 new area tests had two failures,
  demonstrating both unwanted notifications and missed notifications.
- Before integrating newer work packages: **49 tests passed** (24 existing,
  10 area, 15 RSS).
- After merging `master` at `096d2ba`, **73 tests passed** with the Docker
  CI commands from a clean source copy.
- Template cleanup was also checked with a different test order; the original
  `TEMPLATE_DIRS` value was restored after the suite.

The workflow still needs its first run on GitHub after the branch is pushed.
Local verification of the Docker commands is separate from a hosted CI result.
