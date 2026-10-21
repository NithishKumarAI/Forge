# Forge V1 Phase 0 repository audit

Audit date: 21 October 2026 (Asia/Calcutta). The local working tree is authoritative. This document records observations, not a release certification. Proposed behavior is described separately in [ARCHITECTURE_PLAN.md](ARCHITECTURE_PLAN.md), [CURRICULUM_SCOPE.md](CURRICULUM_SCOPE.md), and [IMPLEMENTATION_ROADMAP.md](IMPLEMENTATION_ROADMAP.md).

## 1. Baseline and boundaries

- Checkout: `C:\My PC\git\Forge`, branch `main`, HEAD `51605d8` (`final verification`). No remote checkout was substituted for these files.
- Existing modifications: `.gitignore`; `apps/api/app/{config,main}.py`; `apps/api/scripts/course_builder/validate.py`; `apps/api/tests/test_course_content_quality.py`; eleven DSA lessons (`backtracking`, `bfs`, `big-o`, `dfs`, `dynamic-programming`, `graphs`, `hash-maps`, `recursion`, `sets`, `trees`, `two-pointers`); six SQL lessons (`constraints-design`, `ctes`, `data-modification`, `database-python`, `indexes`, `postgresql-practicals`). These changes predate the audit and were not edited.
- Existing untracked work: `Open Forge.bat`, `Close Forge.bat`, `scripts/`, and `apps/api/tests/test_static_serving.py`. These are part of the inspected local implementation.
- Phase 0 creates only the four requested Markdown documents. No application/content edits, commits, pushes, provider calls, content generation, or learner-data migrations were performed. Test/build caches are verification artifacts.
- Existing SQLite files include `apps/api/data/forge.db` and six smoke databases. The normal database was opened with SQLite URI `mode=ro` and `PRAGMA query_only=ON`; only schema, counts, curriculum metadata, and mapping aggregates were read.
- Repository-wide enumeration encountered permission errors in existing `apps/api/data/pytest-arena-temp` and `pytest-full-temp`. Source inspection used explicit source directories; pytest used a separate temporary directory. Those inaccessible directories were not changed.

## 2. Overall finding

Reuse the current React/FastAPI/SQLite application. There is no technical basis for a rewrite. It already has substantial deterministic learning infrastructure, but it is an AI/Python-engineering preparation product, not the requested nine-subject Placement Foundations edition.

The largest blockers are content identity across curriculum revisions, runtime model dependency in assessment, incomplete objective coding evidence integration, and absence of placement aptitude/English content. Passing existing validators does not mean the material is fully correct or complete.

## 3. Existing application and reusable systems

### Frontend

`apps/web/package.json` defines Vite, React, TypeScript, React Router, Tailwind, Monaco, Pyodide, PGlite, and Vitest. `package-lock.json` exists; many declared dependency ranges are `latest`, so future lockfile updates need deliberate review.

`apps/web/src/App.tsx` routes Dashboard, Curriculum, custom curriculum drafts, Topic, Learn, AI Tutor, Practice, Transfer, Arena, Review, Interview, reports, and Settings. Arena and interview screens are lazy-loaded. Existing pages, layout, Markdown rendering, typed API client, loading/error states, and editors are reusable.

`LearnPage.tsx` consumes static lesson JSON through the API; normal Learn does not call Gemini. `Layout.tsx` mounts global `DoubtChat`; `SettingsPage.tsx` makes successful AI-status loading a prerequisite for the settings screen. Removing only backend AI routes would therefore break frontend behavior.

### Backend and startup

`apps/api/app/main.py` composes ten router groups, health, `/assets`, and SPA fallback. Lifespan runs table creation, revision-1 and revision-2 curriculum seeding, default migration/activation, evidence backfill, course synchronization, and Arena synchronization. `database.py` uses SQLModel/SQLAlchemy with SQLite; there is no versioned schema migration runner. `create_all` creates missing tables but is not a migration strategy for changed existing columns.

Service boundaries already exist for curriculum, course, practice, Arena, mastery, transfer, FSRS review, planner, readiness, dashboard, interviews, and usage. Keep these boundaries and extend their contracts.

### Learning and assessment

- `services/custom_curriculum.py` distinguishes drafts from confirmed curricula; confirmed structures require a new version. Manual browsing and active-curriculum selection exist.
- `services/practice.py` prefers static exercises, grades MCQs deterministically, persists answers/attempt history, and separates pending evaluations from completed evidence.
- `features/practice/python.worker.ts` runs learner Python in Pyodide; `pythonRunner.ts` handles initialization, timeout termination, and restart. The typed comparison harness distinguishes list/tuple and bool/int, supports exceptions and stdin/stdout.
- `features/arena/sql.worker.ts` creates an ephemeral PGlite database per request. `sqlRunner.ts` gives each run a separate worker and terminates it on timeout. This is separate from Forge SQLite.
- `features/arena/judging.ts` and the SQL validator compare columns, normalized rows, and ordering where required. SQL fixtures include alternate datasets.
- `services/mastery.py` implements weighted practice evidence, hint penalties, clean-transfer and delayed-recall gates, confidence, and downward revision after weak delayed recall.
- `services/review.py` maps objective scores to FSRS ratings and stores a versioned FSRS JSON envelope. FSRS controls due dates rather than mastery.
- `services/planner.py` persists advisory plans; prioritizes due reviews, repeated mistakes, Python/SQL/DSA minima, and topic priorities. Study targets already accept 30–480 minutes. The UI exposes a minute field, not 5/6/8-hour presets.
- `services/interview.py` supplies seven fixed blueprints, fixed rubric weights, bounded follow-ups, active-assessment help blocking, saved sessions, history, and deferred reports. Wording and non-code grading still require a provider.

## 4. Curriculum and content inventory

### Namespaces are currently different things

`data/default-ai-engineer-curriculum.json` is curriculum revision 1: ten tracks, 160 topics. `data/default-interview-curriculum-v2.json` is revision 2: eleven tracks, 97 topics. Neither is the proposed Forge V1/V2 product edition definition. `content/ai-engineer/v1` is a content-pack directory, not a guarantee that it implements Placement Foundations Levels 1–3.

Both curriculum JSON files have valid prerequisite references in the structural audit. These counts do not establish topic coverage or prerequisite pedagogical quality.

### Revision 1: all tracks and topic slugs

- `python` (18): syntax-data-types, collections, control-flow, functions, comprehensions, oop, exceptions, type-hints, iterators, generators, decorators, file-handling, modules-packages, virtual-environments, async-await, debugging, testing, reading-unfamiliar-code.
- `backend-engineering` (22): http-fundamentals, rest, request-response-lifecycle, fastapi, pydantic-validation, routing, dependency-injection, authentication, jwt-basics, oauth-basics, orm-concepts, postgresql-fundamentals, migrations, pagination, background-work, external-api-integrations, retries, timeouts, error-handling, logging, testing, api-design.
- `sql-cs` (13): select-filtering, joins, group-by, subqueries, ctes, window-functions, indexes, transactions, normalization, database-relationships, big-o, process-thread-basics, networking-basics.
- `dsa` (18): arrays, strings, hash-maps, sets, two-pointers, sliding-window, sorting, binary-search, stacks, queues, linked-lists, recursion, trees, bfs, dfs, heaps, graph-basics, dynamic-programming-basics.
- `machine-learning` (16): training-vs-inference, data-splits, preprocessing, overfitting, bias-variance, data-leakage, classification-metrics, precision, recall, f1-score, embeddings, decision-trees, xgboost, feature-engineering, model-evaluation, pytorch-fundamentals.
- `llm-engineering` (19): transformer-intuition, tokens, context-windows, model-apis, prompt-design, structured-outputs, tool-calling, agent-loops, agent-state, memory-concepts, human-approval, retries, rate-limits, streaming, latency, cost-trade-offs, hallucinations, evaluation, safety-fundamentals.
- `rag` (16): document-ingestion, chunking, embeddings, similarity-search, vector-databases, pgvector, qdrant-awareness, metadata-filtering, retrieval, reranking, context-construction, citations, hallucination-control, retrieval-evaluation, answer-evaluation, hybrid-search.
- `production-devops` (14): git, linux-basics, docker, environment-variables, secrets, ci-cd, gcp, cloud-run, logging, monitoring, tests, permissions, failed-deployments, basic-scalability.
- `frontend-basics` (11): javascript-fundamentals, typescript-basics, react-components, props, state, hooks, api-calls, loading-states, error-handling, forms, frontend-debugging.
- `interview-engineering` (13): project-explanation, technical-decisions, bug-stories, trade-offs, testing-explanations, live-coding, api-design, system-design, rag-system-design, agent-system-design, behavioral-fundamentals, robin-architecture, cognitive-memory-engine-architecture.

### Revision 2: all tracks and topic slugs

- `python` (14, priority 100): foundations, control-flow, strings, collections, functions, pythonic-programming, oop, exceptions-files-data, modules-packages-environments, advanced-working-python, standard-library, concurrency, testing-debugging-quality, reading-unfamiliar-code.
- `sql-postgresql` (14, priority 100): relational-foundations, query-basics, values-expressions, aggregation, joins, subqueries, ctes, window-functions, data-modification, constraints-design, indexes, transactions, postgresql-practicals, database-python.
- `dsa` (20, priority 98): big-o, arrays, strings, hash-maps, sets, two-pointers, sliding-window, sorting, binary-search, stack, queue-deque, linked-lists, recursion, backtracking, trees, bfs, dfs, heaps, graphs, dynamic-programming.
- `backend-engineering` (8, priority 90): http-client-server, fastapi-validation, crud-postgresql, auth, async-integrations, reliability, api-design-security, testing.
- `cs-fundamentals` (7, priority 88): complexity-memory, oop, concurrency, networking, databases, engineering-process, system-design.
- `llm-engineering` (6, priority 85): models-context, prompt-context, structured-tools, agents-state, reliability-cost, evaluation-safety.
- `rag` (6, priority 85): ingestion-chunking, embeddings-similarity, vector-stores, retrieval-reranking, context-citations, evaluation.
- `machine-learning` (6, priority 70): numpy-pandas, learning-data, model-problems, metrics, models-features, embeddings-pytorch.
- `production-devops` (7, priority 65): git-linux, configuration-secrets, docker, ci-deployment, gcp-cloud-run, operations, scalability.
- `frontend-basics` (4, priority 45): javascript-typescript, react, api-forms, debugging.
- `interview-engineering` (5, priority 90): project-pitches, engineering-stories, live-coding, debugging-api-design, system-design-behavioral.

### Static course pack: actual files

`manifest.json` lists 53 compiled topics across three tracks; every listed lesson exists and no accepted lesson is unlisted. Coverage files and reviewed-URL-plan files each cover all their track's existing lessons.

- Python: 19 lessons, 112 sections, 102 examples, 133 exercises (57 MCQ, 76 short answer).
- SQL/PostgreSQL: 14 lessons, 72 sections, 74 examples, 98 exercises (42 MCQ, 56 short answer).
- DSA: 20 lessons, 100 sections, 82 examples, 140 exercises (60 MCQ, 80 short answer).
- Total: 53 lessons, 284 sections, 258 examples, 371 exercises (159 MCQ, 212 short answer). All lesson versions are `1.1.0`. There are **zero** `python_code`, `python_debug`, or executable SQL items in the course exercise files; independent coding practice is currently supplied by Arena or runtime generation.
- Python lesson slugs are the revision-1 Python list plus `strings`.
- SQL lesson slugs exactly match the revision-2 SQL list.
- DSA lesson slugs match revision 2 except that files use `stacks` and `queues`, rather than `stack` and `queue-deque`.

No static lesson packs exist for quantitative aptitude, logical reasoning, verbal/English, system design, AI foundations, or interview/communication. Curriculum titles in related historical tracks are reusable scope ideas, not accepted teaching material. Nothing assigns the nine requested subjects to numeric Levels 1–3.

### Arena bank

`content/problem-bank` contains 110 JSON problems:

- Python: 40 (27 easy, 13 medium).
- SQL: 30 (15 easy, 15 medium).
- DSA: 40 (18 easy, 22 medium).

All current Python/DSA references pass their stored tests. All SQL references pass the real PGlite visible and alternate datasets. This establishes agreement with the test fixtures, not comprehensive correctness of every statement or edge case.

Nine Python JSON records declare Exercism adaptation: anagram-check, bob, collatz, flatten-list, leap-year, pangram, raindrops, two-fer, word-count (each has the `python-` prefix). `THIRD_PARTY_CONTENT.md` instead enumerates four adaptation identifiers, including celsius-to-fahrenheit, which is not marked adapted in its JSON. `schemas/arena.py` permits only `source_type="original"` and drops extra provenance fields on model serialization. Attribution metadata and publication policy need reconciliation before claiming an original-only shipped bank. Preserve the existing bank and learner history; do not silently relabel adaptations as original.

## 5. Defects and limitations requiring action

### P0: curriculum/content binding is not reliable

`services/course.py` finds the first `Track.slug` without curriculum scoping during course/exercise sync and FTS indexing. Normal lesson reads derive a path from slugs, so a readable lesson does not prove its exercises or search entries were synchronized for that topic ID. Only `python/foundations` has a special alias. Versioned metadata does not determine runtime reads; the filesystem does.

For revision 2, 39 of 97 topics have a readable lesson path (Python 7, SQL 14, DSA 18). The other 58 do not. The two DSA name mismatches are explicit; seven consolidated Python topics need multi-lesson mappings rather than a guessed single alias.

The ordinary database has 98 `CourseLesson` rows (68 for curriculum 1, 30 for curriculum 2); these are historical metadata rows and must not be reported as 98 distinct shipped lessons. An isolated fresh startup created only 49 metadata rows (34 for curriculum 1, 15 for curriculum 2) and 343 exercises (238/105 respectively). Of the 39 readable active topics, 24 had no static exercises: six Python topics (control-flow, strings, collections, functions, oop, reading-unfamiliar-code) and all 18 readable active DSA topics. This reproduces the first-track lookup defect independently of stale ordinary-DB metadata. Fix with explicit curriculum-topic-to-immutable-content bindings, including ordered multiple lessons per topic, not broad slug substitutions.

`services/arena.py` has only three aliases. Seventeen problems remain unmapped to the active curriculum: two Python and four DSA problems use `dsa/stacks`, while eleven SQL problems use `sql-cs/subqueries` (4), `sql-cs/ctes` (2), or `sql-cs/group-by` (5). These are confirmed both by static mapping inspection and existing DB null mappings.

### P0: Arena evidence is excluded from mastery calculations

`record_attempt` appends `MasteryEvidenceEvent(event_type="arena")` for a first successful mapped problem and then calls `recalculate_topic`. `practice_metrics` selects only `event_type="practice"`; transfer and recall are the other score branches. Arena events therefore do not increase the score or establish transfer eligibility. Preserve all existing Arena events and add a versioned, deterministic projection policy with replay tests. Also record a stable Arena-attempt linkage for new events; current metadata contains problem key/difficulty, not an Arena-attempt foreign key.

### P0: the complete learning loop requires Gemini

Static reading, MCQs and Arena execution work without a key, but 212 static short answers become pending, fresh transfers explicitly require Gemini, reviews may choose short answers, and scored interviews require generation/evaluation. Disabling chat alone does not create an offline assessment product. See section 6 for all integration surfaces.

### P1: a problem statement contradicts the strict judge

`content/problem-bank/dsa/dsa-two-sum-indices.json` says return a tuple and displays `(0, 1)`. Its starter signature, reference, and expected tests require a list. Strict type checking rejects a learner following the statement. A supplemental literal-example comparison evaluated 83 parseable function examples and found this mismatch; 28 examples were skipped because they needed nonliteral input/output parsing or different invocation handling. This is a bounded check, not a complete editorial review. The normal validator still passes this problem.

The same file has the placeholder constraint “Reasonable constraints for the problem” and returns `[0, 0]` when no pair exists without defining that case in its contract. Define bounds and no-solution behavior before approval.

### P1: content validation and approval are incomplete

- `course_builder/validate.py` validates Pydantic structure, literal coverage terms, section length/headings, basic checkpoints, Python AST syntax, MCQ indices, short-answer rubric presence, and detected Arena reference keys. All 53 topics are now in `QUALITY_TARGETS`; README's “thirteen priority lessons” claim is stale.
- It does not execute the 258 lesson examples, assert expected output, prove MCQ answer correctness, evaluate free-text reference answers, verify source licensing, or prove that an analogy/explanation is correct or beginner-friendly. SQL lesson examples are not covered by the Arena SQL validator.
- All 53 lesson `content_hash` values differ from SHA-256 calculated using the current builder's `StaticLesson.model_dump_json(exclude={"content_hash","generated_at"})` algorithm. This is a reproducibility/integrity mismatch, not proof of malicious edits; no check currently enforces the hash contract.
- `course_builder/promote.py` validates `lesson.candidate.json`, but lesson validation reads sibling **accepted** `exercises.json`, then replaces both accepted files with candidates. It does not validate the exact new exercise candidate bundle as a unit, can require an already-existing exercise bank, and overwrites accepted paths rather than preserving immutable revisions. No approval record/reviewer identity is required.
- Source registry contains 24 track-scoped records (13 Python, 6 SQL, 5 DSA); 9 are enabled. There is one cached source snapshot. Forty-five lessons reference at least one URL with no matching local snapshot. This is incomplete reproducibility, not proof the sources were never reviewed.
- SQL `database-python` cites `python-stdlib-docs`, absent from its SQL track's registry but present elsewhere. Define cross-subject source identity explicitly.
- Fetching rejects disabled/reference-only sources and checks HTTPS/path scope and robots text. Redirect destinations are not revalidated against the source registry. Treat fetch hardening and snapshot retention as development-pipeline work; runtime should never fetch.

### P1: practice and mastery policy need objective assessment coverage

Static course exercises contain only MCQs/free text. Offline users cannot currently supply the mixed completed evidence needed for transfer eligibility through most course packs. `start_practice` excludes successfully attempted exercises and eventually exhausts a finite bank; define deliberate replay and distinct-evidence rules. Current eligibility accepts two exercise types, without requiring independent coding for Python/SQL/DSA.

Pending answers are correctly excluded from evidence, but their `Attempt.score` storage uses a numeric placeholder because the table requires a score; consumers must honor `evaluation_status`, not aggregate raw attempt scores. Keep old pending rows pending. Provider-graded completed historical evidence must retain its original grading source; never relabel it as deterministic.

### P1: score boundaries and trust

Arena submission trusts client-provided `passed` and `score`; practice Python checks test identities but trusts client-reported pass flags. The current local-personal trust model is documented in README. Backend aggregation is deterministic, but it is not independent server-side verification of arbitrary learner code. Keep worker execution for the local edition, validate the complete result contract and derive scores on the backend; do not claim tamper-proof assessment.

Arena's public serializer currently includes the full hints list before calling the hint endpoint, so a technical client can read hints without incrementing assistance. It should expose only a hint count. Pending Python reference-validation endpoints can also return reference solutions before a learner passes or gives up; move static reference validation entirely to the development pipeline. Browser-accessible hidden tests are not secrets.

### P1: planner and launch gaps

Planner uses UTC's calendar date, can exceed the requested budget (due reviews/minima are added before budget checks, and the last task is not clipped), and fills remaining time by topic rank without subject-diversity or interview quotas. Existing plans are returned after settings changes without explicit versioning/regeneration. Foundation tasks point to generic `/arena`, rather than preserving selected subject/topic filters.

The launchers serve a production build on loopback, discover ports 18100–18149, and reuse recorded process/health state. `close-forge.ps1` trusts a recorded PID without verifying process identity; a reused PID can stop an unrelated process. `verify_launcher.py` closes any recorded running instance and assumes port 18101 is free, so it was not executed against the user's current runtime. The startup active-curriculum migration also changes revision-1 activation automatically; the new edition must require an explicit selection instead.

The four `../../../...` content/data overrides in `.env.example` resolve outside Forge when run from the documented `apps/api` working directory: e.g. `../../../content/ai-engineer/v1` resolves to `C:\My PC\git\content\ai-engineer\v1`, which does not exist. A copied example environment can therefore break startup/content loading even though default anchored settings work. Resolve relative configuration against an explicit root or correct the sample paths, with a setup regression test. Do not assume the existing successful development environment validates clean installation from `.env.example`.

## 6. Complete runtime LLM dependency map and removal boundary

No other provider integration was found in the inspected application source; the abstraction is generic but the implementation is Gemini.

- Provider transport: `app/providers/{base,dependencies,gemini,__init__}.py`. Lazy SDK import, cached configured provider, Google Interactions API, retry/error handling, JSON schema requests and Pydantic validation.
- Tutor: `routers/tutor.py`, `services/tutor.py`, `schemas/ai.py`; structured turns, grounded static lesson context, chat and usage storage.
- Doubts: `routers/doubt.py`, `services/doubt.py`; local FTS context followed by `generate_text`. Keep retrieval, replace synthesized chat with exact excerpts, sources and navigation.
- Curriculum preview: `routers/curricula.py`, `services/curriculum_generation.py`, `schemas/ai.py`. Keep manual draft/save/confirm/activate operations in `custom_curriculum.py` and `active_curriculum.py`; remove only provider generation.
- Practice: `routers/practice.py`, `services/practice.py`, `schemas/practice.py`: missing-pack generation, repair, and free-text evaluation. Keep MCQ/code scoring, attempts, hints, and history; use approved static pools and unscored reflection.
- Transfer: `routers/adaptive.py`, `services/transfer.py`: new unseen task generation; replace with reserved static variants and explicit pool exhaustion.
- Reviews: `routers/adaptive.py`: generation fallback and short-answer evaluation; retain FSRS queues and use only deterministic approved questions for scored recall.
- Interviews: `routers/interviews.py`, `services/interview.py`, `schemas/interview.py`: question/coding generation, rubric dimension evaluation, contextual follow-up wording, optional report narrative. Retain fixed blueprints, session persistence and calculations; replace with static question selection and deterministic grading. Open communication/project responses must be unscored reflection, not an invented objective score.
- Status/budgets: `routers/ai.py`, `services/usage.py`, `schemas/ai.py`, `schemas/interview.py`, model `ModelUsageEvent` and AI `AppSetting` keys. Remove live settings/cost surfaces only after client callers are migrated; preserve historical usage rows.
- Frontend: `pages/{TutorPage,CurriculumBuilderPage,SettingsPage,InterviewPage,TopicPage,LearnPage,PracticePage,TransferPage,ReviewPage,CurriculumPage}.tsx`; `components/{DoubtChat,Layout}.tsx`; `App.tsx`; `services/api.ts`; `types/{api,practice,adaptive,interview,course}.ts` contain UI, route, client or contract dependencies. `api.ts` includes `aiStatus`, budget methods, generation, tutor and doubt calls.
- Configuration: `app/config.py`, `.env.example`, README. Variables: `GEMINI_API_KEY`, `GEMINI_MODEL`, `GEMINI_TUTOR_THINKING`, `GEMINI_DOUBT_THINKING`, `GEMINI_CURRICULUM_THINKING`, `GEMINI_EXERCISE_THINKING`, `GEMINI_ANSWER_EVALUATION_THINKING`, `GEMINI_INTERVIEW_THINKING`, `GEMINI_INTERVIEW_EVALUATION_THINKING`, `GEMINI_INPUT_PRICE_PER_MILLION`, `GEMINI_OUTPUT_PRICE_PER_MILLION`, `GEMINI_CACHED_INPUT_PRICE_PER_MILLION`. Local `.env` secrets were not printed.
- Package: `apps/api/requirements.txt` contains `google-genai==2.25.0`. There is no frontend LLM SDK. Keep `httpx` where used by tests/development source tooling; do not remove it just because Gemini also uses it.
- Development-only tools: `scripts/gemini_smoke.py`, `scripts/course_builder/build.py`, `scripts/problem_builder/build.py` call the provider; `manual_v1_fixture.py` seeds AI settings. Existing fake-provider tests live in `tests/fakes.py`, `test_phase2_ai.py`, `test_phase2_curricula.py`, `test_practice.py`, `test_adaptive.py`, `test_interviews.py`, and provider tests. Replace runtime AI assertions as deterministic replacements land; retain meaningful data-preservation coverage.

Safe sequence: repair content identity and preservation first; add static assessment pools; replace each consumer end to end; then remove provider imports/routes/settings/package from the runtime distribution. Optional agent-assisted authoring belongs in development tooling with separately installed dependencies, never in startup or the learner application. Existing AI histories remain readable. A blank API key is insufficient evidence of removal; test startup and all supported journeys with provider imports forbidden and outbound networking blocked.

## 7. Database preservation inventory

Observed normal DB: two confirmed curricula, 21 tracks, 257 topics and 257 learner states; active curriculum ID 2. Counts at inspection: 6 attempts, 6 details, 6 mastery events, 1 review state, 0 review events, 20 plan items, 23 section-progress rows, 679 exercises, 110 Arena problems, 5 Arena attempts, 28 topic-migration-map rows, and no interview sessions/responses/reports. Counts are a snapshot of this checkout, not test fixtures or product defaults.

Storage in `models/entities.py`:

- Curriculum structure: `Curriculum`, `Track`, `Topic`, `TopicPrerequisite`; `AppSetting.active_curriculum_id`; draft-generation metadata retained separately.
- Learning history: `LearningSession`, `ChatMessage`, `TutorSessionState`, `LessonSectionProgress` (currently keyed by topic/section, not lesson revision).
- Course/exercise metadata: `CourseLesson` (unique topic/content_version), `Exercise.content_json`, `PracticeSessionExercise`, `PracticeHintUse`.
- Evidence: `Attempt`, `ExerciseAttemptDetail`, `MasteryEvidenceEvent`, `TransferCheck`, `Mistake`; learner state is a derived/cache projection, not original evidence.
- Scheduling/planning: `ReviewState.state_json`, append-only `ReviewEvent`, and mutable `DailyPlanItem` status.
- Interviews: `InterviewSession`, `InterviewQuestion` with stored rubric, `InterviewResponse` with evaluation JSON, `InterviewReport`.
- Arena: `ArenaProblem` mutable metadata/source path, `ArenaAttempt`, `ArenaHintUse`; attempts currently reference a problem key rather than a content revision.
- Compatibility/history: `TopicMigrationMap`, `ModelUsageEvent`, `CurriculumGenerationMetadata`.
- Search: `course_content_fts` and SQLite FTS shadow tables are derived/rebuildable, unlike learner history.

`curriculum_migration.py` copies cached learner fields for 28 explicit topic mappings and changes active revision 1 to revision 2; it does not move attempt/evidence/review history. A copied mastery cache without corresponding evidence is not an evidence migration. Do not reuse this algorithm to merge product editions or inflate new-topic mastery. The migration-safe design and copy/restore tests are in the architecture plan.

## 8. Verification execution record

Existing dependencies were used without installation. Working directories below are part of each command. For Python verification, the process environment set `GEMINI_API_KEY=''` and `FORGE_DATABASE_URL='sqlite:///:memory:'` before execution; `load_dotenv` therefore did not enable the local key or ordinary database. Tests use injected fakes, mocks, and in-memory SQLModel sessions. No model smoke tool, source fetch/build, fixture seeder against learner data, or destructive database command was run.

### Existing checks

From `C:\My PC\git\Forge\apps\api`:

```powershell
$env:GEMINI_API_KEY=''
$env:FORGE_DATABASE_URL='sqlite:///:memory:'
.\.venv\Scripts\python.exe -m pytest -q --basetemp='C:\My PC\git\Forge\scratch\phase0-full-http-20261021'
.\.venv\Scripts\python.exe -m scripts.course_builder.validate --track python
.\.venv\Scripts\python.exe -m scripts.course_builder.validate --track sql-postgresql
.\.venv\Scripts\python.exe -m scripts.course_builder.validate --track dsa
.\.venv\Scripts\python.exe -m scripts.problem_builder.validate
```

Results:

- Backend suite: exit 0, **137 passed**, 1 warning, 124.09 seconds. Warning: Starlette TestClient uses the deprecated `anyio.abc.BlockingPortal` alias. The successful full command ran outside the socket-restricted sandbox, still with Gemini disabled and an in-memory database.
- Python lessons: exit 0, 19 validated.
- SQL/PostgreSQL lessons: exit 0, 14 validated.
- DSA lessons: exit 0, 20 validated.
- Full problem bank: exit 0, 110 validated, including SQL through Node/PGlite.

From `C:\My PC\git\Forge\apps\web`:

```powershell
npm test
npm run typecheck
npm run build
npm run validate:sql-problems
```

- Vitest: exit 0, 4 files / 22 tests passed. Coverage includes deterministic judging and PGlite integration/isolation; it is not a full rendered-UI or browser end-to-end suite.
- Typecheck: exit 0 (`tsc -b`).
- Build: exit 0 (`tsc -b && vite build`); 3311 modules transformed and five Pyodide assets copied. Warnings: Pyodide's Node built-ins externalized for browser compatibility, PGlite direct `eval`, and bundles larger than 500 kB (editor API approximately 2.65 MB minified). These warnings were not suppressed or treated as test failures.
- Standalone SQL validation: exit 0, **30 passed, 0 failed, 60 datasets**.

There is no separate configured backend static type-checker or frontend lint script. No unconfigured check is reported as passing.

### Supplemental audit probes

Read-only Python snippets run with `apps/api/.venv/Scripts/python.exe -` from the repository root parsed curriculum/content JSON, counted fields, compared `manifest.compiled_topics` against paths, checked prerequisite existence, compared Arena mappings against revision-2 keys plus the three actual aliases, compared builder-format content hashes, and queried normal SQLite in read-only mode. These probes exited 0 and produced the counts/findings above. An initial inventory probe looked for a generic manifest key before reading `compiled_topics`; the corrected comparison confirmed all 53 entries. Raw-JSON hashing was followed by the exact Pydantic serialization algorithm before recording the mismatch finding.

The display-example probe used `ast.literal_eval` on example input/output and called the accepted reference function with tuple inputs expanded as arguments; it checked 83 examples, skipped 28 and found the tuple/list mismatch. It never executed learner submissions.

An isolated startup probe replaced `app.main.engine` with `create_engine('sqlite://', connect_args={'check_same_thread':False}, poolclass=StaticPool)`, created tables on that engine, and overrode `get_session` for `TestClient`. Its completion record is below. It never opened the normal DB for writing.

- Startup probe: exit 0 outside the socket-restricted sandbox. `/health`, `/`, `/arena`, `/api/dashboard`, `/api/course/search?q=loops`, and `/api/arena/summary` returned 200 with the expected JSON/HTML content types; `/api/nonexistent_phase0` returned 404 JSON. Fresh active curriculum was revision 2. Metadata/exercise counts and the 24 missing exercise bindings are recorded in section 5. This verifies HTTP responses and fresh sync, not rendered browser execution.
- Full collection command `.\.venv\Scripts\python.exe -m pytest --collect-only -q` from `apps/api` exited 0 and collected 137 tests (0.44 seconds).
- The initial full run used `--basetemp='C:\My PC\git\Forge\scratch\phase0-pytest-20261021'` inside the sandbox and stalled at `tests/test_health.py`; it was interrupted with exit 1. An initial in-memory TestClient probe also stalled and was interrupted. Neither is counted as a pass.
- A bounded diagnosis ran `pytest.main(['-vv','-s','tests/test_health.py'])` through `.\.venv\Scripts\python.exe -` with `faulthandler.dump_traceback_later(15,exit=True)`: exit 1 after 15 seconds. Stack traces show Windows `asyncio` Proactor initialization blocked in `socket._fallback_socketpair -> accept`, before the health handler. This was an execution-environment limitation, not a demonstrated health-handler defect.
- The same four HTTP tests were then run outside the sandbox using `pytest.main(['-q','tests/test_health.py','tests/test_static_serving.py','tests/test_practice.py::test_practice_routes_protect_answers_and_run_is_unscored','--basetemp=C:/My PC/git/Forge/scratch/phase0-http-20261021'])`, with a 30-second faulthandler bound. Result: exit 0, **4 passed**, 1 warning, 0.68 seconds. These four are a subset of the later successful 137-test run, not extra unique tests.
- An intermediate service-only attempt used `.\.venv\Scripts\python.exe -m pytest -q --ignore=tests/test_health.py --ignore=tests/test_static_serving.py -k 'not practice_routes_protect_answers_and_run_is_unscored' --basetemp='C:\My PC\git\Forge\scratch\phase0-services-20261021'`; it was interrupted with exit 1 once the socket limitation was resolved. It is not counted as a completed pass; the subsequent full run supersedes it.
- `git diff --check` exited 1 because the pre-existing change in `apps/api/tests/test_course_content_quality.py:68` has a new blank line at EOF. This audit did not edit that test file. Existing LF/CRLF notices also appeared. The four new documents are checked separately for whitespace, references and completeness.

Not executed: `scripts/verify_launcher.py`, interactive browser journeys, complete offline/browser-network-denial tests, every lesson example, every prose answer, or full upstream licensing-chain verification. The launcher check would close the existing recorded runtime. Passing unit tests does not establish those unexecuted checks.

## 9. Release decision and immediate next step

Proceed incrementally. Phase 1 is solely preservation infrastructure plus explicit immutable content bindings and the diagnosed mapping fixes, with fresh/upgrade/idempotency tests. It does not change the confirmed curriculum, activate a product edition, rewrite mastery scores, remove historical AI rows, author new lessons, or implement the later planner/interview replacement. See the roadmap for exact files and acceptance criteria.
