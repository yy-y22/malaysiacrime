# Changelog

This is a record of merged group maintenance, reconstructed from GitHub PR metadata on 18 November 2026. Dates use Asia/Kuala_Lumpur (UTC+08:00), based on each PR's actual `merged_at` timestamp. Documentation proposed in WP8 is separate from these completed application changes.

## Unreleased — WP8 documentation and coordination

Proposed in [PR #9](https://github.com/yy-y22/malaysiacrime/pull/9); not merged.

- Add an evidence-backed contribution register and presenter handoff; prepare the Tutorial 5 table in the shared Google Doc.
- Reconcile stale test and CI instructions with WP6. No application or dependency versions change.
- WP8 remains partial while repository-owner Issues enablement, destination-report insertion and final presenter rehearsal are pending. See [the register](docs/WP8_CONTRIBUTIONS.md).

## Merged maintenance

| Local merge date | WP / PR | Type | Change |
| --- | --- | --- | --- |
| 2026-11-18 | WP4 [#8](https://github.com/yy-y22/malaysiacrime/pull/8) | Corrective | Fix five report/monitor maps after WP3 removed the body-level initializer; initialize each page on DOMContentLoaded and remove duplicate Leaflet loads. |
| 2026-11-16 | WP6 [#7](https://github.com/yy-y22/malaysiacrime/pull/7) | Corrective / Preventive | Replace dummy feeds tests; add notification-area regression tests and correct the rectangle check; isolate template settings; add sitemap template and Docker CI. |
| 2026-11-15 | WP2 [#3](https://github.com/yy-y22/malaysiacrime/pull/3) | Preventive | Add README setup instructions, contributor workflow, architecture explanation and diagrams. |
| 2026-11-15 | WP7 [#6](https://github.com/yy-y22/malaysiacrime/pull/6) | Corrective / Preventive / Perfective | Fix recently commented retrieval, share the page/feed helper, paginate the homepage and record benchmark evidence. |
| 2026-11-15 | WP3 [#5](https://github.com/yy-y22/malaysiacrime/pull/5) | Adaptive | Replace homepage Google Maps v2 with Leaflet/OpenStreetMap and load shared Leaflet assets. |
| 2026-11-15 | WP5 [#2](https://github.com/yy-y22/malaysiacrime/pull/2) | Corrective / Preventive | Restore CSRF checks, load SECRET_KEY from the environment, validate forwarded IPv4 values and hash edit passwords with South migrations. |
| 2026-11-15 | WP4 [#4](https://github.com/yy-y22/malaysiacrime/pull/4) | Adaptive / Corrective | Migrate report and monitor map pages and shared icons to Leaflet; preserve saved icons and remove eval on icon input. |
| 2026-11-13 | WP1 [#1](https://github.com/yy-y22/malaysiacrime/pull/1) | Corrective / Adaptive | Configure SQLite and MEDIA_URL defaults, remove deployment-only runtime dependencies and add Python 2.7 Docker setup. |

## Verification evidence

- Application snapshot [`3d58b30`](https://github.com/yy-y22/malaysiacrime/commit/3d58b3077520bdec4b0a13905119274adba012d1): [master CI run 44152682510](https://github.com/yy-y22/malaysiacrime/actions/runs/44152682510/job/134284977413), completed successfully; its test-step log records **73 tests, OK**. This is a hosted result on that exact SHA, not a claim about every contributor's environment.
- WP7's recorded performance experiment has [original](wp7_evidence/benchmark_original_summary.json) and [improved](wp7_evidence/benchmark_improved_summary.json) data. Results belong to that experiment; they are not newly measured timings for current master.
- Current local checks and browser observations are in [the presenter handoff](docs/SHOW_PROGRESS_2_HANDOFF.md).

## Remaining limitations

- Python 2.7 / Django 1.3.1 remain the runtime; Docker reproduces the old stack rather than modernizing it.
- Recently commented and recently updated templates still call Google Maps v2; the other map migrations do not cover those pages.
- New-comment UI remains disabled. Email subscriptions require separate email/error-path verification; no outgoing email is claimed as tested.
- Some older README / architecture claims were written before WP6. In particular, the missing sitemap template and arithmetic-only feeds test are historical defects fixed by PR #7.

## Historical baseline

The inherited [2011 snapshot `941fc5b`](https://github.com/yy-y22/malaysiacrime/commit/941fc5bb9ca708f6bf59b836fa88b2daa1fc64c0) underpins Tutorial 5's legacy-system analysis. Findings such as blank setup defaults, missing README, duplicate retrieval logic and disabled CSRF refer to that baseline; they must not be presented as unchanged current-master behavior.
