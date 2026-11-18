# Show Progress 2: evidence handoff

Prepared by Osman for the assigned presenter on 18 November 2026. This is an evidence pack and rehearsal checklist; the assigned presenter retains ownership of the script.

## Snapshot and claims

- Application snapshot: [`3d58b3077520bdec4b0a13905119274adba012d1`](https://github.com/yy-y22/malaysiacrime/commit/3d58b3077520bdec4b0a13905119274adba012d1), including WPs 1–7 and Malak's post-merge map fix, PR #8.
- Baseline test evidence: [CI run 44152682510, test job](https://github.com/yy-y22/malaysiacrime/actions/runs/44152682510/job/134284977413), **73 tests, OK**. This verifies the automated suite on that SHA, not live map tiles or outgoing email.
- WP8 documentation is proposed in [PR #9](https://github.com/yy-y22/malaysiacrime/pull/9), not merged. Its first commit, `044a94f`, passed [hosted CI](https://github.com/yy-y22/malaysiacrime/actions/runs/44249174155); no extra application functionality is implied.
- Use the [contribution register](WP8_CONTRIBUTIONS.md) for member, PR, commit and merge-date evidence; use the [changelog](../CHANGELOG.md) for the maintenance sequence.
- Tutorial 5 compares the inherited **2011 snapshot `941fc5b`** with maintenance in **2026**. Missing README, blank setup defaults, the old area-check bug and disabled CSRF are baseline findings, not unchanged current-master defects.

## Rehearsal sequence for the presenter

Use a disposable local demonstration database. Record the Git SHA actually shown; if it differs from the snapshot above, repeat the relevant checks. Follow the [README](../README.md) for setup and tests. Never display the secret key.

| Step | Demonstration | Expected result | Evidence to retain | Current rehearsal status |
| --- | --- | --- | --- | --- |
| 1 | Show the original dependency pins, then the Docker setup and current run. | Explain reproduction of Python 2.7 / Django 1.3.1, without claiming a Python 3 upgrade. | PR #1; terminal startup screenshot with commit recorded. | Pending local runtime availability. |
| 2 | Open the homepage with sample reports; open a report and the create/edit pages. | Map tiles, report markers and the saved icon appear; map initialization works after PR #8. | PRs #5, #4, #8; screenshots of homepage and report map. | Browser check pending; a merged fix alone is not proof. |
| 3 | Show CSRF and password regression tests and security maintenance notes. | Explain request protection, environment secret and migrated edit-password hashes. | PR #2; passing test output; security notes. | Automated suite passed on baseline; live create/edit flow not rehearsed here. |
| 4 | Show RSS tests, notification boundary tests and current CI. | Explain the corrected southern boundary and test isolation. | PR #7; linked CI test log. | Baseline CI verified. |
| 5 | Show recently commented results and a populated second homepage page. | No old 200/500-ID crash; shared helper; at most 20 reports per homepage page. | PR #6; screenshot using enough disposable reports for page 2. | Baseline automated tests passed; browser check pending. |
| 6 | Show the contribution table and changelog, then acknowledge remaining work. | Every credited change has evidence; outstanding work is not presented as complete. | WP8 PR, shared Doc, owner/report/rehearsal checklist. | Documentation prepared; WP8 remains partial. |

## Performance figures

If using a speed comparison, cite WP7's actual [original summary](../wp7_evidence/benchmark_original_summary.json), [improved summary](../wp7_evidence/benchmark_improved_summary.json) and [method/report](../WP7_REPORT.md). Its homepage experiment records medians of **2,571.56 ms** and **157.93 ms**, with 30 measured requests per endpoint and 5 warmups. These are the recorded experiment's results, not fresh current-master measurements or browser rendering times. Do not mix them with the earlier 1,475 ms figure in the task allocation.

## Known limitations and fallback material

- The recently commented and recently updated map templates still call `GMap2`; do not claim all maps were migrated. Their list retrieval is separate from map rendering.
- New-comment input remains disabled. Sample comments have a content-type mismatch in a fresh database; do not promise visible report comments based only on the Commented list.
- Admin template lookup and subscription email/error handling still need browser verification. Do not demonstrate outgoing email without a configured, tested mail environment. WP6 fixed the missing sitemap template; do not repeat the old missing-template claim.
- Python 2.7 and Django 1.3.1 remain the stack. The current work reproduces and maintains the legacy application.
- No new application screenshots were captured in this WP8 session. The local Docker build stopped before application execution with `metadata_v2.db: input/output error`; the data volume was effectively full. Do not retry builds until storage is healthy.
- Fallback while a live application is unavailable: show the linked 73-test CI log, source diffs in PRs #1–#8, the existing [architecture diagram](images/architecture.png), the contribution register and WP7's recorded benchmark files. These are evidence artifacts, not replacement screenshots of a successful current rehearsal.

Before presenting, capture the homepage, report detail and passing test output from the chosen commit. Keep the original filenames, commit/date and result alongside those images; do not use an unrelated older screenshot as proof for this snapshot. If those captures cannot be made, present the limitations and the available source/CI evidence explicitly.

## Coordination still required

1. Repository owner Tan Yun Yu: **Settings → General → Features → Issues**. Confirm the setting is enabled before opening follow-up issues. Osman cannot change this with the current non-admin access.
2. After enablement, track the two remaining map pages (Adaptive), admin template lookup (Corrective), subscription error handling (Corrective) and fixture content-type mismatch (Corrective), checking for existing issues first. Treat disabled comments as a product decision requiring group agreement before enabling them.
3. Report editor: insert the prepared native table from the shared Doc's Final Answer tab into the destination project report and record its link/section. The destination report has not been supplied.
4. Assigned presenter: finish the script and record an actual rehearsal against the chosen SHA. This handoff has not been sent to anyone automatically.
5. Group reviewer and Tan Yun Yu: review and merge the WP8 PR under CONTRIBUTING. The shared document's stated deadline is **19 November 2026, 11:59 PM** (local time assumed).
