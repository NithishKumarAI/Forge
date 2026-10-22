# Independent readiness audit

Audit date: 22 October 2026. Scope: the authoritative local working tree, actual teaching files, independently executed tests and disposable learner journeys.

## Decision

**A. NOT READY — major engineering or educational blockers.**

**No:** a beginner should not currently use Forge as their sole platform to learn Python, SQL, DSA, AI/GenAI, aptitude, reasoning, English and system design, or to prepare reliably for fresher AI-engineer interviews. Useful local software and legacy material exist, but no subject has a completed approved Placement Foundations course. The public commit is also missing essential backend/release files. This decision is not a hiring-probability judgment.

The local engine now passes its repaired regression tests. That does not repair the educational gaps or make the GitHub checkout a complete release. There are0 published Placement Foundations lessons,9 validated candidate pairs and148 unauthored topics. All nine actual-course subject journeys are **BLOCKED BY CONTENT**, not passed. Synthetic approvals used to test mechanics are excluded from those counts.

## Repository reconciliation

- Exact HEAD/local main/origin-main/GitHub-verified commit:`6ca192105bc58d20fe729d070dd7fe1942ff4fd1`, “phase5 done”. One Git worktree at the requested project location.
- The commit changes24 frontend files. Planner backend, timed router/service/schema, migration6, safe launchers and Phase5 reports remain locally modified or untracked. They were not missing from the disk and were not overwritten.
- The file-by-file report is PHASE5_SYNCHRONIZATION_REPORT.md; audit-evidence/synchronization.json records statuses/digests and sharing exclusions. The clean HEAD archive lacks `/api/timed-tests/start` and `/api/planner/regenerate`. An explicit engineering-only overlay successfully starts, serves dashboard/planner/settings/blueprints, rejects missing pools, enforces strict types and rejects an untrusted browser origin.
- No reset, checkout replacement, staging, commit or push occurred. No recommendation includes new unreviewed teaching content, secrets, learner databases, .runtime, snapshots/backups or scratch. Candidate-generating scripts embed prose and candidate-dependent tests need local inputs; they are excluded from the engineering-only synchronization. The exact tested overlay paths are in engineering-overlay.json.
- Ignored names were inventoried without opening .env or learner records for disclosure. Dependency folders, caches, source cache, runtime and learner data are intentionally excluded. Two old inaccessible pytest directories were not opened or modified. Previous Phase4 scratch work was preserved.

## Independent test results

These were new executions for this audit, not copied Phase5 results.

- Initial existing backend suite:271 passed,1 upstream Starlette warning,498.46s.
- New negative cases reproduced three security/deadline failures; a separate strict-schema probe reproduced three coercion failures. Their red logs are retained.
- After repairs:278 passed,1 upstream Starlette deprecation warning,603.54s,exit0. No pytest skips. An intermediate run exposed duplicate retired-route operation IDs; explicit IDs plus a uniqueness assertion removed that additional warning.
- Frontend:49 passed across12 files,12.91s. Typecheck and production build passed. No frontend rewrite was needed.
- Existing lesson validators:Python19,SQL14,DSA20 pass their structural/syntax checks. Full problem validator:111 files including corrected Two Sum. SQL bank:30 problems/60 fresh datasets pass.
- All24 current portable candidates independently revalidated:18 prior Phase5 files,5 new audit corrections and existing Two Sum1.0.1. Passing is not human approval. Contextual-example declarations are explicitly distinguished from executed checks.
- Dependency checks:existing pip check and npm ls pass. A new disposable Python environment installed the requirements successfully and passed20 security/schema/migration/rollback/restore tests. A new lockfile Node installation added220 packages with lifecycle scripts disabled and built the copied actual frontend successfully in5.18s. Existing app dependencies were not replaced.

Commands, logs and machine results are under audit-evidence. Representative exact commands:

```powershell
# apps/api; each test run uses a new disposable basetemp
$env:FORGE_DATABASE_URL='sqlite://'
.venv/Scripts/python.exe -m pytest -q --basetemp='C:\My PC\git\Forge\scratch\independent-audit\pytest-release'
.venv/Scripts/python.exe -m scripts.course_builder.validate --track python
.venv/Scripts/python.exe -m scripts.course_builder.validate --track sql-postgresql
.venv/Scripts/python.exe -m scripts.course_builder.validate --track dsa
.venv/Scripts/python.exe -m scripts.problem_builder.validate
.venv/Scripts/python.exe -m scripts.content_checks.provenance --output ../../docs/forge-v1/audit-evidence/legacy-provenance.json
# apps/web
npm test -- --run
npm run typecheck
npm run build
npm run validate:sql-problems
npm ls --depth=0
```

Repository-root commands include `scripts/audit_content.py`, `audit_coverage.py`, `audit_contract_probes.py`, `audit_sql_facts.cjs`, `audit_sync_smoke.py`, `verify_launcher.py`, `verify_independent.py` and `verify_timed_expiry.py`. Browser tools use the installed Playwright module via `--playwright-module` and write only new synthetic databases under scratch. The reproducible command inventory is in audit-evidence/README.md.

## Database and historical-content preservation

The closing read-only database transaction matched the initial counts and complete sorted-row fingerprints for all **38 existing tables**; there were no changed tables or new tables. SHA256 checks matched all **229 protected files**, including historical teaching JSON, frozen migrations and schemas. HEAD is unchanged. No raw learner rows were exported. The check found zero true human attestations in the local approval archive. Five new correction-candidate digests match their validation reports and review packets, and their review checklist remains entirely false. Exact evidence is in audit-evidence/preservation.json and summary.json.

All disposable audit scratch is retained locally and excluded from synchronization, including fresh dependency installations and synthetic databases. The two pre-existing Phase4 scratch directories were preserved. Audit harnesses closed their own isolated servers through their explicit runtime directories; no generic process termination or normal Forge shutdown was used. No reset, clean, learner migration, commit or push was performed on the user's checkout.

## Browser, offline and Windows release evidence

- 17 existing real Chromium journeys passed independently on fresh/content synthetic servers: curriculum draft/review/confirmation/activation, lesson progress, local search, grading, Python/SQL Run and Submit, Arena hint/failure/pass/reveal, transfer/recall, planner presets/regeneration, timed coding/subject/mixed tests, draft refresh, objective interviews, unscored rehearsal, legacy reports and mobile navigation.
- Additional actual browser checks passed for an unversioned synthetic database upgrade, all nine real-content journeys correctly displaying missing lessons, and computed visible keyboard focus on mobile.
- A real15-minute timed test was started, answered once, given an unsubmitted draft, restarted, reopened in Chromium and later allowed to cross its actual server deadline. Browser completion produced33.33%,two unanswered questions and timeout reporting; the draft did not count as an answer. Its deadline/draft survived process restart. No test clock or deadline mutation was used for this case.
- The legacy upgrade reached schema6, retained a synthetic sentinel, created a verified schema0 backup and restored that backup/sentinel into another disposable database. Injected upgrade-failure rollback and historical preservation also passed backend tests.
- Windows launcher:18 checks passed after inspection established isolation and held-handle identity verification. Tested creation-time/PID, executable, exact command, owner and runtime tampering; collision fallback; duplicate launch; restart; missing build; failed startup; idempotent close; unrelated sentinel survival. Normal Forge runtime/data were not accessed by that harness.
- Dedicated browser ports were24000–24049. All audit servers used explicit scratch runtime/database/snapshot/backup paths. No other live project was targeted.
- External browser requests were denied and none were attempted in the exercised journeys. Pyodide WASM/stdlib, PGlite assets and Monaco resolved locally. The Python verification process denied external networking/provider imports. Supported runtime source has no provider imports; a redacted frontend secret-pattern scan found no matches.
- This is not machine-wide network disconnection, an OS firewall around Node, remote proctoring, a hostile-code sandbox certification, or a comprehensive dependency-advisory/CVE audit. Dependency installation/reference research used the network separately. Offline operation requires installed dependencies and built assets.

## Actual educational evidence

The complete census covers53 legacy lessons,371 unique authored exercises,258 example blocks and110 historical problem files. Database exercise copies/bindings are not counted as additional authored questions.

- 189 Python blocks were attempted in actual Pyodide workers: 166 matched displayed stdout; 23 independently failed because of missing helper/import context, unavailable host packages or incorrect/nonportable expectations. This does not mean 23 algorithms are wrong.
- 69 SQL blocks were attempted in fresh PGlite databases: 37 executed, 32 required undeclared tables/setup. Among the 37, 26 matched exact tables, 3 Indexes examples have material query/result defects, 1 promises a fixed timestamp for CURRENT_TIMESTAMP, 5 need Date/TZ/NULL display-context review, and 2 have descriptive outputs needing semantic review.
- 26 template MCQs, 52 generic reference answers and 13 underspecified repair prompts were found with exact file/key evidence. 38 problems have placeholder input constraints. 83 of 110 have only one hidden test/dataset beyond public/base examples; that is a coverage risk, not by itself proof of a wrong solution.
- 80 eligible Python/DSA problems rejected a constant-first-answer mutant. Four in-place tasks nevertheless accept newly allocated return values without the required input mutation. Two Sum rejects tuple results despite its tuple statement. Output correctness does not certify mutation, space or asymptotic complexity.
- Specific factual errors include Exception/KeyboardInterrupt hierarchy, stripped type annotations, custom-object truthiness, foreign-key targets, GROUP BY functional dependencies, missing JOIN conditions, zero-row scalar subqueries, CTE inlining, index catalog names/visibility/write claims, identity sequence guarantees and CPython list growth. Seven isolated PostgreSQL counterexamples and Python facts corroborate relevant cases; primary references and exact sections are in EDUCATIONAL_CONTENT_DEFECTS.md.
- Sources/originality labels were not promoted to independent review or license clearance. Existing adaptation/provenance blockers remain. No allegation of copying is made without a verified source comparison.

## Subject and syllabus readiness

LEARNING_COVERAGE_GAPS.md and audit-evidence/learning-coverage.json enumerate all157 IDs with outline/candidate/automatic-validation/human-review/publication/practice/transfer/recall/mock states, exact prerequisites, competencies and a prerequisite-ordered author/review queue.

- Python:21 topics,1 candidate pair,0 published.19 useful but unreviewed legacy lessons with identified defects. Not a complete reliable beginner-to-intermediate track.
- SQL/PostgreSQL:18 topics,1 candidate pair,0 published.14 legacy lessons, with setup gaps and factual/query defects. Not a certified complete track.
- DSA:19 topics,1 candidate pair,0 published.20 legacy lessons and original/historical bank records do not establish reviewed new-scope coverage; type/mutation/precondition problems remain.
- Quantitative aptitude18,reasoning15,English17,system design15,AI/GenAI19,communication15:each has only1 candidate pair and0 published lessons. No complete legacy taught course exists for these six subjects. RAG/agents/project/backend-production objectives are mostly outlines.
- The seven objective candidate topics have2 practice/1 transfer/1 recall/1 interview item each. A subject test needs3 unused interview-purpose items, so the first batch is too shallow even after hypothetical approval. The two reflection topics have no scored transfer/recall denominator. Generic rehearsal is not a taught interview curriculum.

## Repairs made and remaining limitations

Repaired with regression evidence:

1. Cross-origin state mutation/help side effects:browser-boundary middleware rejects untrusted origins/cross-site API requests, including GET routes that can create a plan.
2. DNS-rebinding Host acceptance:trusted local hosts enforced.
3. Objective interview grading beyond deadline:post-evaluation check rolls back transient attempts/responses and completes timeout consistently; historical accepted results remain intact.
4. Coerced timed level/position values:strict JSON integers now reject booleans, strings and floats.
5. Duplicate retired-practice operation IDs:explicit per-method IDs and schema-uniqueness regression assertion.

The in-place/complexity content contract problem is still unresolved; a reviewed new contract must observe the property or explicitly limit its claim. Old snapshots and scores were not silently rewritten. Other limits include revoked references in saved advisory plans requiring regeneration/replacement, no dedicated plan-history browser, supported-subset Python verification, trusted local administrator/clock boundaries, and unpinned Python transitive dependencies. A clean install/build passed on this Windows machine; a new physical OS installation and other platforms were not certified.

## Correction candidates and human dependencies

Five new unapproved1.2.0 drafts are in `data/content-approvals/independent-audit/` with exact review packets, sources, worked answers, reports and all-false checklists. Functions replaces generic exercises and executes six standalone examples. SQL Indexes corrects seed data/catalog/plan claims with four exact fixtures and one contextual EXPLAIN example. Exceptions, Type Hints and Control Flow are focused factual patches; their inherited examples still need review/setup work. These five do not add approved Placement Foundations coverage.

Human work remains substantive:finish missing teaching and pools, repair remaining facts/contracts, review genuine transfer independence and alternative valid answers, resolve source rights, and validate a real beginner learning pilot. Use the existing `content_checks.publish review` command only with an actual independent human identity/attestation and personally completed checklist. Confirm the actual target graph, then package and publish exact reviewed bytes through the existing workflow. No target IDs, human approvals or releases were invented here.

RELEASE_BLOCKERS.md is the concrete priority checklist. The engine tests establish mechanics; they do not establish that a beginner can learn the whole syllabus or become interview-ready using Forge alone.
