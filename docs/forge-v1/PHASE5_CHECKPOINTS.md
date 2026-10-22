# Phase 5 durable checkpoint log

Baseline: `main`, `1d7bffd` (`phase 4 done`), 22 October 2026. Existing untracked `scratch/phase4-browser-20261021-232948/` and `scratch/phase4-check-20261021-231846/` belong to prior work and must be preserved. No commit/push, actual learner DB write, or real approval/publication is authorized by this log.

## A — Phase 4 verification (complete automated baseline; browser smoke complete)

- Read the user request and project documentation; actual code remains authoritative.
- Before-change read-only fingerprints recorded in `scratch/phase5-verification/before.json`: 228 historical content/migration files, 38 actual SQLite tables. Do not use the learner DB as a mutable test fixture.
- Full backend baseline: 247 passed, one Starlette warning, 718.33 seconds. Frontend corrected run: 43 passed, 15.22 seconds. Typecheck/build and 53 legacy lesson / 111 problem / 30 SQL (60 dataset) validators pass. Logs in `scratch/phase5-verification/`.
- Initial frontend: 41 passed, two 5-second PGlite cold-start timeouts under concurrent backend work; typecheck/build pass. Investigate and bound integration-test timing without weakening correctness assertions.
- Installed Playwright/Chromium confirmed via bundled workspace runtime. Real isolated browser smoke passes fresh startup/dashboard, scope navigation, local search, seven communication responses/report and 390px layout; no page errors. External requests were denied. Found Google Fonts requests; removed CSS remote import and selected system fonts. Final browser rerun after production rebuild remains required.

## Next work, in requested checkpoint order

B–D: all-157 coverage inventory; original review-ready small content batch; exact existing candidate validation/provenance/coverage pipeline; no fabricated human review or publishing. Record remaining syllabus gaps precisely.

E: additive migration 6 only as needed; local-time, budget-correct diverse planner with safe regeneration/replacement and preserved legacy plan history.

F: persisted fixed-blueprint timed subject/level/mixed tests reusing frozen AssessmentSelection/scoring and shared help/feedback guards; no test-to-mastery shortcut.

G: extend existing dashboard/settings/subject flows; readable, accessible controls and honest missing content.

H: process-identity/creation-time/ownership validation and isolated launcher harness; never stop normal Forge or other projects.

I: isolated real Chromium/worker/browser checks with external networking denied; explicit evidence/limits.

J: final full verification, preservation comparison, required four deliverables and honest readiness classification. No top-level new phase, commit or push.

## B–D — controlled content batch and inventory

18 exact candidates (9 lessons + 9 pools) validated with bounded Python/PGlite positives/negatives and exact rational/sequence proofs. Nine review packets/checklists remain unapproved. All-157 JSON/Markdown inventory generated; 148 topics un-authored; no content published. Synthetic-only end-to-end publication test: 5 passed, one warning, 30.90 seconds. No human attestation is invented. Helpers: scripts.placement_batch / placement_inventory / placement_review.

## E — planner (in progress)

Migration 6 adds StudyPlanRevision/Entry and TimedTestSession/Item; migrations 1–5 frozen. New plan policy uses actual approved pools/lessons, selected IANA timezone, net budgets, P0 minima, due review, subject caps/rotation, idempotent day persistence, terminal-task retention and manual replacement. tzdata==2026.5 installed/pinned for Windows ZoneInfo. First planner run: 7 passed/one failed (30-minute review reserve clipped below a full recall slot); corrected reserve minimum 10 minutes. Rerun required. Old schema-version tests updated only to include 6; new v5→6 fault/backup/restore test still needed.

F is next: use shared AssessmentSelection with purpose timed, exclude mastery, fixed static blueprints, persisted drafts/deadlines, post-worker deadline recheck with rollback, withheld feedback/global help guards, immutable report; generic assessment Submit must not bypass timed API.

Outstanding: planner rerun; timed backend/UI; dashboard/settings; launcher hardened ownership/creation-time/executable/command + isolated harness; full browser/worker/network denial; final full checks and preservation; four final reports. Do not finish merely at this checkpoint log.

## E verified and F/G implementation checkpoint

- Planner/migration/adaptive rerun: 28 passed, one warning, 30.49 seconds. Default target 300, presets 300/360/480; no phantom legacy tasks. Sources/rows remain untouched.
- Timed schema/engine: 10 passed, one warning, 34.08 seconds. Fixed subject/level/mixed/coding templates; binary full-contract scores; optional authored negative marking; no mastery/FSRS; persisted drafts/deadlines; post-verification expiry rolls back transient attempt; shared help guards and direct timed-submit bypass protection. Fixed completion report variable shadowing; corrected test-only JSON datetime encoding/Path argument.
- UI integrated: StudyPlanPanel, settings presets/timezone, timed pages/history/reports, saved drafts, global nav, dashboard availability/mistakes, topic review/test links. npm test 43 passed, typecheck and build pass (ui-tests.log). New feature-specific frontend tests still needed.
- Migration 6 also enforces immutable plan metadata, timed blueprints/reports, owned entries and locked submitted drafts. Migrations 1–5 remain unedited.

## H in progress

New scripts/forge_server.py writes actual child process PID, native creation FILETIME, actual executable, exact command hash, UUID owner and runtime/repo identity; binds a socket before API startup. launcher-common.ps1 checks these with CIM and a held OS process handle. open/close scripts use per-runtime mutexes, isolated explicit data overrides, unique logs, verified identity health, quarantine stale state and never kill an unverifiable PID. Existing .bat wrappers retain correct working directories. Isolated smoke run starting; safe scripts/verify_launcher.py rewrite and harness execution still required. Do not run old verifier against default .runtime.

Outstanding: launcher harness, real full Chromium/worker/offline test fixture/harness, feature frontend/HTTP tests, complete final full suite/validators/preservation, README/ARCHITECTURE + required 4 final deliverables. Existing old Phase 4 scratch dirs must remain untouched. Baseline browser server (scratch/phase5-verification/browser-server.json) is task-owned and should be stopped by verified command identity at cleanup, never normal Forge.

## H verified

Isolated launcher harness: 18 checks passed (launcher-report.json). Covers all six identity-field tamperings, unrelated sentinel survival, creation time/PID reuse resistance, held-handle close/idempotency, stale/corrupt state, duplicate launch, preferred-port collision, restart plan persistence, missing build and failed startup cleanup. Fixed identity route ordering before SPA fallback. Initial harness anonymous-pipe inheritance caused a Windows subprocess wait; corrected capture to temporary files and reran successfully. Only explicitly isolated runtime paths were used.

Content recheck: neutral choice IDs / varied positions now enforced (correctness-named keys rejected), exact reports/inventory/review packets regenerated. 6 content tests pass, 32.22 seconds; still zero human reviews/publications. Numeric/sequence and actual Python/SQL execution remain. G current frontend tests43/typecheck/build pass; add specific planner/timed/draft tests next.

## I next

Installed Playwright is C:/Users/nithi/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright; installed Chromium works. Isolated baseline browser showed 5 journeys passing with blocked Google Fonts calls. CSS now system fonts, and Monaco loader config moved before child mount to prevent first-render CDN requests (needs real browser verification). Build new isolated browser fixture DB with 18 exact candidate bundles + clearly synthetic extra mock/coding variants, real shared engine past-time DSA practice/transfer as a recall fixture (no mutation of historical evidence). All review records must be TEST ONLY and only in scratch DB. Use launcher runtime/data overrides and external-request denial in Chromium; optionally Python socket guard per test process. Verify all supported journeys, mobile/keyboard, assets/console/API and persistence. Do not touch user .runtime or real learner DB.

Remaining: feature tests + browser fixture/harness; final complete backend/frontend/content/source/runtime checks; preservation against scratch/phase5-verification/before.json (228 protected files/38 tables); required reports README/ARCHITECTURE, exact 157 gaps and readiness classification; clean only task-owned scratch except prior Phase4 dirs. Current old baseline browser server is task-owned: browser-server.json contains its PID/port, but it was launched before new launcher protocol so cleanup requires exact CIM command proof, not default close script.

## I / J verification progress

Frontend feature tests added: 49 tests pass, typecheck/build pass. Final legacy validators pass (19 Python + 14 SQL + 20 DSA lessons, 111 problem files, 30 SQL problems / 60 datasets); all 18 candidates revalidated, exact inventory/review packets refreshed. No real review/publication.

First full final backend run: 270 passed / one failed / one upstream warning in 528.37 seconds. Failure was the old fresh-restore CLI test asserting five migrations after a successful six-migration restore; corrected expected count to six. Entire suite rerunning in phase5-final-recheck; do not call it passed until its exit/result is read.

Real Chromium offline harness implemented in scripts/verify_offline.py + verify-browser.cjs, fixtures in prepare_browser_fixture.py. It refuses existing/outside-scratch DBs, uses isolated owned launcher runtimes and denies external browser requests plus Python network/provider imports. Modern Monaco EditContext required a harness locator update. Browser found a production defect: vite-plugin-static-copy retained node_modules/pyodide path segments, so local Pyodide core URLs failed. Added explicit rename.stripBase=true and rebuilt; actual browser Python public Run, Python/SQL Submit and transfer89 now pass. First recall fixture was only 25h old while FSRS due interval was two days; recreated synthetic past sequence at 73h, without rewriting events or changing production FSRS/gates. Full browser rerun in progress.

Preservation PASS: all 228 protected file hashes and all 38 actual learner-table full-row digests/counts unchanged. Durable docs/forge-v1/verification/preservation.json. Network guard selfcheck passes external DNS/TCP/provider import denial (verification process only, not OS firewall).

Required report/checklist/limitations and README/ARCHITECTURE drafts now exist. Outstanding: finish browser harness (including interview/report/planner/mobile), clean backend full rerun, copy final logs/results into durable verification, reconcile report placeholders/checklist/readiness and safely stop/remove only owned Phase5 scratch. Preserve both old Phase4 scratch directories. No commit/push.

## Final checkpoint — execution finished

- Final full backend rerun: **271 passed**, one upstream Starlette warning, 529.50 seconds, exit 0. The stale migration-count assertion is fixed. No skipped tests.
- Final frontend: **49 passed**, 12 files, 11.49 seconds; typecheck/build pass. All legacy lesson/problem/SQL and 18 candidate validators pass. Final launcher rerun: **18 checks pass**.
- Final real Chromium: **17 journeys pass**, 46.636 seconds; zero external requests and page errors. Two expected console 409s come from intentional unavailable-pool checks. Python public Run/backend Submit, SQL public Run/backend Submit, transfer/recall, Arena hint/failure/pass/reveal, coding/subject/mixed timed tests, saved draft/deadline, objective/reflective interviews, historical reports, plan presets/completion/regeneration, mobile width and keyboard focus verified. Local Monaco/Pyodide/PGlite assets observed; mobile screenshots visually inspected. Explicit timed-select accessible names added after browser checks. Final report assertion waits for navigation rather than matching repeated pre-navigation labels.
- Source candidates and exact report/inventory/review packets remain unpublished and unapproved: nine topic pairs, 148 unauthored topics. Classification **Engineering complete, content review/publishing pending**, with additional content authoring explicitly required.
- Required four reports completed, README/ARCHITECTURE updated. Durable evidence is now `docs/forge-v1/verification/`, including summary.json, full final logs, browser/launcher reports, screenshots, provenance, before fingerprints and preservation results. Earlier scratch references above are historical; those Phase5 scratch directories have been removed.
- All task-owned servers stopped through exact command/runtime ownership checks. Only task-created phase5-* scratch directories removed after copying evidence. Both pre-existing Phase4 scratch directories preserved; normal .runtime untouched. Final post-cleanup read-only comparison again confirms all 228 protected files, exact set of 38 learner tables, row counts and complete-row hashes unchanged. No real learner DB migration/write, human approval, publication, commit or push.
- Execution is complete. Remaining human work is content authoring, independent review and exact confirmed-graph publication, as detailed in PHASE5_IMPLEMENTATION_REPORT.md. No further top-level phase prompt is needed.
