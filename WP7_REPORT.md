# WP7 – Recent Commented fix, shared query, homepage pagination

Branch `wp7-maintenance`, created from `master` @ `3ded562ab20ce225d64698f3a5a0a183d98fb9f4`.
Status: **WP7 commit `25137486` integrated with master `f61dc244` (WP3, WP4, WP5) in a local merge commit; not pushed, no PR.** See section 12.

Evidence labels: **[src]** found by reading the source, **[run]** observed when executed, **[hyp]** hypothesis, not yet verified.

## 1. Environment (Stage 0)

| Item | Value | Evidence |
|---|---|---|
| Runtime | Docker container `malaysiacrime_legacy` (image `malaysiacrime-web`), Python 2.7.18, Django 1.3.1, South 0.7.3, Markdown 2.0.3, Django dev server (`runserver`) | [run] `pip freeze` |
| Host | Windows 11, Docker 29.9.3, Compose v5.7.0; benchmark client is host Python 3.13 | [run] |
| Database | SQLite `/malaysiacrime/dev.db`, sha256 `f008d67495f6d80a81698625b87b49b3a2d337d7d98817efd10615371e684831`: 1,000 crimes (all active), 0 comments. All 1,000 match the signature of `malaysiacrime_performance_kit/seed_local_crimes.py` (author `Benchmark`, location `Kuala Lumpur (synthetic)`) | [run] |
| Test DB | `:memory:`; South's `test` command runs migrations, so the `crime` tables exist | [run] probe and passing fixture tests |
| `Paginator` API | `count`, `num_pages`, `page`, `page_range`, `validate_number` (no `get_page`) | [run] `dir(Paginator)` |
| Assignment document | Tutorial 5 is not available locally; WP7 scope taken from the team brief | — |

### Findings that affect testing
- **Wrong template rendered in combined test runs.** [run] `crime/tests/__init__.py` and `monitor/tests.py` both set `settings.TEMPLATE_DIRS = ()` at import time. With `test crime main monitor`, `/` then renders the stub `main/templates/main/index.html` (670 bytes, no map) instead of `templates/main/index.html` (7,011 bytes). The existing `MainTestCase` therefore never checks the real pages. The WP7 tests restore the project template directory for themselves (`RealTemplatesTestCase`, using `addCleanup`); the global setup is left alone.
- **`feeds` is not in `INSTALLED_APPS`.** [run] `manage.py test feeds` fails with "App with label feeds could not be found". The feed tests therefore live in `main/tests.py` and request `/feeds/commented.xml`.
- **Fixture content type is wrong.** [run] `main/fixtures/comments.json` uses `content_type: 11`. In the test DB, 11 is South's `migrationhistory`; `Crime` is 12. The existing recent-commented test passes only because the code ignores content type. The fixture is left unchanged (see §3, technical debt).
- **Test baseline.** [run] `test crime main monitor`: 24 tests, 1 pre-existing error (`test_get_sitemap`, `TemplateDoesNotExist: sitemap.xml`). This is outside WP7's scope and not counted as a regression.

## 2. Original defects (root cause)

[src] Original `main/views.py`:
```python
ids = Comment.objects.all().values_list('object_pk', flat=True).order_by('-submit_date')[:500]
ids = reduce(lambda l, x: int(x) not in l and l.append(int(x)) or l, ids, [])
crime_dict = Crime.objects.in_bulk(ids[:200])
crimes = [crime_dict[id] for id in ids if not crime_dict[id].is_removed]
```
`in_bulk` loads only `ids[:200]`, but the loop walks **all** ids. The code crashes when:
1. there are more than 200 distinct commented crimes: [run] `KeyError: 1`;
2. any comment points at a crime that no longer exists, even with fewer than 200 (generic foreign keys do not cascade on delete): [run] `KeyError: 99999`;
3. any comment has a non-numeric `object_pk` (found in the final audit): [run] `ValueError: invalid literal for int() with base 10: 'invalid-id'`;
4. any comment has a numeric `object_pk` too large for a 64-bit database integer (found by the final Ponytail review): [run] `OverflowError: Python int too large to convert to SQLite INTEGER`.

`feeds/feeders.py` `CommentedEntries.items()` duplicates the same code with a window of 10 and a limit of 10. Case 1 cannot happen there (at most 10 distinct ids), but cases 2–4 can. [run] `KeyError: 99999`, `ValueError` and `OverflowError` through `/feeds/commented.xml`.

## 3. Decisions (approved after Stage 0)

| # | Decision |
|---|---|
| D1 | One shared function, `recently_commented(comment_window, limit)`, in `crime/models.py`. No new module. |
| D2 | Comment filtering stays as it was: no content-type, `is_public` or comment `is_removed` filter. |
| D3 | Homepage uses Django's `Paginator`, 20 per page, ordered by `('-created_at', '-id')`. The 500 cap is removed. Invalid page values (non-integer, 0, negative, past the last page) return **404**. An empty dataset still shows a valid page 1. |
| D4 | `crimes` in the homepage context is the current page, used by both the list and the map. The map JavaScript is unchanged. Awaiting WP3 confirmation. |
| D6 | Benchmark with the existing kit (5 warm-ups and 30 requests per endpoint) against the same container and the same `dev.db`. |

**What the helper returns.** Take the `comment_window` most recent comments (all of them, including any whose `object_pk` is unusable), turn their `object_pk` values into distinct crime ids in order of latest comment, drop ids that are non-numeric, outside the 64-bit range, missing or removed, then keep the **first `limit` valid crimes**. When the original code did not crash, the result is identical, because dropping crimes before or after the limit only makes a difference when there are more than `limit` distinct ids, which is exactly the case that crashed.

**Technical debt (D2).** Comments are not filtered by content type, so a comment on another model whose pk matches a crime id would list that crime. Today only `crime/show.html` hosts comments, and its comment form is disabled. Fixing this needs a content-type filter **and** a corrected `main/fixtures/comments.json` (it uses `content_type: 11`). Ordering is undefined when two comments share the same `submit_date`, as before.

## 4. Baseline performance (original, before any code change)

Commit `3ded562`, same container, same `dev.db` (sha256 above, unchanged after all measurements). Raw data: `wp7_evidence/benchmark_original_*` (see §9).

[run] HTTP, 5 warm-ups + 30 sequential requests per endpoint, all HTTP 200:

| Endpoint | median ms | mean ms | min ms | max ms | p95 ms | bytes |
|---|---|---|---|---|---|---|
| `/` | 2571.56 | 2591.33 | 2525.90 | 2776.44 | 2707.99 | 428,784 |
| `/?page=2` (ignored by original) | 2570.65 | 2581.04 | 2506.83 | 2717.59 | 2672.06 | 428,784 |
| `/?page=50` (ignored by original) | 2584.40 | 2610.19 | 2544.85 | 2927.83 | 2714.84 | 428,784 |
| `/recent/updated/` | 1056.02 | 1059.66 | 1032.27 | 1137.91 | 1088.83 | 173,559 |

[run] Queries per request (see §9 for the method):

| Endpoint | queries | `django_comments` queries | SQL time ms | total ms |
|---|---|---|---|---|
| `/` | 1002 | 1000 | 1234 | 2480 |
| `/recent/updated/` | 402 | 400 | 497 | 985 |

The 1,000 comment queries come from `{% get_comment_count %}`, which runs twice per crime (map and list) for 500 crimes. The comment-count hypothesis from Stage 0 is now measured. Earlier baselines (2,043 ms in the brief, 1,475 ms in the Tutorial 3 kit results) were taken in other environments and are not used for comparison.

## 5. Regression tests (Stage 2)

New tests in `main/tests.py`. They build their data in the isolated test DB and look up `Crime`'s content type with `ContentType.objects.get_for_model` (no hardcoded content-type ids).

- `RecentCommentedTestCase`: no comments; duplicates; exactly 200; 201; missing crime; removed crime; non-numeric and oversized `object_pk` (audit); limit counts valid crimes only; only the latest 500 comments are used.
- `CommentedFeedTestCase`: parses the actual RSS from `/feeds/commented.xml` (status, content type, `<item><link>` order). Cases: no comments; 10 of 11; missing, removed and non-numeric references.

[run] Before the fix, `python manage.py test main`: 15 tests, **5 errors**: the 4 expected `KeyError`s (`test_201_…` `KeyError: 1`; `test_comment_on_missing_crime_is_skipped`, `test_limit_counts_only_valid_crimes`, feed `test_skips_missing_and_removed_crimes` `KeyError: 99999`) plus the pre-existing sitemap error. All other new tests pass on the original code, so they guard existing behaviour.

## 6. Corrective and preventive fix (Stage 3, amended in the audit)

`crime/models.py`:
```python
def recently_commented(comment_window, limit):
    ids = []
    for pk in Comment.objects.order_by('-submit_date').values_list('object_pk', flat=True)[:comment_window]:
        try:
            pk = int(pk)
        except ValueError:
            continue
        # Ids outside the 64-bit database integer range cannot exist and make in_bulk overflow.
        if abs(pk) < 2 ** 63 and pk not in ids:
            ids.append(pk)
    crimes = Crime.objects.filter(is_removed=False).in_bulk(ids)
    return [crimes[pk] for pk in ids if pk in crimes][:limit]
```
- **Root-cause fix:** the lookup and the loop now use the same id list. Ids with no matching active crime are skipped instead of being indexed blindly, and non-numeric or oversized references are skipped instead of crashing.
- **Shared code:** `main.views.recent_commented` calls `recently_commented(500, 200)` and `feeds.feeders.CommentedEntries.items` calls `recently_commented(10, 10)`, so the two windows and limits are preserved. The obscure `reduce` lambda is replaced by an equivalent order-preserving loop.
- **Why `crime/models.py` and not a new module:** both callers already import `crime.models`, and `django.contrib.comments.models` does not import `crime`, so there is no cycle. A separate `queries.py` would add a module for one function.
- **Query count is unchanged:** 2 queries (comments, then crimes).

[run] After the Stage 3 change, `test crime main monitor`: 35 tests, 34 passed, 1 error (pre-existing sitemap). Live dev server: `/recent/commented/` 200 (4,672 B), `/feeds/commented.xml` 200 (527 B, valid RSS); sizes match the pre-change responses.

**Audit amendment: non-numeric `object_pk`.** [run] With one valid comment and one with `object_pk='invalid-id'` (isolated `:memory:` DB), both `/recent/commented/` and `/feeds/commented.xml` raised `ValueError`. The original `reduce` called `int()` in the same way, so the crash pre-dates WP7. It is the same class of defect as the missing-crime `KeyError` (an unusable comment reference takes down the whole page), so it is fixed in the same place with a `try/except ValueError: continue`. The final Ponytail review then found the same crash for a numeric but oversized reference (`'99999999999999999999'`): `int()` accepts it, but `in_bulk` raises `OverflowError` because database integers are 64-bit. Such an id cannot exist, so it is skipped with `abs(pk) < 2 ** 63`. The window and limit semantics are unchanged: a malformed comment still uses one slot of the comment window, exactly like a comment on a missing crime. `test_non_numeric_object_pk_is_skipped` failed with `ValueError` and then `OverflowError` before each fix, and passes after both; the extended feed test failed with `ValueError` before the fix and passes after it. [run] The `:memory:` probe now returns 200 on both endpoints for both kinds of reference.

## 7. Homepage pagination (Stage 4, amended in the audit)

`main/views.py` `index`:
```python
paginator = Paginator(Crime.objects.filter(is_removed=False).order_by('-created_at', '-id'), 20)
try:
    page = paginator.page(request.GET.get('page', 1))
except InvalidPage:
    raise Http404
...
'crimes': page.object_list, 'page': page, 'crime_total': paginator.count,
```
`templates/main/index.html`: a 5-line `<div class="pagination">` (« Newer · Page N of M · Older ») added below the list, inside the content block. The map script is unchanged.

- **The database does the paging.** [run] SQL for `/?page=50`: `... WHERE is_removed = False ORDER BY created_at DESC, id DESC LIMIT 20 OFFSET 980`, plus one `COUNT(*)`.
- **The `-id` tie-breaker is needed.** [run] Before the change, with tied `created_at` values, the test got ids in ascending order (`[1, 2, 3, …]`), so pages over tied rows were not stable.
- **The 500 cap is removed.** All 1,000 active reports are reachable over 50 pages.
- **404 cases:** `PageNotAnInteger` and `EmptyPage` are both `InvalidPage`. `allow_empty_first_page` (Django's default) makes an empty table a valid page 1.

**Audit amendment: homepage total.** [run] With 45 active reports and 1 removed, the original `crime_total` (`Crime.objects.count()`) showed **46** while only 45 can be browsed ("Showing 20 of 46", "Page 1 of 3"). The homepage now uses `paginator.count` (the same active-report count the pages are built from), which also removes one `COUNT` query. **Legacy behaviour change:** the number differs only when removed reports exist (`dev.db` has none, so the live page still says "of 1000"). It is justified because the old number contradicted the pagination: a user could never reach the extra reports it counted. `/recent/updated/` and `/recent/commented/` still use `Crime.objects.count()`; they are not paginated, and changing them is outside WP7.

New `IndexPaginationTestCase` (real template, checked by `id="map_index"`):

| Test | What it checks |
|---|---|
| `test_pages_are_ordered_and_sized` | Pages 1/2/3 have 20/20/5 reports, ordered with the tie-breaker, removed reports excluded; the number of map markers equals the page size |
| `test_navigation_links` | First page has only a next link; the middle page has both; the last page has only a previous link; "Page N of 3" |
| `test_invalid_pages_return_404` | `?page=` set to `4`, `0`, `-1`, `abc`, empty or `1.5` |
| `test_empty_dataset_has_valid_first_page` | 200, no reports, "Page 1 of 1", no links; `?page=2` gives 404 |
| `test_total_counts_only_browsable_reports` (audit) | 45 active + 1 removed shows "Showing 20 of 45"; it failed with `46 != 45` before the fix |

[run] Live server with the 1,000-report `dev.db`: `/`, `/?page=2` and `/?page=50` return 200 with "Showing 20 of 1000" and the correct links; `/?page=51`, `/?page=0` and `/?page=abc` return 404. A browser check of `/?page=2` shows "« Newer Page 2 of 50 Older »".
Cosmetic: the links use the site's existing dark link colour, which has low contrast on the dark background, the same as the existing headline links. CSS was not changed (out of scope).

**Map contract for WP3 (provisional, awaiting WP3 confirmation).** The homepage context has `crimes` (the current page's `Crime` objects, at most 20, newest first), `page` (a Django 1.3 `Page` object) and `crime_total` (the number of active reports). The list and the map both iterate `crimes`, so the map shows only the current page's markers instead of the newest 500. If WP3 needs every marker, that needs a separate data source (for example a JSON endpoint) and is WP3's decision.

**Not browser-validated.** WP3 integration is pending, and the map has not been checked in a browser: the legacy Google Maps v2 script no longer loads. What is verified is the server-side contract only: the test counts one `createMarker` call per report on the page (20/20/5).

## 8. Full regression run (Stages 5 and audit)

Final code, `docker compose exec web python manage.py test …`:

| Labels | Ran | Result |
|---|---|---|
| `crime main monitor` | 41 | 40 pass, 1 error: `test_get_sitemap` (pre-existing) |
| `monitor main crime` (reversed order) | 41 | same |
| `main` | 21 | 20 pass, 1 error: `test_get_sitemap` (pre-existing) |
| `crime` | 10 | OK |
| `monitor` | 10 | OK |

- Existing tests: 23 of 24 pass, the same as the baseline. New tests: 17, all pass. No new failures.
- [run] `RealTemplatesTestCase` restores `TEMPLATE_DIRS` through `addCleanup`. A probe with a subclass whose `setUp` raises confirmed the setting is back to `()` afterwards, so the swap cannot leak into other tests.
- Not run: `feeds/tests.py` (placeholder 1+1 tests), because `feeds` is not an installed app. The real feed behaviour is covered through the URL in `main/tests.py`.
- [run] `python -m py_compile` on all changed `.py` files under Python 2.7.18: OK. Django 1.3 APIs used (`Paginator.page`, `InvalidPage`, `Http404`, `QuerySet.in_bulk`) are exercised by the tests.

## 9. Performance (Stage 6, final code re-measured in the audit)

**Conditions:** same machine, same container, same `runserver`, same `dev.db` (sha256 unchanged before and after every run), same kit, 5 warm-ups + 30 sequential requests per endpoint, all 240 requests HTTP 200.
- Original: commit `3ded562ab20ce225d64698f3a5a0a183d98fb9f4`.
- Maintained: `3ded562` plus the final working-tree diff, `git diff | sha256sum` = `f7fb3e0e47532693fff48e3d7eee68d0a02c8a2f43c710f1b8c813d8e68e5979` (tracked files only; it will become the WP7 commit). Earlier maintained runs (diffs `b7b7a8f9…` and `33c8096b…`, before the audit amendments) are superseded and not reported.
- **Raw evidence in the repo:** `wp7_evidence/benchmark_{original,improved}_requests.csv` (every request: status, ms, bytes), `…_summary.json`, `…_summary.txt`, and `wp7_evidence/query_counts.txt`.

[run] HTTP response time (ms):

| Endpoint | Version | median | mean | min | max | p95 | bytes |
|---|---|---|---|---|---|---|---|
| `/` | original | 2571.56 | 2591.33 | 2525.90 | 2776.44 | 2707.99 | 428,784 |
| `/` | maintained | 157.93 | 163.05 | 145.10 | 205.48 | 199.03 | 21,882 |
| `/?page=2` | original | 2570.65 | 2581.04 | 2506.83 | 2717.59 | 2672.06 | 428,784 |
| `/?page=2` | maintained | 169.06 | 168.14 | 143.69 | 212.69 | 193.88 | 21,917 |
| `/?page=50` (last) | original | 2584.40 | 2610.19 | 2544.85 | 2927.83 | 2714.84 | 428,784 |
| `/?page=50` (last) | maintained | 155.37 | 154.83 | 134.43 | 196.45 | 183.52 | 21,884 |
| `/recent/updated/` (control, unchanged code) | original | 1056.02 | 1059.66 | 1032.27 | 1137.91 | 1088.83 | 173,559 |
| `/recent/updated/` (control, unchanged code) | maintained | 1083.25 | 1098.39 | 1045.09 | 1480.33 | 1172.99 | 173,559 |

**`/?page=2` and `/?page=50` were not distinct pages before pagination.** The original `index` view ignored the `page` query parameter, so its three homepage rows measure the same 500-report response (identical 428,784-byte bodies) three times. Only in the maintained version are they different pages (2 and the last page, 50).

[run] Queries per request:

| Endpoint | Version | queries | comment-count queries | SQL time ms | total ms |
|---|---|---|---|---|---|
| `/` | original | 1002 | 1000 | 1234 | 2480 |
| `/`, `/?page=2`, `/?page=50` | maintained | 42 | 40 | 54–56 | 112–117 |
| `/recent/updated/` | original / maintained | 402 / 402 | 400 / 400 | 497 / 494 | 985 / 999 |

**What this shows, and what it doesn't:**
- **Why the query count fell from 1,002 to 42:** pagination reduced the number of rendered reports from 500 to 20, and with it the number of per-report comment-count queries from 1,000 (2 × 500) to 40 (2 × 20). The remaining 2 queries are the active-report `COUNT` and the page `SELECT`. **The per-report N+1 query behaviour (one extra query per rendered report, here two: map and list) still exists**; only N is smaller. No query was optimised.
- The homepage median fell from about 2,572 ms to about 158 ms, and the response from 429 KB to 22 KB, for the same reason: the page does less work per request, not the same work faster.
- Time outside SQL (template rendering and Python) shrank by a similar factor (about 1,246 → 60 ms in the query script). Rendering and queries both shrink with page size; they were not measured separately in the HTTP benchmark.
- Deep pages cost the same as page 1 at this size (page 50 ≈ page 1). `OFFSET` cost grows with depth, but is not measurable at 1,000 rows.
- **Run-to-run noise:** the `/recent/updated/` control, whose code is unchanged, was 2.6% slower in the final maintained run (median 1,056 → 1,083 ms; one outlier at 1,480 ms). The superseded run measured +8.3% on the same control, so differences up to roughly 10% between runs are environmental noise. The homepage difference (about 16×) is far larger than that. Page 2's median (169 ms) is about 10% above page 1's (158 ms) for the same query count and size; this is within that noise.
- These are Django dev-server HTTP timings on one machine. They say nothing about production throughput or the browser/map.

### Reproducing the measurements
1. Benchmark client: the Tutorial 3 kit `malaysiacrime_performance_kit/benchmark_http.py` (Python 3, standard library only). It is not committed, as the kit instructs. The one change is the endpoint list:
   `ENDPOINTS = [('/', 'Homepage'), ('/?page=2', 'Homepage page 2'), ('/?page=50', 'Homepage page 50'), ('/recent/updated/', 'Recent Updated')]`
2. With the container running on the version under test (`git switch` changes the files and the dev server reloads):
   ```bash
   python benchmark_http.py --tag original --base http://127.0.0.1:8000 --requests 30 --warmups 5 --timeout 30
   python benchmark_http.py --tag improved --base http://127.0.0.1:8000 --requests 30 --warmups 5 --timeout 30
   ```
3. Query counts: a temporary, uncommitted script run inside the container (`python /tmp/qcount.py / "/?page=2" "/?page=50" /recent/updated/`). It only issues GET requests through `django.test.client.Client` against the configured `dev.db` with `DEBUG=True`. For each URL it makes one warm-up request, calls `reset_queries()`, makes one measured request, and prints `len(connection.queries)`, the number of queries mentioning `django_comments`, the sum of their `time` values and the wall time.
4. Verify the dataset afterwards with `sha256sum dev.db`; the expected hash is in §1.

## 10. Final review (Stage 7 and audit)

- **Ponytail reviews:** run after Stage 3, on the full diff in Stage 7, and again after the audit amendments. The audit review found one defect (oversized numeric `object_pk` → `OverflowError`), fixed test-first (§6).
- **`git diff --check`:** clean.
- **Line endings:** index LF, working tree CRLF (`core.autocrlf=true`), the same as the rest of the repo.
- **Scope of the diff:** only the five WP7 files are modified; `MainTestCase` and the fixtures are unchanged.
- **Checked:** every caller of the changed code; no import cycle from `crime.models` importing `comments`; identical results on non-crashing inputs; all invalid page inputs; that `{{ crimes.count }}` adds no query; the stub template still works.

## 11. Summary (Stage 8)

**Maintenance classification**
- Corrective: the `recent_commented` crash (more than 200 distinct crimes, missing crimes, non-numeric or oversized references) in the page and the feed; the homepage total counting reports that cannot be browsed.
- Preventive: the duplicated query is now one tested helper.
- Perfective: homepage pagination.

**Files changed:**

| File | Change |
|---|---|
| `crime/models.py` | +19 lines: `recently_commented()` |
| `main/views.py` | Pagination and active-report total in `index`; `recent_commented` uses the helper |
| `feeds/feeders.py` | `CommentedEntries.items` uses the helper |
| `templates/main/index.html` | +5 lines: page navigation |
| `main/tests.py` | +17 tests and their setup helpers |
| `WP7_REPORT.md` (new) | this report |
| `wp7_evidence/` (new) | raw benchmark results and query counts (7 small text files) |

**Remaining risks and limitations**
- Comments are not filtered by content type, and the fixture `content_type: 11` is wrong (§3, technical debt).
- Ordering is undefined when two comments have the same `submit_date`, as before.
- `/recent/updated/` and `/recent/commented/` still show `Crime.objects.count()` (including removed reports) as their total.
- `/recent/updated/` still renders 200 rows with 400 comment-count queries (not in WP7's scope).
- `crime/tests` and `monitor/tests` still clear `TEMPLATE_DIRS` globally. Only the WP7 tests work around it; the existing `MainTestCase` still checks the stub templates.
- `test_get_sitemap` still errors (`TemplateDoesNotExist: sitemap.xml`). The error is **pre-existing and unresolved**: it is in the 24-test baseline on `3ded562`, before any WP7 change. It is **not a WP7 regression** and is left for WP6.
- WP3 map integration is **pending**: the current-page map contract (§7) is unconfirmed by WP3 and has **not been validated in a browser**.

**Coordination notes**
- WP3: the map contract in §7 needs confirmation. Expect a merge conflict in `templates/main/index.html`; the WP7 change is a 5-line block inside `{% block content %}`.
- WP6: the sitemap error and the test-suite template issue (`TEMPLATE_DIRS`) are relevant to its work.

**Reproduce the tests**
```bash
git switch wp7-maintenance
docker compose exec web python manage.py test crime main monitor
```
Expected: `Ran 41 tests`, `FAILED (errors=1)`. The only error is the pre-existing, unresolved `test_get_sitemap` (not a WP7 regression).

## 12. Integration with master `f61dc244` (WP3, WP4, WP5)

**Starting point.** `wp7-maintenance` @ `25137486` (based on `3ded562`). `origin/master` @ `f61dc244d2fa92d6ed98f71bd320818e88a2371e` (merge of WP3 PR #5, WP5 PR #2, WP4 PR #4). Merge base: `3ded562`. Master changed 29 files; three of them are also changed by WP7: `crime/models.py`, `main/views.py`, `templates/main/index.html`.

### Environment protection
- **Backup first.** `dev.db` was copied to `SME/malaysiacrime-backups/dev.db.pre-wp7-integration` (sha256 identical to the original, `f008d674…4831`).
- **The developer container was not used.** `malaysiacrime_legacy` stayed stopped. Its start-up command runs `migrate`, which with WP5's code would irreversibly hash the passwords in `dev.db`.
- **Throwaway containers instead.** Every check ran in a throwaway container from the same image (`malaysiacrime-web`, Python 2.7.18, Django 1.3.1), with:
  - settings `integration_settings` = `from settings_default import *` plus `DATABASE_NAME = "/data/integration.db"`. This is WP5's real configuration: CSRF middleware and `SECRET_KEY` from the environment;
  - a throwaway random `SECRET_KEY` passed in through the environment, never printed or stored;
  - `django-admin.py` instead of `manage.py`, because `manage.py` imports the Git-ignored local `settings.py`, which has neither WP5 change.
- **Database copy.** The running instance used a copy of `dev.db` (mounted read-only, then copied inside the container). WP5's migrations were applied to that copy only.
- **Proof.** [run] `dev.db` sha256 was `f008d674…4831` before and after every step. The settings module, the database path, the CSRF middleware and the presence of `SECRET_KEY` were checked inside the container before running anything.

### Merge and conflicts
[run] `git merge --no-commit --no-ff origin/master`: **no textual conflicts**; Git merged all three overlapping files automatically. Each was checked by hand:
- `crime/models.py`: WP5 `password` `max_length=128` + WP7 `recently_commented()`, both present.
- `main/views.py`: WP5 `render_to_response(..., context_instance=context)` in all three views + WP7 pagination, 404 handling, `crime_total = paginator.count` and the `recently_commented(500, 200)` call, all present.
- `templates/main/index.html`: WP3 Leaflet script and `initialize();` call unchanged + WP7 `.pagination` block below the list. WP7 did not edit any map code.
- [run] `git diff origin/master` after the merge lists exactly the 13 WP7 files, so nothing from WP3, WP4 or WP5 was lost or overwritten.

**One semantic adjustment (test only).** [run] After the merge, `test_pages_are_ordered_and_sized` failed with `0 != 20`. It counted `batch.push(createMarker(`, the Google Maps v2 call that WP3 replaced with `markerLayer.addLayer(createMarker(`. The assertion still requires one map marker per report on the page; only the marker text was updated to WP3's Leaflet call. This is not a loosening of the test, and no application code changed during integration.

### Test evidence (integration settings, isolated `:memory:` test DB)

| Tree | Labels | Ran | Result |
|---|---|---|---|
| master `f61dc244` (baseline, separate worktree) | `crime main monitor` | 31 | 30 pass, 1 error: `test_get_sitemap` |
| merged | `crime main monitor` | 48 | 47 pass, 1 error: `test_get_sitemap` |
| merged | `monitor main crime` | 48 | same |
| merged | `main` | 21 | 20 pass, 1 error: `test_get_sitemap` |
| merged | `crime` | 17 | OK (includes WP5's CSRF, forwarded-IP and password tests) |
| merged | `monitor` | 10 | OK |

48 = master's 31 + WP7's 17. The only error is the same pre-existing, unresolved `test_get_sitemap` error that master also has. **No new failures.**

### Running-instance evidence (port 8001, migrated `dev.db` copy with seeded comments)

| Check | Result |
|---|---|
| WP5 migrations `0004`, `0005` on the 1,000-report copy | [run] applied in 98 s; 1000 of 1000 passwords hashed |
| `/`, `/?page=2`, `/?page=50` | [run] 200, "Showing 20 of 1000", "Page N of 50", 20 `markerLayer.addLayer` calls each |
| `/?page=51`, `/?page=0`, `/?page=abc` | [run] 404 |
| 201 distinct commented crimes + `invalid-id`, `99999999999999999999` and a missing id (seeded into the copy only) | [run] `/recent/commented/` 200 with 200 reports, PERFTEST-0201 … 0002 (the oldest-commented, 0001, correctly dropped) |
| `/feeds/commented.xml` with the same data | [run] 200, valid RSS, 7 items (PERFTEST-0201 … 0195). Expected: the 10-comment window contains the 3 bad references, which are skipped but still use a slot (§3) |
| WP5 CSRF | [run] `/crime/create/` contains `csrfmiddlewaretoken`; POST without a token returns 403 |
| WP3 Leaflet on `/?page=2` (browser) | [run] Leaflet 1.9.4 loads, OSM tiles render, no console errors, **20 markers**, and the marker popup headlines are exactly the 20 listed reports (PERFTEST-0980 … 0961) |

Browser limits: the synthetic reports all share one coordinate, so the 20 markers stack on one pin. Marker *placement* across different coordinates and popup clicking were not checked visually. Only Chromium (the desktop app's browser pane) was used.

### Compatibility
- **WP3 / WP4.** The homepage map works with pagination: it receives the current page's `crimes` (at most 20). The contract in §7 now holds with WP3's Leaflet code. Whether WP3 accepts "map shows the current page" (rather than all reports) is still their decision.
- **WP5.** Security behaviour is unchanged: CSRF enforced, password hashing and migrations work, `SECRET_KEY` comes from the environment. WP7 tests create `Crime` rows directly with a dummy password; they never exercise the password path.
- **Pre-existing cross-WP issue, not caused by WP7, for WP3.** `templates/main/recent_commented.html` and `recent_updated.html` still contain Google Maps v2 code (`GMap2`, `batch.push`). WP3 removed the Google Maps script from `base.html` (and the `onload="initialize()"`). [run] In the browser, `/recent/commented/` shows its 200-item list but an **empty map area**. No JavaScript error appears, because `initialize()` is never called. WP7 did not touch these templates, and master has the same state.
- **Developer environment warning.** The next `docker compose up` needs `SECRET_KEY` and, through the container command, will run WP5's irreversible password-hashing migration on `dev.db`. A pre-integration backup exists (above). The local `settings.py` is Git-ignored and is not updated by `cp -n`, so it still lacks WP5's CSRF and `SECRET_KEY` settings until a developer recreates it from `settings_default.py`.

### Benchmark after integration
The §4 and §9 measurements (`wp7_evidence/`) remain the evidence for the WP7 change itself: original `3ded562` versus `3ded562` + WP7, same environment and dataset. **They are not a benchmark of the integrated system.** After integration:
- the homepage includes WP3's Leaflet script, and its response size changed from 21,882 to 22,854 bytes ([run] port 8001, page 1);
- the server ran with WP5's CSRF middleware and a migrated database;
- the integrated system was not re-benchmarked.

Nothing here supports a claim about the combined system's response time. Template work and query count still scale with the 20 reports on a page, because WP3's template keeps one `{% get_comment_count %}` per report for the map and one for the list.
