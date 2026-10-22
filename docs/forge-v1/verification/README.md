# Verification evidence

`summary.json` records the final counts. `final-backend-recheck.log` is the clean full 271-test run; `final-backend.log` retains the earlier stale migration-count failure for transparency. The corrected full frontend run, build/typecheck, lesson/problem/candidate/SQL validators and final launcher logs are included.

`browser-report.json` describes 17 real installed-Chromium journeys against disposable synthetic fixtures with external browser requests denied. Its two HTTP 409 console messages are deliberate missing-pool checks. There were no external requests or page errors. Screenshots contain synthetic data only. `network-guard.json` records process-scoped Python DNS/TCP/provider denial; this is not a machine-wide firewall or Node network sandbox.

`before.json` stores protected-file hashes and learner-table hashes/counts from the consistent read-only baseline transaction. `preservation.json` records unchanged contents; the exact table set and all hashes were rechecked after cleanup. No raw learner rows or database copy is included here. `legacy-provenance.json` preserves unresolved historical attribution/publication blockers rather than certifying them.

The repeatable harnesses are `scripts/verify_launcher.py`, `scripts/verify_offline.py`, `scripts/verify-browser.cjs` and `scripts/prepare_browser_fixture.py`. Use the commands in the implementation report. Browser verification needs an installed Playwright module and its Chromium installation; pass its absolute module directory with `--playwright-module`. Dependencies/build must already exist. Harnesses use only new explicit scratch databases/runtime directories and never the normal learner DB or .runtime. Reproduction scratch fixtures are retained for inspection; remove only verified task-owned scratch paths after stopping their owned runtimes.

Publication during tests is explicitly synthetic, isolated and excluded from the shipping coverage counts. There are zero actual new human reviews/releases. The whole 157-topic syllabus is not complete.
