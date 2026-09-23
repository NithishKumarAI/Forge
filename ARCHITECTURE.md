# Forge architecture

```text
User
 │
 ▼
React / Vite
 │
 ├── Learn
 ├── Practice
 ├── Review
 ├── Interview
 └── Planner
 │
 ▼
FastAPI
 │
 ├── CurriculumService
 ├── TutorService
 ├── PracticeService
 ├── MasteryService
 ├── ReviewService
 ├── PlannerService
 └── InterviewService
 │
 ├────────────────────► Gemini 3.8 Flash
 │
 ▼
SQLite

Coding:
Monaco → Pyodide module Worker → deterministic tests
```

Forge remains a local-first modular monolith. Routers own HTTP concerns, services own product rules, SQLModel owns persistence, and the React client receives typed JSON. The Gemini API key exists only in the backend process.

## Authority boundaries

The backend is the source of truth for curricula, learner state, sessions, chat history, active-curriculum selection, and usage records. Gemini supplies explanations, feedback, questions, and proposed curricula; its output is always validated before it can become application state.

A custom curriculum moves through `proposal → draft → confirmed → active`. Generation does not write a draft. Confirmation is explicit, and confirmed structures are immutable. Activation is separate and accepts confirmed curricula only.

Tutor and doubt conversations reuse `LearningSession` and `ChatMessage`. Only the latest ten relevant messages are sent with minimal topic context. Neither conversation path creates mastery evidence. A doubt opened during an unfinished transfer marks that check assisted, so it cannot unlock the transfer gate.

## Phase 2 services

- `active_curriculum`: resolves and changes the confirmed active curriculum using `AppSetting`.
- `custom_curriculum`: persists, validates, confirms, and protects curriculum structures.
- `curriculum_generation`: prompts Gemini for validated `CurriculumProposal` output and performs one repair attempt.
- `tutor`: applies the central teaching policy and owns Learn-mode sessions.
- `doubt`: answers short contextual questions without affecting mastery.
- `usage`: records provider token metadata and configurable cost estimates.
- `GeminiProvider`: implements the small `LLMProvider` interface with the official Interactions API.

## Phase 3 practice

```text
PracticePage → Monaco editor → PythonRunner → module Web Worker → Pyodide
       |              Run: sample tests only          |
       |              Submit: all tests              |
       v                                             v
FastAPI practice router → practice service → Exercise / LearningSession / Attempt
                              ├─ structured Gemini generation and rubric evaluation
                              └─ deterministic MCQ and code-test scoring
```

The practice service owns exercise selection, caching, structured validation, session packs, hints, submissions, and history. It reuses `LearningSession` (`mode=practice`), `Attempt`, `LLMProvider`, and `ModelUsageEvent`. The router owns HTTP validation and does not execute learner code. MCQ correctness is server-side and deterministic; Python results are calculated from tests in the browser worker and recorded as `grading_source=client_pyodide`. Short answers use a fixed stored rubric and a validated structured Gemini response; unavailable evaluation is saved as pending rather than given a fabricated score. Completed submissions append evidence and trigger deterministic recalculation.

Schema additions are additive tables: `exercise` holds type-specific JSON and validation state; `practicesessionexercise` fixes pack order; `exerciseattemptdetail` adds answer, execution summary, hints, feedback, and grading provenance to existing `attempt`; `practicehintuse` counts revealed hints. Existing tables and database files are not dropped or rebuilt. SQLModel creates only missing tables at startup.

Generated coding references begin `pending`. On first use, the browser executes the reference against all tests and reports the outcome; failed references become inactive. The normal exercise response excludes solutions, MCQ answers, rubrics, and hidden tests. The reference-validation and submission-test endpoints necessarily deliver coding test data to the local client. This is suitable for a personal local app, not secure hidden testing or a hardened untrusted-code sandbox. A public product would need server-side sandboxed revalidation.

The worker keeps Python off the UI thread, gives each run a fresh logical namespace, and is terminated after the configured timeout. A subsequent run creates a fresh worker. No arbitrary package installation is supported. `Run` executes visible samples without an attempt; `Submit` executes all tests and records evidence.

## Phase 4 adaptation loop

```text
completed attempt
      v
MasteryEvidenceEvent --deterministic weights/hint penalty--> LearnerTopicState
      |                                                       |
      +--> TransferCheck (clean and unassisted) -- gate 79 ----+
      +--> delayed ReviewEvent (>=24h) ----------- gate 89 ----+
      +--> Mistake recurrence                                  |
      v                                                       v
ReviewState + FSRS card                               readiness + daily plan
```

`mastery` is the sole authority for evidence interpretation. It backfills legacy completed attempts idempotently, uses the latest eight practice events, calculates confidence, enforces practice/transfer/recall caps, and creates a review state only after meaningful evidence. Transfer and recall are distinct event types, so ordinary practice cannot impersonate either gate. The transfer service generates exactly one unseen structured exercise and allows one schema-repair attempt; the review service maps score to an FSRS rating deterministically and stores a versioned FSRS card JSON wrapper.

`planner` builds and persists a dated plan from the active confirmed curriculum. `readiness` aggregates topic mastery by curriculum priority and returns coverage plus named gaps. Dashboard, recommendation, and catalog services consume those shared calculations rather than inventing separate mastery rules. AI may generate an exercise or grade a rubric-bound short answer, but it never assigns mastery, confidence, readiness, priority, or review intervals.

Phase 4 adds `masteryevidenceevent`, `transfercheck`, `reviewevent`, and `dailyplanitem`. Existing `reviewstate`, `attempt`, and learner-state rows remain in place; startup creates missing tables and idempotently interprets historical completed attempts. FSRS card payloads include `fsrs_schema_version` so a future scheduler migration can be explicit.

## Phase 5 interview assessment

```text
fixed InterviewBlueprint
          │
          ▼
validated question wording ─────► one bounded contextual follow-up
          │
          ▼
fixed rubric / deterministic code tests
          │
          ▼
InterviewResponse → weighted Forge Interview Score → topic-linked report
```

Blueprints are code-controlled data: mode, competency order, allowed question types, duration guidance, and section weights cannot be changed by Gemini. Question generation receives exactly one blueprint slot plus relevant learner/topic context. Project questions additionally receive one immutable profile from `default-projects.json`. Generated Pydantic output receives at most one repair attempt.

Free-form evaluation returns scores for exactly the dimension names in the stored rubric; the backend applies the immutable weights. Coding questions create an `Exercise` plus `LearningSession(mode=interview)` and reuse Phase 3 submission grading with no hints. Interview evidence is intentionally excluded from automatic mastery recalculation in V1. Behavioral responses can only affect their interview section.

`InterviewSession`, `InterviewQuestion`, `InterviewResponse`, and `InterviewReport` are additive tables. Sessions may be active, saved, completed, abandoned, or generation-failed. Completed responses are committed before the next question is generated, so provider failure cannot erase an answer; `/next` safely retries preparation. Tutor and doubt routers reject requests while a scored interview is active.

## Static course architecture

Authority is one-way:

1. confirmed curriculum;
2. versioned course coverage specification;
3. accepted static course lesson and exercise bank;
4. runtime AI.

Runtime AI may explain levels 1–3 but cannot redefine them.

Course build time: explicit vetted source URLs → conservative cached fetch → text extraction → Gemini structured synthesis → schema, coverage, source, structure, duplicate, and Python syntax validation → candidate file → deliberate promotion.

Runtime: the disk course pack is canonical. Startup synchronizes lesson metadata and `source="course_pack"` exercises into SQLite and rebuilds a local FTS5 section index. Learn reads the pack directly; Tutor receives the selected authoritative section and deterministic outline; Doubts receives the current section plus a small FTS result set. `LessonSectionProgress` is deliberately separate from mastery evidence.

## Interview-first curriculum V2

The prior confirmed curriculum is retained. V2 is seeded as a separate confirmed version and becomes active when the prior default was active. `data/curriculum-migrations/v1-to-v2.json` records unambiguous topic mappings. Only learner-state summaries are copied into untouched V2 states; attempts and mastery evidence remain permanently associated with their original topic IDs.

Priority tiers are code/data controlled: P0 Python, SQL/PostgreSQL, and DSA; P1 Backend, CS, LLM, and RAG; P2 ML and Production; P3 Frontend; Interview Engineering is ongoing. Planner target settings reserve configurable Python, SQL, and DSA practice before lower-priority recommendations.

## Coding Arena

```text
Versioned static problem file
        ↓ startup sync
ArenaProblem metadata ─── ArenaAttempt / ArenaHintUse
        ↓
Python or DSA → Monaco → Pyodide worker → deterministic tests
SQL           → Monaco → PGlite worker → fresh fixture DB → deterministic result comparison
        ↓ first non-farmable pass
MasteryEvidenceEvent(event_type="arena") → central mastery recalculation
```

Problem statements, fixtures, tests, explanations, and solutions are canonical disk content. SQLite is only the synchronized index and attempt history. Public problem responses remove reference solutions and hidden validation. Giving up reveals the solution but creates no mastery evidence. Every SQL execution constructs and discards an isolated PGlite database; Forge application data is never attached.

Build-time problem tools create candidates, validate schemas and Python references, and require explicit promotion. A Node/PGlite validator executes accepted SQL reference solutions against sample and hidden datasets. Runtime Gemini does not generate or grade normal Arena work.

The final report’s overall score is calculated from blueprint weights before Gemini may add a validated narrative. Reports always identify the result as a Forge rubric score and explicitly reject hiring-probability interpretation.

## Usage guardrails

Every successful provider response becomes a `ModelUsageEvent`. `AppSetting` stores the estimated monthly budget and optional nonessential-generation pause. Threshold messages are deterministic. The estimate never claims to be authoritative billing, and quota errors are handled generically without hard-coded Gemini tier assumptions.
