# Forge V1 implementation roadmap

Status: proposed on 21 October 2026 from the actual local working tree. **Phase 0 implements none of the phases below.** Preserve the pre-existing uncommitted application/content/launcher work. No rewrite, commit, push, live model call or learner-data reset is required by this plan.

Read [PHASE0_AUDIT.md](PHASE0_AUDIT.md) for defects and test evidence, [ARCHITECTURE_PLAN.md](ARCHITECTURE_PLAN.md) for contracts and data preservation, and [CURRICULUM_SCOPE.md](CURRICULUM_SCOPE.md) for the nine-subject Levels 1–3 scope.

## Shared completion rule

For every implementation slice: run the relevant deterministic backend tests, frontend tests if affected, `npm run typecheck`, and `npm run build`. Run all changed-content validators, including real PGlite validation when SQL changes. Use fake/forbidden providers in automated tests; do not use the ordinary learner DB as a mutable fixture. Execute the full backend suite at milestone boundaries, accounting for the Windows sandbox socket limitation recorded in the audit. Record exact results and unexecuted checks.

The file lists below identify existing files actually found in this checkout; new names are proposed. Directory-wide references identify content families, not permission to mass-edit them. Keep each slice reviewable; if its acceptance criteria cannot be validated independently, split it further.

## Phase 1 — Preserve data and make content identity explicit

**Objective:** establish safe additive upgrades and correct content/exercise/search/Arena mappings across existing curriculum revisions. This is the exact next implementation scope.

**Existing files likely to change:**

- `apps/api/app/database.py`, `app/main.py`, `app/models/entities.py`, `app/models/__init__.py`.
- `apps/api/app/services/course.py`, `services/arena.py`, `services/curriculum_migration.py`.
- `apps/api/tests/test_course.py`, `tests/test_arena_curriculum_v2.py`, `tests/test_content_bank.py`.
- `apps/api/app/config.py` and `apps/api/.env.example` for explicit backup/snapshot roots and the diagnosed relative-path setup defect; retain unrelated settings.

**New files/folders:**

- `apps/api/app/migrations/__init__.py`, `runner.py`, `v001_content_bindings.py`.
- `apps/api/app/schemas/content_registry.py`, `app/services/content_registry.py`, `app/services/database_backup.py`.
- `data/content-bindings/legacy-curricula.json` with reviewed, exact topic-to-content mappings.
- A local immutable legacy snapshot store under a configured data directory, with content-addressed filenames and no user edits to accepted source JSON.
- `apps/api/tests/test_database_migrations.py`, `test_content_bindings.py`, `test_data_preservation.py`.

**Database changes:** add migration ledger, immutable `ContentRevision`, ordered curriculum/topic `TopicContentBinding`, and curriculum-scoped `ArenaTopicBinding`. Retain `CourseLesson`, exercises, all histories and IDs. Existing active curriculum remains selected; prevent mapping sync from silently switching it. Make a consistent backup before upgrading a populated DB. Fresh installs use the same numbered initialization path.

**Tests required:** fresh/upgrade/repeat/interrupted migrations; backup opens and restores; existing row digests/IDs unchanged; active curriculum 1/2/custom preserved; ambiguous bindings rejected; multiple lessons per topic ordered; curriculum-scoped exercise sync/FTS; all 17 diagnosed Arena mapping misses resolved through explicit reviewed bindings; old content revisions remain resolvable; actual stored digest verified without overwriting legacy hash fields. Include a custom curriculum with a matching slug to catch first-track lookup bugs, and a clean setup using the sample environment to catch paths resolving outside Forge.

**Acceptance criteria:**

1. Existing learner row payloads, confirmed topic graphs and historical evidence are preserved. Only approved additive metadata/derived-index changes occur.
2. All 53 physical lessons are registered with an immutable legacy identity. Registration does not falsely assert editorial approval.
3. Every **explicitly bound** readable lesson has matching exercises/search scoped to the same curriculum/topic. Binding completeness is reported; no unreviewed topic merge is guessed.
4. Every current Arena problem maps correctly where an exact equivalence is established; all 17 known misses have reviewed mappings, and ambiguous future cases fail visibly.
5. Running initialization twice does not duplicate content, exercises, evidence or migration entries. Restore of a synthetic upgraded DB is demonstrated.

**Risks/dependencies:** the ordinary DB contains stale metadata and possibly copied mastery caches. Counts alone cannot validate preservation. Consolidated Python topics need reviewed multi-lesson mappings; do not equate a broad old topic with a new competency automatically. Snapshot disk usage and digest conventions must be defined. No scoring-policy replay in this phase.

**Explicitly out of Phase 1:** new curriculum activation or structural edits, new lessons/questions, runtime provider removal, mastery-policy changes, planner redesign, timed tests and interview redesign. Phase 1 does not certify existing content as pedagogically complete.

## Phase 2 — Repair publication gates and the known content defects

**Objective:** ensure an approved release is the exact tested bundle and correct the tuple/list and provenance inconsistencies through new revisions.

**Existing files likely to change:** `apps/api/scripts/course_builder/{validate,promote,build,fetch,sources}.py`; `scripts/problem_builder/{validate,promote}.py`; `app/schemas/{course,arena}.py`; `tests/{test_course,test_course_content_quality,test_content_bank,test_arena_judges}.py`; `content/problem-bank/dsa/dsa-two-sum-indices.json` as an input to a new revision, not an overwrite of historical identity; `data/course-sources.json`, `THIRD_PARTY_CONTENT.md`, `LICENSES/exercism-mit.txt` if verified upstream notices require correction.

**New files/folders:** `apps/api/scripts/content_checks/{bundle,examples,provenance,coverage}.py`; `tests/test_content_publication.py`; `data/content-approvals/`; immutable corrected problem/lesson revisions under the registry path. Add machine-readable example-fixture links and source IDs to new revision schemas.

**Database changes:** no destructive schema changes; register new content revisions and release bindings through Phase 1 tables. Historical attempts continue to resolve old versions. Publication status distinguishes legacy baselines, candidates, reviewed and approved releases.

**Tests required:** invalid exercise candidate cannot hide behind valid accepted exercises; first-time topic publication; stale approval/hash rejection; no accepted-file overwrite; provenance round trip; blocked/redirected source scope; full Python/SQL example execution where self-contained; expected-output/type comparison; deliberately incorrect reference implementations rejected; stable content digests. Execute all problem references and verify displayed two-sum example agrees with the typed judge.

**Acceptance criteria:** exact candidate bundle validated and explicitly approved; source metadata survives serialization; all known source/attribution mismatches have a documented resolution; original-only future Arena publication enforced; legacy adaptations/history retained truthfully; tuple/list contradiction and undefined no-solution contract fixed in a new approved version. Do not claim prose/reference answers fully verified until their review records exist.

**Risks/dependencies:** licensing/provenance cannot be reconstructed from a model assertion or an `adapted` boolean alone. Confirm per-item upstream revision/notices; unavailable provenance blocks new publication. Candidate tooling currently assumes accepted exercise files, so regression tests must precede refactoring. Some examples require contextual setup; do not execute database-connection examples against a real learner database.

## Phase 3 — Add edition and level metadata with an explicit curriculum draft

**Objective:** introduce independent product edition identity and subject/level navigation while retaining both historical curricula.

**Existing files likely to change:** `app/models/{entities,__init__}.py`; `app/schemas/api.py`; `app/services/{active_curriculum,curriculum,custom_curriculum,catalog,dashboard}.py`; `app/routers/{api,curricula}.py`; `apps/web/src/{App.tsx,services/api.ts,types/api.ts}`; `pages/{CurriculumPage,CurriculumBuilderPage,TopicPage,LearnPage}.tsx`; `tests/{test_curriculum,test_phase2_curricula,test_dashboard}.py`.

**New files/folders:** `data/editions.json`; `data/placement-foundations-scope.json`; `app/schemas/editions.py`; `app/services/editions.py`; `app/routers/editions.py`; `app/migrations/v002_editions_levels.py`; `apps/web/src/components/SubjectLevelNavigation.tsx`; `tests/test_editions.py`; frontend navigation tests.

**Database changes:** additive `EditionCurriculumBinding`, `TopicPlacement`, `LessonRevisionProgress`; store edition preference separately from curriculum ID/version. Create the proposed curriculum as a draft. Seed no fictitious mastery and do not implicitly confirm or activate it.

**Tests required:** existing revision 2 is not interpreted as product Forge V2; all nine subjects and levels visible; advanced-level metadata does not fork the app/database; confirmed immutability; explicit draft/confirmation/activation flow; manual access; reading progress stays separate from mastery; old/custom curricula and histories still accessible.

**Acceptance criteria:** navigation expresses all nine proposed subjects at Levels 1–3 with truthful availability; old curricula are unchanged; no topic access lock from recommendations; numeric levels are not inferred from mastery or `target_level`; activation is an explicit learner action after approval.

**Risks/dependencies:** new draft scope requires human review. Missing teaching must appear as missing, not as generated placeholders. Repeated concepts across subjects need stable competency identities and deliberate links, not duplicated score credit.

## Phase 4 — Complete deterministic objective assessment and Arena evidence

**Objective:** unify approved item selection/results, introduce numeric/SQL course assessment contracts, and repair independent coding evidence without rewriting history.

**Existing files likely to change:** `app/services/{practice,arena,mastery,readiness}.py`; `app/routers/{practice,arena,adaptive}.py`; `app/schemas/{practice,arena,adaptive}.py`; `app/models/{entities,__init__}.py`; `apps/web/src/features/practice/{pythonRunner,python.worker}.ts`; `features/arena/{judging,sqlRunner,sql.worker}.ts`; `pages/{PracticePage,ArenaPage,TransferPage,ReviewPage}.tsx`; `services/api.ts`; `types/{practice,arena,adaptive}.ts`; `tests/{test_practice,test_adaptive,test_arena_judges,test_arena_curriculum_v2}.py`.

**New files/folders:** `app/services/{assessment,scoring_policy}.py`; `app/schemas/assessment.py`; `app/migrations/v003_assessment_identity.py`; `tests/test_assessment_contracts.py`, `test_evidence_replay.py`; frontend numeric/SQL exercise renderers and result-contract tests; approved pool-role manifests.

**Database changes:** additive attempt-content snapshots/exposure records, scoring-policy version and stable unique evidence-source association. New Arena attempts link exact content revision. Existing `arena` evidence retains event type/score/time; projection incorporates it under an explicit versioned calculation. Preserve before/after projection records and leave ambiguous historical provenance unchanged.

**Tests required:** numeric normalization/units/tolerance; MCQ exact scoring; list/tuple/bool/int/exception/stdin contracts; SQL null/duplicate/order/columns and fresh DB isolation; score/result consistency; hints withheld until tracked reveal; solution/reference withheld before pass/Give Up; client retries idempotent; no farmable repeated Arena credit; meaningful Arena contribution to mastery; independent coding requirement; 79/89/24-hour gates; weak delayed recall can lower mastery; pending/reflection excluded.

**Acceptance criteria:** a passing first independent Arena solve contributes exactly once to the deterministic practice projection; unmapped/ambiguous history does not gain fabricated credit; reference validation is development-only for static items; scores are derived by backend policy from structured results. Local worker trust limits remain documented. Old source/attempt/evidence rows are not overwritten.

**Risks/dependencies:** score changes are visible to learners; replay must first run on a synthetic/copied DB and be reviewed. Do not upgrade raw client `score` into authoritative evidence. Current event uniqueness is enforced mainly by service queries; add idempotency constraints/associations without deleting historical duplicates.

## Phase 5A — Replace Tutor/doubts/generation UI with static guidance

**Objective:** remove teaching/chat and curriculum-generation dependencies while keeping manual drafts, static learning, search and history.

**Existing files likely to change:** `app/main.py`; `app/routers/{tutor,doubt,curricula,course}.py`; `app/services/{tutor,doubt,curriculum_generation,course}.py`; `app/schemas/ai.py`; `apps/web/src/{App.tsx,services/api.ts,types/api.ts}`; `components/{DoubtChat,Layout}.tsx`; `pages/{TutorPage,LearnPage,TopicPage,CurriculumBuilderPage,CurriculumPage}.tsx`; `tests/{test_phase2_ai,test_phase2_curricula,test_course}.py`.

**New files/folders:** `apps/web/src/components/LessonSearch.tsx`; `pages/GuidedLessonPage.tsx` only if static guidance needs a distinct screen; `tests/test_static_guidance.py`; frontend search/manual-draft tests.

**Database changes:** no new learner-history schema required. Preserve `ChatMessage`, `LearningSession`, `TutorSessionState` and curriculum-generation metadata as read-only legacy history. Use Phase 1 registry/FTS bindings.

**Tests required:** exact excerpt/source navigation; active curriculum scoping; no-match behavior; manual draft save/edit/confirm/activate without a provider; static help during an open transfer marks assistance; active scored interview blocks help; historical chats remain readable; no model call/import in new guidance paths.

**Acceptance criteria:** all normal teaching/explanation discovery works from static content; no dangling tutor/doubt/generate buttons; runtime cannot synthesize a lesson or curriculum; historical records remain intact.

**Risks/dependencies:** global DoubtChat is mounted in Layout; remove callers and backend dependencies together. Search itself can reveal answers, so assistance/assessment restrictions must be enforced at APIs, not just UI.

## Phase 5B — Replace generated practice, transfer and review

**Objective:** complete the core evidence loop entirely from reserved approved static items.

**Existing files likely to change:** `app/services/{practice,transfer,review,mastery}.py`; `app/routers/{practice,adaptive}.py`; `app/schemas/{practice,adaptive}.py`; `pages/{PracticePage,TransferPage,ReviewPage}.tsx`; `types/{practice,adaptive}.ts`; `services/api.ts`; `tests/{test_practice,test_adaptive}.py`.

**New files/folders:** `app/services/assessment_pool.py`; `data/assessment-pools/`; `tests/test_static_assessment_pools.py`; original approved transfer/recall variants published through Phase 2 gates.

**Database changes:** reuse Phase 4 exposure/content linkage; persist pool selection and context for resume. Keep old pending AI evaluations pending/history; do not backfill scores. Add a migration only if resumable selection needs a new association.

**Tests required:** unseen transfer exclusion, revealed/assisted exclusion, deterministic ordering, practice replay versus evidence deduplication, pool exhaustion, due recall >=24 hours, FSRS updates only after completed objective scoring, no generation fallback, no word-overlap free-text scoring, provider-forbidden paths.

**Acceptance criteria:** Python/SQL/DSA practice -> clean transfer -> delayed recall completes without a model; free text is saved as reflection or legacy pending, never fake-scored; explicit missing/exhausted pool states preserve manual practice.

**Risks/dependencies:** requires enough independently reviewed variants to distinguish practice from transfer/recall. Reusing familiar MCQs cannot substitute for independent coding. Content effort is separate from selection logic.

## Phase 5C — Replace interview generation and remove the runtime provider

**Objective:** deliver static scored technical mocks and honest communication rehearsal, then delete the remaining runtime model dependency.

**Existing files likely to change:** `app/services/{interview,usage}.py`; `app/routers/{interviews,ai}.py`; `app/schemas/{interview,ai}.py`; `app/providers/{base,dependencies,gemini,__init__}.py`; `app/config.py`, `app/main.py`; `apps/api/requirements.txt`, `.env.example`; `apps/web/src/pages/{InterviewPage,SettingsPage}.tsx`; `App.tsx`, `services/api.ts`, `types/{api,interview}.ts`; `tests/{fakes,test_interviews,test_phase2_ai,test_gemini_provider,test_practice}.py`; README and ARCHITECTURE.md.

**New files/folders:** `content/interview-bank/` (original versioned approved items); `data/interview-blueprints/`; `app/services/static_interview.py` if useful to isolate fixed selection; `tests/test_no_runtime_llm.py`, `test_static_interviews.py`; optional development-only requirements outside the runtime install for existing authoring scripts.

**Database changes:** additive blueprint/item revision snapshots associated with existing interview questions/sessions. Preserve question rubrics, responses, reports, `ModelUsageEvent`, AI settings and historical generated-by values. Unsupported old in-progress AI sessions remain saved/read-only rather than receiving invented continuation.

**Tests required:** fixed competencies/weights, one prewritten follow-up maximum, response/retry/resume, feedback withheld until completion, help blocked while active, reflection excluded from scored denominator and technical mastery, deterministic report, old reports resolve unknown/legacy modes, Settings works with no AI endpoint, startup/import and supported flows fail if any provider is requested. Verify no runtime `google-genai` dependency or Gemini environment requirement remains.

**Acceptance criteria:** scored objective interviews complete offline, open communication/design responses are labeled reflection, all provider routes/callers/config/cost UI are removed or explicitly historical, and no runtime module imports providers. No API key entry or usage budget is required for study. Keep `httpx` for tests/development where still used.

**Risks/dependencies:** fake-provider tests must be replaced by meaningful deterministic assertions, not simply deleted to turn CI green. Removing shared AI schemas prematurely can break manual draft import and historical report rendering. This slice depends on 5A/5B and a minimal approved static interview pool.

## Phase 6 — Publish nine-subject Levels 1–3 coverage in small batches

**Objective:** fill the actual curriculum gaps through verified original material, without runtime generation. Only this and the preceding explicitly identified static-pool work authorize later content authoring; Phase 0 authors no lessons.

**Existing files likely to change:** `data/course-sources.json`; `data/course-coverage/{python,sql-postgresql,dsa}.json`; `data/course-url-plans/{python,sql-postgresql,dsa}.json`; `content/ai-engineer/v1/manifest.json` only for compatibility metadata, not rewriting accepted lessons; `THIRD_PARTY_CONTENT.md`; relevant existing content validators/tests; the new draft/bindings from Phase 3.

**New files/folders:** approved coverage/source/URL-plan records for `quantitative-aptitude`, `logical-reasoning`, `verbal-english`, `system-design`, `ai-fundamentals`, `interview-communication`; `content/forge/<subject>/<topic>/revisions/`; original new problem revisions and assessment pools; per-bundle validation/review/approval records. Reuse accepted Python/SQL/DSA via registry bindings after review.

**Database changes:** content registration/bindings only. No learner reset, synthetic progress or mastery migration. Keep new curriculum in draft until coverage/review is approved; confirmation and activation remain explicit.

**Tests required:** concept-level coverage completeness per subject/level; all examples/reference solutions through deterministic checks; numeric answer arithmetic/units; reasoning puzzle validity/uniqueness; English accepted variants; source provenance/license checks; broken references; independent coding variants; negative solutions; no proprietary copied tasks; technical and clarity review for unautomatable content.

**Acceptance criteria:** every required competency in the approved nine-subject matrix has accepted teaching/practice/revision and an appropriate assessment or explicit reflection route. No placeholder can satisfy a topic by title alone. All new future Arena tasks meet original-only policy.

**Risks/dependencies:** six subjects lack existing accepted lessons, so content verification is a major workstream. Do not promise a lesson count or completion date before the concept matrix is approved. Employer-specific frequency claims require a separate current primary-source task.

**Batch rule:** publish one subject/level or small topic bundle at a time, each with its own tests, approval and rollbackable release binding. Prioritize Python/SQL/DSA prerequisites in parallel with initial aptitude/reasoning/English coverage, then system-design/AI/interview foundations. Later levels depend on reviewed earlier prerequisites, but manual access remains free.

## Phase 7 — Add balanced 5/6/8-hour daily plans

**Objective:** turn existing advisory planning into budget-correct, diverse, timezone-aware study allocation.

**Existing files likely to change:** `app/services/{planner,recommendations}.py`; `app/routers/adaptive.py`; `app/schemas/adaptive.py`; `app/models/{entities,__init__}.py`; `apps/web/src/pages/{DashboardPage,SettingsPage,ArenaPage}.tsx`; `services/api.ts`; `types/adaptive.ts`; `tests/{test_adaptive,test_recommendations}.py`.

**New files/folders:** `app/services/planner_policy.py`; `app/migrations/v004_plan_revisions.py` (number finalized by migration runner order); `tests/test_planner_budgets.py`; frontend preset/regeneration tests.

**Database changes:** additive plan revision metadata with local date/timezone, settings/policy version and activity links; preserve old `DailyPlanItem` IDs/statuses. Store user timezone and target settings explicitly.

**Tests required:** 300/360/480 budgets, due overload, zero/oversized minima, short leftover slots, missing content, mastered foundations, weak prerequisites, subject diversity/rotation, interview allocation, deterministic ties, local midnight, UTC elapsed recall gate, regeneration preserves completed/skipped tasks, manual access and topic-filtered Arena action paths.

**Acceptance criteria:** planned study minutes never exceed target; Python/SQL/DSA P0 priorities persist; multiple subjects plus review/interview receive meaningful allocation where approved content exists; unused minutes/gaps are shown honestly; completing a plan adds no mastery evidence.

**Risks/dependencies:** requires edition/level and availability metadata from Phases 1/3. Test selection policy independently before UI changes. Large targets do not justify repetitive content or fake tasks.

## Phase 8 — Add resumable timed subject and mixed tests

**Objective:** provide persisted, deterministic timed assessment beyond interview rehearsal.

**Existing files likely to change:** `app/models/{entities,__init__}.py`; `app/main.py`; shared assessment/scoring modules from Phase 4; `app/services/interview.py` for shared guard/report behavior only; `apps/web/src/{App.tsx,services/api.ts,components/Layout.tsx}`; `pages/InterviewPage.tsx` only where shared session controls are extracted.

**New files/folders:** `app/schemas/timed_tests.py`; `app/services/timed_tests.py`; `app/routers/timed_tests.py`; `app/migrations/v005_timed_tests.py` (final sequence assigned at implementation); `data/timed-test-blueprints/`; `apps/web/src/pages/TimedTestPage.tsx`, `types/timedTests.ts`; `tests/test_timed_tests.py`; frontend timer/resume tests.

**Database changes:** additive timed sessions/answers containing blueprint revision, item/content revisions, persisted start/deadline, state and result snapshots. Use existing attempts/evidence only through explicit approved context policy; no second scoring database.

**Tests required:** fixed weights and optional negative marking, deterministic selection, deadline expiry, refresh/resume, repeated submit, timeout during code execution, all feedback withheld until completion, help/solution endpoint guards, abandoned/expired session behavior, frozen content despite release updates, reflection excluded from scores.

**Acceptance criteria:** subject/level and mixed tests resume without restarting the clock, score deterministically and reveal detailed review only after completion. No live model is reachable.

**Risks/dependencies:** local machine clock is a personal-app trust boundary; do not claim proctored security. Pool exposure must be shared with transfer/interview selection to avoid false unseen credit. Builds on Phase 4 and static content availability.

## Phase 9 — Validate offline packaging, launcher safety and upgrades

**Objective:** demonstrate the complete installed product works offline and upgrades/restores preserve learner data.

**Existing files likely to change:** `scripts/{open-forge,close-forge}.ps1`, `scripts/verify_launcher.py`, `Open Forge.bat`, `Close Forge.bat`; `apps/api/app/{main,config}.py`; `tests/test_static_serving.py`; `apps/web/vite.config.ts`, `src/components/CodeEditor.tsx`, `src/features/practice/python.worker.ts`, `src/features/arena/sql.worker.ts` if asset resolution needs correction; package/lock files only for deliberately reviewed packaging changes; README, ARCHITECTURE.md, THIRD_PARTY_CONTENT.md.

**New files/folders:** isolated launcher verification harness with runtime/data-directory overrides; `tests/test_offline_assets.py`; browser journey tests for worker loading/execution/timeout and no-network operation; release/backup/restore instructions. Add a browser-test dependency only if needed for these actual journeys, not by default.

**Database changes:** no destructive changes. Exercise all numbered migrations on populated synthetic/copy fixtures; verify backup restoration and historical content resolution. Never test reset/upgrade against the ordinary learner database.

**Tests required:** all backend/frontend checks; every shipped content validator; real browser Pyodide/PGlite/Monaco asset loading with external network disabled; startup without provider packages/key; complete learn/practice/Arena/transfer/recall/planner/timed/interview loops; port fallback, duplicate launch, missing build, stale/reused PID protection and idempotent close. Check production SPA/API/asset boundaries, route-safe static file resolution and startup diagnostics.

**Acceptance criteria:** no runtime model/network dependency, all nine-subject publication gates complete, relevant checks pass, launchers operate only on verified Forge processes, and restored backups reproduce learner history. Record remaining build warnings and actual bundle/runtime measurements; do not describe unit tests as proof of complete offline operation.

**Risks/dependencies:** WASM/editor bundles are substantial; build success does not prove browser loading. Test launcher lifecycle only in an isolated runtime context. This is an integration milestone, not permission to add a desktop wrapper, service worker, cloud service or unrelated infrastructure.

## Sequencing and stop conditions

Phase 1 precedes any learner-data/content migration. Phase 2 gates all new publication. Phase 3 can proceed after Phase 1 while assessment contracts are implemented; 5A depends on content/search bindings, 5B on objective pools/evidence, and 5C on both. Content batches can proceed after schemas/coverage/gates are stable. Planner and timed tests build on approved content and shared assessment; offline validation closes the release.

Stop a publication if coverage, provenance, expected output, review or approval is missing. Stop an upgrade if backup/integrity/preservation checks fail. Stop scoring unsupported answers rather than inventing results. None of these stop conditions authorizes deleting historical data, weakening deterministic checks, changing a confirmed curriculum in place, or calling a runtime model.
