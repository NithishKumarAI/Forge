# Combined Phase 4 implementation report

Implementation date: 2026-10-21. This report covers the static assessment and learning infrastructure; it does not certify a fully authored syllabus or an installed offline release.

## Checkpoint status

- **A — Audit and baseline: Complete and verified.** Frozen baseline checkout, full baseline tests, route/provider/trust audit, and before/after preservation fingerprints.
- **B — Deterministic assessment: Complete and verified.** Choice, Decimal numeric, strict Python, isolated SQL and unscored reflection contracts have positive and negative execution tests.
- **C — Identity, help and answer safety: Complete and verified.** Frozen selection identity, exact SHA, idempotent submission, append-only help, reveal/exposure guards, hidden DTO fields and interview feedback embargo have backend tests and frontend rendering tests.
- **D — Static pools: Complete and verified for infrastructure; production content Blocked.** Reviewed release selection, exhaustion, exposure exclusion and legacy isolation are tested with synthetic approvals. No real approval was created.
- **E — Mastery and Arena: Complete and verified.** Versioned credit, actual worker verification, one global Arena credit, historical replay, caps, delayed recall, weak recall and rollback are tested.
- **F — Static guidance/manual curricula: Complete and verified.** Scoped corpus retrieval and legacy history safety are tested; existing manual draft/confirm/activate and immutable graph tests remain.
- **G — Interviews: Complete and verified for infrastructure; objective production pools Blocked.** Fixed objective weights/deadline, withheld feedback, save/resume, legacy reports and seven unscored reflection prompts are tested. The broader subject/mixed timed-test system is outside this phase.
- **H — Runtime LLM removal: Complete and verified.** Runtime AST/import/startup tests reject provider and optional SDK imports; external test connections are blocked.
- **I — UI integration: Partially complete verification.** Implemented pages, controlled input callbacks, HTTP adapters and feedback/report rendering pass tests and build. No interactive browser walkthrough was performed; complete worker/network-denial and installed offline verification remain Phase 5 work.
- **J — Tests and checks: Complete and verified for automated checks.** Exact command results are below. Backend, frontend, validators and preservation checks use disposable data. Browser release verification is explicitly outstanding.

## 1. Baseline and working tree

Started on clean `main` at `1cd5768` (`phase 3 done`). The authoritative baseline is a `git archive HEAD` checkout, with the installed web dependencies linked for local judge validation: **215 passed, one warning, 365.93 seconds**, exit 0. An earlier overlapping run on the live working tree returned 214 passed/one failed because it loaded the newly added migration while an old assertion still expected schema 4; that run is not presented as a pristine baseline.

Read the Phase 0–3 reports, architecture plan, curriculum scope, implementation roadmap, teaching checklist and agent guide. No commit, push, paid model call, learner-database migration or real content publication was performed.

Audit findings: practice/transfer/review, tutor/doubt and interview generation depended on the provider; settings exposed model/cost controls; Arena accepted client pass/score claims; developer validation routes exposed hidden contracts; old Arena events lacked reliable new-policy credit provenance. These paths are replaced or explicitly retired. Historical records are retained.

## 2. Exact files changed

The inventory at the end lists every added, modified and deleted source/document path. Removed runtime implementations and obsolete provider-generation tests are preserved as non-importable `.py.txt` archives, rather than silently changing the meaning of historical features. No dependency lockfile, published course JSON, scope definition, or migration 1–4 was changed.

## 3. Migration 5 and recovery

Additive migration 5 adds four association/audit tables over existing sessions, attempts, evidence and interviews: `AssessmentSelection`, `EvidenceCredit`, `EvidencePolicyRecord`, `AssessmentHelpEvent`. It does not create a second learner or assessment database. Selection freezes exact revision/SHA, item/family, contract, purpose, curriculum/topic and policy/judge versions. Only unscored communication rehearsal may have a null topic; it creates no artificial Python mapping or mastery attempt.

Unique constraints prevent duplicate credit, concurrent open topic contexts and repeated global Arena credit across curriculum switches. Ownership triggers validate curriculum/topic/session/content identity and attempt/evidence associations. Completed selections and credit/help/policy records cannot be rewritten/deleted through ordinary SQL updates. Static interview blueprint metadata is immutable.

The existing runner keeps checksum validation, backup-before-upgrade, atomic schema/ledger writes and restore compatibility. Tests exercise populated version-4 upgrade, deliberate version-5 DDL failure/rollback, unchanged old ledger definitions, backup restoration and repeat startup. Migrations 1–4 and their frozen schemas remain byte-identical. The real learner database was never opened for write; migration testing used isolated copies/fixtures only.

## 4. Assessment contracts and trust boundary

Single-choice uses one immutable answer ID; multi-select requires exact set equality. Duplicate/unknown keys and malformed contracts are rejected. Numeric input is a bounded finite Decimal string with authored units, inclusive tolerance and explicit no-rounding policy. Expressions are not evaluated.

Python contracts freeze function parameters or stdin/stdout mode, complete fixtures, typed expectations, exceptions, normalization, starter and reference. Recursive comparison distinguishes tuple/list, bool/int and integer/float. Public Run remains in the Pyodide browser worker; authoritative Submit executes source in an isolated child interpreter with an allowlisted language/library subset, clean environment/directory and time, instruction, output, memory and process limits. Unsupported code or unavailable verification yields no evidence. This is a restricted local verifier, not a secure remote-proctoring service.

SQL Run remains in a fresh browser PGlite worker. Submit uses a bounded Node child and a fresh PGlite database for every authored dataset, read-only query transaction and statement timeout. Comparison enforces exact column identities, duplicates, NULL, authored ordering, UTC date serialization and explicit numeric representation. Fixture/runtime failure is unverified; query failure is a failed contract. No learner input reaches Forge SQLite.

The backend receives source/answer and exact selection SHA, never a trusted browser score. Legacy Arena pass/score request fields are ignored. Missing worker dependencies fail closed. Runtime model grading has no fallback.

## 5. Practice, transfer and recall

Pools derive from effective independently reviewed releases and exact curriculum-topic bindings. `assessment_bundle` extends the existing publication registry, validator, review and release process. Coding references and negative implementations execute during validation. No parallel approval store exists.

Selection is deterministic and persisted before display; resume preserves the same UUID, content and contract. Practice prefers unused families; repetition does not farm credit. Transfer requires a reviewed independent variant and excludes exposed families, including historical Arena/course exposure and help. Coding subjects require coding variants. Recall uses FSRS due state, respects the 24-hour clean-transfer gate, and excludes recently revealed/helped variants for 24 hours. It is delayed recall, not a claim of unseen transfer.

Missing and exhausted pools return explicit errors without new attempts, fabricated results or generation. Legacy static course practice can remain available in historical curricula as `legacy_unverified`; generated old exercises are never silently added to approved pools. Model-era pending attempts remain readable and pending, with no fabricated evaluation.

## 6. Arena-to-mastery repair

Approved, mapped, unassisted first solves require a complete backend contract pass. They retain the Arena attempt, exact revision association, shared attempt/selection and `arena` evidence with source IDs and policy/judge versions. A unique global problem-family claim prevents repeating the same solve for credit after switching curricula. Generic practice sourced from an Arena item uses the same credit path.

Legacy/unapproved or unmapped problems can retain actually verified run history but grant no new approved mastery credit. Hinted/revealed/assisted solves do not earn independent Arena credit. Old Arena rows and ambiguous old evidence are neither rewritten nor inferred to be independently verified. Partial coding scores remain useful feedback but cannot satisfy passing evidence, transfer or recall gates.

## 7. Scoring policy and historical projection comparison

New policy: `forge-evidence/2`; worker contract: `forge-worker/1`; score-to-FSRS mapping: `forge-score-to-fsrs/1`; FSRS card envelope remains schema 1. The first qualifying new event saves an immutable envelope containing the previous `legacy/unversioned` projection and original evidence IDs.

Practice is capped at 79, clean transfer at 89, and successful unassisted recall at least 24 hours later permits 90+. Weak recall can lower mastery. Coding transfer needs actual independent coding evidence; MCQs alone cannot unlock it. Reflection, reading, chat and study minutes contribute no mastery. Interview scores never change technical mastery or claim a hiring probability.

Read-only replay fixtures demonstrate: an ambiguous historical Arena event has old/new practice score `null/null`, grants no new credit and leaves its bytes unchanged; a newly reviewed complete independent solve changes practice projection `null -> 100`, with mastery capped at 79. Repeating it, including under another active curriculum, leaves one event/credit. The complete synthetic practice/transfer/recall sequence reaches 79, 89 and 100; subsequent weak delayed recall lowers it. These are fixture results, not a recalculation of the user's learner history.

Attempt, provenance, credit, projection and FSRS update in one transaction. Injected projection failure rolls all of them back. Normal browsing/startup does not backfill or reset historical mastery.

## 8. Help/reveal and answer safety

Learner DTOs whitelist public fields and omit answer keys, reference implementations and hidden fixtures. Public Run uses public samples only. Submission/reference-validation developer endpoints return 410. Static frontend serving checks path containment to prevent traversal into backend files.

Hints, static help and permitted saved-answer reads mark open transfer/recall work assisted and append audit. Reveal ends clean eligibility and grants no score/evidence. Post-completion worked answers append help events rather than rewrite immutable completed selections. Prior exposure/reveal excludes transfer variants. Active scored interviews block tutor/help/search/lesson/hint/reveal/report shortcuts; objective item feedback stays hidden until the full interview completes.

## 9. Static guidance and manual curriculum workflow

The former tutor route now searches the local FTS lesson corpus with curriculum/revision boundaries, exact authored excerpts, section links, provenance and approved/legacy labels. It invents no explanation. Legacy chat history remains readable and labeled model-era guidance. Empty search results are explicit. Learn retains version selectors and revision-scoped section progress; reading still has no mastery effect.

Manual template/custom draft, edit, review, confirm and activate remain separate explicit operations. Confirmed curricula remain structurally immutable. No runtime generation or curriculum override remains. Advisory planner behavior and free manual access remain available.

## 10. Static objective interviews

The versioned objective blueprint fixes Python/SQL/DSA competencies and weights at 40/30/30, with a 1,800-second allowance. It requires approved interview-purpose items before creating a session. Selected IDs, families, revisions, hashes and full weights/blueprint are frozen in existing interview metadata and shared selections.

Save/resume does not restart the clock. After expiry, further answers are rejected; completion reports unanswered items as zero in the interview denominator without fabricating learner attempts/evidence. Answered scores and authored explanations are withheld until whole-session completion. Reports are deterministic and completion is idempotent. Technical interview results do not alter mastery. Saved-session assistance is explicitly recorded.

## 11. Reflection-only rehearsal and old interviews

Seven static prompts cover introduction, HR, STAR, project explanation, design, RAG and tradeoffs. Learners save written responses and review authored rubrics/examples; no model or automatic free-text correctness score exists. Responses have `score: null` in learner/report DTOs, no scored denominator and no technical mastery evidence. Legacy mandatory numeric storage placeholders are explicitly marked reflection metadata and never treated as a learner score; unbound communication rehearsal creates no ordinary Attempt.

Historical interview questions, rubrics, responses and saved reports remain available verbatim, including unknown historical report fields/modes. Model-era sessions are read-only; no invented continuation, rescoring or regenerated feedback is offered.

## 12. Runtime LLM removal

Removed runtime provider package/imports, AI/tutor/doubt generation routers/services, generated curriculum/practice/transfer/review/interview calls, usage/cost controls, model selectors, runtime key configuration and `google-genai` requirement. No actual secret file was printed or edited. Normal learning and startup import no provider.

Optional authoring helpers and their explicit `google-genai==2.25.0` development requirement live under `scripts/authoring`, outside `app`. Existing development authoring may be invoked deliberately, never as runtime fallback. Retired implementation/tests are non-importable archives. Structural/runtime startup tests deliberately reject Google/provider/authoring imports; test sockets reject external destinations. No live provider call was executed.

## 13. Historical preservation evidence

Read-only snapshots before and after compare **226 protected files** and full rows/counts of **38 pre-existing SQLite tables**, including FTS shadow tables: **zero changed files, zero changed tables**. The [preservation evidence](PHASE4_PRESERVATION_EVIDENCE.json) records counts and aggregate fingerprints. File set includes all historical `content/**/*.json`, migrations 1–4 and prior frozen schema JSON. Database comparisons use a read-only URI, query-only transaction and sorted row representations, not approximate aggregate scores.

- Aggregate protected-file fingerprint: `87643eca0d0782c9b17279d4661c23010cc6fc6d69625fcc24f59ae8ac9dead6`.
- Aggregate database-table fingerprint: `dc1502de1a748dbc797d766af4887b0f7c8dd82e2534d38963367e53044ead2b`.
- Preserved examples: 2 curricula, 257 topics/states, 679 exercises, 6 attempts/details/evidence events, 8 chat messages, 6 usage events, 5 Arena attempts, 23 legacy lesson progress rows and all existing interview tables.

No real database reset, mastery recalculation, curriculum activation, publication/revocation or source fetch occurred. Historical lessons/Arena content, scope and Two Sum candidate approval status are unchanged.

## 14. Verification results

Final command results are recorded below after completion. All application commands use their own working directory and configured virtual environment. Tests use synthetic approvals only in isolated databases/snapshot directories, never real review records.

Intermediate failures were resolved rather than hidden: migration-version assertions, obsolete generated-workflow assertions, expired SQLModel test fingerprints, wrong fixture function identities/parameters, and the runtime import test's in-memory SQLite threading setup. The penultimate complete run returned 244 passed/two failed (443.42 seconds): the obsolete Arena signature and a stale-submission rejection that left a reused HTTP test session's transaction open. Correcting the fixture and explicitly rolling back rejected assessment requests passed the three-test retry/history regression (3 passed, one warning, 3.66 seconds). A superseded rerun was stopped so the final full run would load that correction. Windows sandbox SSR-cache and temporary-directory errors were retried outside the sandbox. The full suite includes real bounded Python/PGlite contract execution; no provider call is used as a correctness oracle.

Additional implementation-stage runs: contract/pool/migration/edition checks 66 passed/one failed (38.00 seconds; old schema-version assertion); broad changed-backend checks 230 passed/five failed (412.23 seconds; old fixture/workflow expectations and expired ORM fingerprints); corrected targeted checks 10 passed (25.04 seconds); checkpoint checks 51 passed/one failed (37.51 seconds; subprocess in-memory database threading); later contract/replay checks 35 passed (32.84 seconds), including explicit SQL date/numeric and infrastructure-failure behavior. The final full run below is the completion criterion, rather than any of these intermediate counts.

Frontend build warnings remain: Pyodide Node-module browser externalization, PGlite direct `eval`, and large Monaco/editor chunks. They do not fail compilation and are relevant to final offline asset/packaging verification. Backend retains the third-party Starlette/httpx warning where emitted. No browser/network-denial or Windows launcher certification is claimed.

## 15. Missing approved content/pools

All nine Placement Foundations subjects still require independently reviewed educational coverage and purpose-specific scored pools. The 157-topic outline does not mean those topics are taught. No production assessment bundle, transfer/recall/interview bank or synthetic approval was published. Existing legacy material remains labeled accordingly; corrected Two Sum 1.0.1 remains awaiting independent review/publication.

The safe technical publication/selection path exists and is fixture-tested. Real human editorial approval is an external blocker; missing content stays visibly unavailable rather than generated or silently promoted.

## 16. Incomplete, blocked and out-of-scope work

Production approved-content coverage and objective interview availability are blocked by real review/publishing work. Interactive browser QA, complete offline asset verification, network-denial runs and installed Windows packaging remain unverified. The restricted Python verifier intentionally rejects unsupported capabilities; SQL Submit requires installed Node/PGlite. There is no claim of secure remote assessment.

No full syllabus authoring, new planner, subject/mixed timed-test system, Forge V2 levels 4–5, final launcher verifier, commit or push was implemented. Existing pending model evaluations cannot be continued honestly offline and remain historical read-only records.

## 17. Prerequisites for combined Phase 5

Independently author/review/publish actual lesson and purpose-specific item coverage for all nine subjects, with complete executable references/negatives and original provenance. Verify editorial variant/family classification and pool depth. Build the requested planner and separate timed-test features without weakening free topic access or mastery rules. Complete interactive regression testing, first-install migration/backup/restore verification, full offline asset/network-denial testing and Windows release/launcher checks. Preserve these historical fingerprints and keep content approval separate from code passing.

## Final verification summary

- Frozen baseline, API working directory: `.venv/Scripts/python.exe -m pytest -q` against archived HEAD — **215 passed, one warning, 365.93 seconds**, exit 0.
- Final API working directory: `.venv/Scripts/python.exe -m pytest -q --basetemp=<workspace scratch>/phase4-complete-tests`, with `FORGE_DATABASE_URL=sqlite:///:memory:` — **247 passed, one warning, 421.98 seconds**, exit 0. File-database migration/restore/import tests explicitly use their own disposable files. Warning: Starlette's deprecated `anyio.abc.BlockingPortal` alias.
- API: `python -m scripts.course_builder.validate --track python` — **19 valid lessons**, exit 0.
- API: `python -m scripts.course_builder.validate --track sql-postgresql` — **14 valid lessons**, exit 0.
- API: `python -m scripts.course_builder.validate --track dsa` — **20 valid lessons**, exit 0.
- API: `python -m scripts.problem_builder.validate` — **111 valid problem revisions**, exit 0, including real Python verification and exact PGlite bundle checks.
- Web: `npm test` — **43 passed in 10 files, 12.72 seconds**, exit 0. Includes controlled choice/numeric callbacks, public Run/Submit distinction, interview feedback safety, legacy/reflection reports, HTTP pool/revision/exhaustion behavior, and static practice/transfer/recall/help entry states.
- Web: `npm run typecheck` — exit 0.
- Web: `npm run build` — exit 0, with dependency/bundle warnings described above.
- Web: `npm run validate:sql-problems` — **30 passed, zero failed, 60 datasets**, exit 0.
- Repository: `git diff --check` — exit 0; new-file whitespace/UTF-8 checks also clean. Git emits existing Windows LF/CRLF normalization notices.
- Preservation: **226/226 protected file fingerprints and 38/38 full table fingerprints unchanged**. The original learner database was not migrated or opened for write.

Temporary archived checkout and disposable test directories were removed after verification; its dependency junction was explicitly unlinked before checkout removal. No live provider call, content approval/publication, commit or push occurred. Interactive browser QA and installed offline-release verification were not performed.

## Exact change inventory

`A` = added, `M` = modified, `D` = removed from its original path (retired code is archived below).

- `A` `docs/forge-v1/PHASE4_PRESERVATION_EVIDENCE.json`

- `M` `ARCHITECTURE.md`
- `M` `README.md`
- `M` `apps/api/.env.example`
- `M` `apps/api/app/config.py`
- `M` `apps/api/app/main.py`
- `A` `apps/api/app/migrations/assessment_schema.json`
- `M` `apps/api/app/migrations/runner.py`
- `A` `apps/api/app/migrations/v005_assessment.py`
- `M` `apps/api/app/models/__init__.py`
- `M` `apps/api/app/models/entities.py`
- `D` `apps/api/app/providers/__init__.py`
- `D` `apps/api/app/providers/base.py`
- `D` `apps/api/app/providers/dependencies.py`
- `D` `apps/api/app/providers/gemini.py`
- `M` `apps/api/app/routers/adaptive.py`
- `D` `apps/api/app/routers/ai.py`
- `M` `apps/api/app/routers/api.py`
- `M` `apps/api/app/routers/arena.py`
- `A` `apps/api/app/routers/assessment.py`
- `M` `apps/api/app/routers/course.py`
- `M` `apps/api/app/routers/curricula.py`
- `D` `apps/api/app/routers/doubt.py`
- `A` `apps/api/app/routers/guidance.py`
- `M` `apps/api/app/routers/interviews.py`
- `M` `apps/api/app/routers/practice.py`
- `D` `apps/api/app/routers/tutor.py`
- `M` `apps/api/app/schemas/ai.py`
- `M` `apps/api/app/schemas/arena.py`
- `A` `apps/api/app/schemas/assessment.py`
- `M` `apps/api/app/schemas/editions.py`
- `D` `apps/api/app/schemas/interview.py`
- `M` `apps/api/app/schemas/publication.py`
- `M` `apps/api/app/services/arena.py`
- `A` `apps/api/app/services/assessment.py`
- `A` `apps/api/app/services/assessment_judge.py`
- `A` `apps/api/app/services/assessment_pool.py`
- `M` `apps/api/app/services/content_policy.py`
- `M` `apps/api/app/services/content_publication.py`
- `M` `apps/api/app/services/content_registry.py`
- `D` `apps/api/app/services/curriculum_generation.py`
- `D` `apps/api/app/services/doubt.py`
- `M` `apps/api/app/services/editions.py`
- `M` `apps/api/app/services/interview.py`
- `M` `apps/api/app/services/mastery.py`
- `M` `apps/api/app/services/practice.py`
- `M` `apps/api/app/services/review.py`
- `A` `apps/api/app/services/scoring_policy.py`
- `M` `apps/api/app/services/transfer.py`
- `D` `apps/api/app/services/tutor.py`
- `D` `apps/api/app/services/usage.py`
- `A` `apps/api/app/workers/python_worker.py`
- `A` `apps/api/app/workers/sql_worker.mjs`
- `M` `apps/api/requirements.txt`
- `A` `apps/api/scripts/authoring/config.py`
- `A` `apps/api/scripts/authoring/providers/__init__.py`
- `A` `apps/api/scripts/authoring/providers/base.py`
- `A` `apps/api/scripts/authoring/providers/dependencies.py`
- `A` `apps/api/scripts/authoring/providers/gemini.py`
- `A` `apps/api/scripts/authoring/requirements.txt`
- `M` `apps/api/scripts/content_checks/bundle.py`
- `M` `apps/api/scripts/course_builder/build.py`
- `M` `apps/api/scripts/gemini_smoke.py`
- `A` `apps/api/scripts/legacy_runtime/routers/ai.py.txt`
- `A` `apps/api/scripts/legacy_runtime/routers/doubt.py.txt`
- `A` `apps/api/scripts/legacy_runtime/routers/interviews.py.txt`
- `A` `apps/api/scripts/legacy_runtime/routers/practice.py.txt`
- `A` `apps/api/scripts/legacy_runtime/routers/tutor.py.txt`
- `A` `apps/api/scripts/legacy_runtime/schemas/ai.py.txt`
- `A` `apps/api/scripts/legacy_runtime/schemas/interview.py.txt`
- `A` `apps/api/scripts/legacy_runtime/services/curriculum_generation.py.txt`
- `A` `apps/api/scripts/legacy_runtime/services/doubt.py.txt`
- `A` `apps/api/scripts/legacy_runtime/services/interview.py.txt`
- `A` `apps/api/scripts/legacy_runtime/services/practice.py.txt`
- `A` `apps/api/scripts/legacy_runtime/services/transfer.py.txt`
- `A` `apps/api/scripts/legacy_runtime/services/tutor.py.txt`
- `A` `apps/api/scripts/legacy_runtime/services/usage.py.txt`
- `A` `apps/api/scripts/legacy_runtime/tests/adaptive_retired.py.txt`
- `A` `apps/api/scripts/legacy_runtime/tests/fakes.py.txt`
- `A` `apps/api/scripts/legacy_runtime/tests/test_interviews.py.txt`
- `A` `apps/api/scripts/legacy_runtime/tests/test_phase2_ai.py.txt`
- `A` `apps/api/scripts/legacy_runtime/tests/test_practice.py.txt`
- `M` `apps/api/scripts/problem_builder/build.py`
- `A` `apps/api/tests/assessment_fixtures.py`
- `M` `apps/api/tests/conftest.py`
- `M` `apps/api/tests/fakes.py`
- `M` `apps/api/tests/test_adaptive.py`
- `M` `apps/api/tests/test_arena_curriculum_v2.py`
- `A` `apps/api/tests/test_assessment_contracts.py`
- `A` `apps/api/tests/test_assessment_migrations.py`
- `A` `apps/api/tests/test_assessment_pools.py`
- `M` `apps/api/tests/test_content_bindings.py`
- `M` `apps/api/tests/test_content_publication.py`
- `M` `apps/api/tests/test_course.py`
- `M` `apps/api/tests/test_data_preservation.py`
- `M` `apps/api/tests/test_database_migrations.py`
- `M` `apps/api/tests/test_editions.py`
- `A` `apps/api/tests/test_evidence_replay.py`
- `M` `apps/api/tests/test_gemini_provider.py`
- `M` `apps/api/tests/test_interviews.py`
- `A` `apps/api/tests/test_no_runtime_llm.py`
- `M` `apps/api/tests/test_phase2_ai.py`
- `M` `apps/api/tests/test_practice.py`
- `A` `apps/api/tests/test_static_guidance.py`
- `A` `apps/api/tests/test_static_interviews.py`
- `M` `apps/web/src/App.tsx`
- `A` `apps/web/src/components/AssessmentCard.test.tsx`
- `A` `apps/web/src/components/AssessmentCard.tsx`
- `A` `apps/web/src/components/AssessmentInputs.tsx`
- `M` `apps/web/src/components/CodeEditor.tsx`
- `D` `apps/web/src/components/DoubtChat.tsx`
- `A` `apps/web/src/components/InterviewReportBody.tsx`
- `M` `apps/web/src/components/Layout.tsx`
- `M` `apps/web/src/components/SubjectLevelNavigation.tsx`
- `M` `apps/web/src/pages/ArenaPage.tsx`
- `M` `apps/web/src/pages/CurriculumBuilderPage.tsx`
- `M` `apps/web/src/pages/InterviewPage.tsx`
- `M` `apps/web/src/pages/LearnPage.tsx`
- `A` `apps/web/src/pages/OfflineFlows.test.tsx`
- `M` `apps/web/src/pages/PracticePage.tsx`
- `M` `apps/web/src/pages/ReviewPage.tsx`
- `M` `apps/web/src/pages/SettingsPage.tsx`
- `M` `apps/web/src/pages/TopicPage.tsx`
- `M` `apps/web/src/pages/TransferPage.tsx`
- `M` `apps/web/src/pages/TutorPage.tsx`
- `M` `apps/web/src/services/api.ts`
- `A` `apps/web/src/services/offline.test.ts`
- `A` `apps/web/src/services/offline.ts`
- `M` `apps/web/src/types/api.ts`
- `M` `apps/web/src/types/arena.ts`
- `A` `apps/web/src/types/assessment.ts`
- `M` `apps/web/src/types/editions.ts`
- `A` `data/assessment-pools/README.md`
- `A` `data/interview-blueprints/objective-v1.json`
- `A` `data/interview-blueprints/reflection-v1.json`
- `A` `docs/forge-v1/PHASE4_IMPLEMENTATION_REPORT.md`
