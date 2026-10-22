# Phase 5 implementation report

Baseline: `1d7bffdc6d0f121c5dab60d29332d3831d7f1169` (`phase 4 done`), branch `main`. No commits or pushes were made. Previously existing Phase 4 scratch directories were preserved. The active learner database was opened read-only for preservation fingerprints, never migrated or used for feature testing.

## Readiness

**Classification: Engineering complete, content review/publishing pending.** Further authoring is also required for 148 topics. **The 157-topic syllabus is not complete.** Nine topic pairs are validated candidates, 148 topics remain unauthored, and all candidates await independent human review/publication. No approval, learner achievement or publication is inferred from automated tests.

## Content and review

The authoritative scope remains unchanged. FINAL_CONTENT_COVERAGE.md and data/placement-foundations-coverage.json enumerate every topic, level, competencies, prerequisites, historical editorial references, candidate paths/depths, provenance, validation, human-review/publication status and errors.

The batch contains 18 validated files: nine lesson bundles and nine assessment bundles. Seven objective topics have two practice items, one proposed independent transfer, one recall and one interview item each (35 objective items). AI fundamentals and communication each have two unscored reflections (four additional pool items). Nine lesson reflections are separate from these pools. Actual newly published depths are zero for every purpose; actual approved/published Placement Foundations lessons are zero. Synthetic test overlays do not count.

Each subject has one candidate at its first Level 1 topic. Remaining unauthored topic counts: quantitative aptitude 17/18, logical reasoning 14/15, verbal English 16/17, Python 20/21, SQL/PostgreSQL 17/18, DSA 18/19, system design 14/15, AI fundamentals 18/19, communication 14/15. No Level 2/3 completeness is claimed.

Original prose/questions cite nine explicit registered primary reference URLs, without copying publisher prose, images or challenge statements. Usage is factual reference, not a redistribution-license claim. Numeric derivation trees use exact Fraction calculations; sequences have bounded enumeration; Python/SQL references and negative fixtures execute in local isolated workers. DSA transfer uses a different ring-distance context, pending human independence review. Choice IDs are neutral and positions vary. The schema rejects correctness-named choice IDs. Automated checks cannot certify educational adequacy or source support for every claim.

The 53 legacy lessons and historical problem records were not relabeled approved. The problem validator also includes the corrected Two Sum candidate: 111 files versus 110 historical bank entries. Existing adaptation/provenance blockers remain.

## Engineering

- Planner: default 300 net minutes; 300/360/480 presets; IANA timezone/local-day persistence; explicit revision regeneration; due recall, P0 minima, weakness/prerequisite ranking, subject rotation/caps; terminal task retention; skip/complete/replace; immutable referenced content snapshots; honest unallocated minutes. Manual navigation remains free. Completion never changes mastery.
- Timed tests: fixed versioned subject, level, mixed and coding templates; published static pools; full preflight before creating a session; exposure-family exclusion; frozen shared assessment selections; server deadlines; saved drafts and history; locked answers; deterministic scoring and fixed mixed-test negative marking; completion/timeout/abandon; immutable reports. Detailed feedback and help are embargoed until completion. Tests do not modify technical mastery, FSRS or global mistake ratings. Post-worker deadline expiry rolls back transient evaluation.
- UI: dashboard availability/mistakes/progress, planner controls, settings/timezone, topic review/test links, timed-test selectors/timer/history/reports, draft restoration and narrow safe native Markdown disclosures. Fonts and Monaco configuration resolve locally.
- Migration 6 adds four tables with ownership/immutability constraints. Frozen migrations 1–5 and schema snapshots remain unchanged. Disposable upgrade/fault/backup/restore tests exercise rollback and preservation.
- Windows launchers prebind loopback, use per-runtime mutexes and verify native process creation time, actual executable, exact command hash and runtime owner. Close holds the verified process handle; stale/corrupt/unverifiable state is quarantined. Verification never closes default `.runtime`.

## Verification results

Phase 4 baseline: backend **247 passed**, one upstream Starlette warning, 718.33 seconds. Frontend initially had two cold-start PGlite test timeouts under concurrent load; only those test deadlines increased from 5 to 20 seconds. Rerun **43 passed**; typecheck/build passed. Legacy lesson validators: Python 19, SQL 14, DSA 20. Problem validator: 111. SQL PGlite: 30 problems / 60 datasets. Baseline browser: five journeys passed; blocked Google Fonts exposed a remote dependency subsequently removed.

Final backend: **271 passed**, one upstream Starlette deprecation warning, **529.50 seconds**, exit 0. The first run had 270 passes and one stale test expectation (restore succeeded with schema 6; test expected 5); the corrected full rerun is clean. Frontend: **49 passed** across 12 files, 11.49 seconds; typecheck and production build passed. All 53 legacy lessons, 111 problem files, 18 candidate bundles and SQL 30-problem/60-dataset validation pass. The final launcher rerun passes **18 checks**. Browser: **17 passed**, 0 failed, **46.636 seconds** in installed Chromium; zero external requests and zero page errors. Two console HTTP 409 messages are the intentional empty-pool rejection scenarios, not asset/runtime failures. Local Pyodide WASM/stdlib, PGlite WASM/data and Monaco worker/font requests were observed. Mobile screenshots were visually inspected. Durable logs and JSON are in `verification/`.

Commands run from `apps/api` (all tests use disposable databases):

```powershell
$env:FORGE_DATABASE_URL='sqlite://'
.venv/Scripts/python.exe -m pytest -q --basetemp='C:\My PC\git\Forge\scratch\phase5-final-recheck'
.venv/Scripts/python.exe -m scripts.course_builder.validate --track python
.venv/Scripts/python.exe -m scripts.course_builder.validate --track sql-postgresql
.venv/Scripts/python.exe -m scripts.course_builder.validate --track dsa
.venv/Scripts/python.exe -m scripts.problem_builder.validate
.venv/Scripts/python.exe -m scripts.placement_batch validate
.venv/Scripts/python.exe -m scripts.placement_inventory
.venv/Scripts/python.exe -m scripts.placement_review
.venv/Scripts/python.exe -m scripts.content_checks.provenance --output ../../docs/forge-v1/verification/legacy-provenance.json
```

Candidate validation includes strict source/provenance policy, exact candidate hashes, assessment contracts, execution fixtures and derivation proofs. The separate legacy provenance inventory reports unresolved claims; it does not clear them. External source URLs were checked during authoring; offline verification does not refetch them.

From `apps/web`: `npm test -- --run`, `npm run typecheck`, `npm run build`, `npm run validate:sql-problems`. From repository root:

```powershell
apps/api/.venv/Scripts/python.exe scripts/verify_launcher.py --report docs/forge-v1/verification/launcher-report.json
apps/api/.venv/Scripts/python.exe scripts/verify_offline.py --playwright-module <installed-playwright-module-directory> --output docs/forge-v1/verification
git diff --check
rg 'import.*(google|gemini|providers)|from.*(google|gemini|providers)' apps/api/app apps/web/src -n
```

The runtime-import search returned no matches. Authoring helpers are development-only. Installed Chromium is real; no mocked editor/worker execution counts as a browser check. Fixtures explicitly label synthetic curriculum approvals, mock pool additions and a 73-hour past test clock beyond both FSRS due time and the minimum 24-hour recall gate. They exist only in newly created scratch databases.

Network verification denies external browser requests and external Python DNS/TCP/provider imports inside the verification process. It does not disable the machine network or provide an OS firewall around Node. Dependencies must be installed beforehand. See KNOWN_LIMITATIONS.md for precise scope.

No tests were skipped. Existing-database upgrade, injected rollback, backup and restore were verified with disposable database/CLI tests, rather than a nonexistent browser migration UI. No machine-wide internet-disconnection test was run; network denial has the scope described above. Vite reports large bundled-runtime chunks; these remain a packaging limitation.

## Preservation and corrections

Before/after preservation compares all 228 protected content/migration files and all 38 actual learner SQLite tables (row counts and full-row digests). Result: **all unchanged**, with zero mismatches; see verification/preservation.json. No real publication, approval, curriculum selection, chat, interview, Arena, review or mastery record was intentionally changed. Verification backups/restores were disposable only.

Corrections found during this work include answer-revealing candidate choice IDs, insufficient small-budget due-review reservation, completion-report variable shadowing, scored-context bypass guards, expired evaluation rollback, native launcher identity routing, Windows subprocess pipe inheritance, external fonts, nested Pyodide production asset output, missing explicit test-selector accessible names, early Monaco loader configuration and escaped worked-answer disclosures. Test-only browser selectors were adapted to modern Monaco EditContext; that was a harness issue.

## Exact remaining human actions

Read each of the nine packets under `data/content-approvals/phase5/review/` and both exact candidates/reports it names. Check facts, source relevance, pedagogy, legitimate alternative answers, coding contracts, progressive hints and transfer independence. Edit/revalidate failed material. Copy the all-false checklist for each candidate and mark only checks personally completed. Real named independent review is required separately for all 18 candidates.

From `apps/api`, the existing CLI requires:

```powershell
python -m scripts.content_checks.publish review --candidate <candidate.json> --validation <validation.json> --checklist <completed-checklist.json> --output <human-review.json> --reviewer <actual-name> --notes <actual-review-notes> --outcome approved --i-am-the-human-reviewer
python -m scripts.content_checks.publish package --candidate <candidate.json> --validation <validation.json> --review <human-review.json> --targets <exact-targets.json> --output <entry-package.json> --release-id <chosen-release-id>
python -m scripts.content_checks.publish publish --package <complete-overlay-package.json> --database <explicit-learner-db-path>
```

Before packaging, explicitly review/confirm the Placement Foundations graph in Forge and obtain its actual curriculum ID and graph digest. Curriculum confirmation does not approve content. Targets must match that exact graph and topic. Combine reviewed entries into a complete overlay, preserving prior accepted entries. Review the destination and backup policy before publication. No reviewer identity, target ID, approval or publication has been guessed here. Author the remaining 148 topics in reviewable batches using the same gates; outlines are not substitutes.
