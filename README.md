# Forge

Forge is a local-first engineering interview-preparation system that builds, measures, and retains job-ready foundations through deterministic evidence.

## Interview-first core loop

```text
Learn → Guided Practice → Coding Arena → Mastery → Spaced Review → Mock Interview
```

The confirmed V2 default reflects 2026 job-search priorities. Python Programming and SQL + PostgreSQL are priority 100, DSA + Problem Solving is 98, Backend and practical CS follow, then LLM/RAG specialization, ML/production working knowledge, frontend basics, and ongoing interview communication. V1 remains in SQLite as curriculum history. An explicit migration map copies learner state only for unambiguous topics; historical evidence is never moved or rewritten.

### Coding Arena

Coding Arena is independent of course navigation and uses a canonical original problem bank under `content/problem-bank/{python,sql,dsa}`. The initial validated bank contains two problems per track. This deliberately small bank proves the architecture; the long-term target is 40 Python, 40 SQL, and 50 DSA problems after authored review.

Python and DSA problems reuse Monaco and the timeout-controlled Pyodide Web Worker. SQL problems use `@electric-sql/pglite` in a separate Web Worker. Every query run creates a fresh ephemeral PostgreSQL-compatible database from the problem fixture, so learner SQL cannot access Forge SQLite. SELECT results are compared deterministically by columns and normalized rows, with optional ordering and alternate hidden datasets. Gemini never grades runtime Python or SQL.

Solutions remain hidden until a successful submission or explicit Give Up. First successful solves append Arena mastery evidence to the mapped topic, with greater weight for medium problems and the existing assistance penalty for hints. Repeated success on the same problem does not create farmable evidence.

Problem-bank commands, run from `apps/api`:

```powershell
python -m scripts.problem_builder.validate
python -m scripts.problem_builder.validate --track sql
python -m scripts.problem_builder.build --track python --topic strings --difficulty easy --key python-example --dry-run
python -m scripts.problem_builder.build --track python --topic strings --difficulty easy --key python-example
python -m scripts.problem_builder.promote --track python --problem python-example
```

Validate actual SQL reference queries through PGlite from `apps/web`:

```powershell
npm run validate:sql-problems
```

Arena problems must be original Forge-authored tasks. Do not copy third-party challenge statements.

## Problem

Interview preparation often separates teaching, coding practice, spaced review, and mock interviews into unrelated tools. Activity is then mistaken for ability, while chat confidence and opaque AI judgements can inflate progress.

## Solution

Forge V1 combines a confirmed curriculum, contextual tutoring, deterministic coding practice, evidence-based mastery gates, FSRS review, an adaptive daily plan, and semi-structured mock interviews in one local application. Observable evidence remains authoritative; Gemini supplies validated teaching, question wording, and rubric-bound evaluation without controlling mastery, scheduling, curriculum structure, or interview weights.

### Static course content

Forge now separates course compilation from study. At build time, explicitly registered vetted sources are fetched conservatively, cached, extracted, synthesized into structured original Forge material, validated against a required-coverage contract, and written as a candidate. Existing accepted lessons are never overwritten without deliberate promotion.

```text
Vetted sources → Course Compiler → Gemini synthesis → Validation → Static Course Pack

Static Course Pack
├── Learn Course (offline, no Gemini)
├── AI Tutor (grounded on the same lesson)
├── Forge Doubts (current section + local FTS5 search)
└── Static Practice Bank
```

The canonical pack is under `content/ai-engineer/v1`; SQLite stores synchronized metadata, exercise rows, local search, and reading progress. Reading progress is not mastery evidence. Python “Syntax and data types” is included as the deterministic fixture-backed accepted sample, including Boolean coverage and eight offline exercises. Complete required-coverage specifications exist for all 18 Python topics; the remaining topics require reviewed official-source fetching and build-time synthesis rather than fabricated research.

Course builder commands (run from `apps/api` with its environment active):

```powershell
python -m scripts.course_builder.build --track python --topic syntax-data-types --dry-run
python -m scripts.course_builder.build --track python --dry-run
python -m scripts.course_builder.validate --track python --topic syntax-data-types
python -m scripts.course_builder.validate --track python
python -m scripts.course_builder.promote --track python --topic <topic-slug>
```

The non-dry build deliberately stops unless source snapshots and Gemini are configured, and still requires a reviewed topic URL plan. Runtime never crawls or browses the web.

## Philosophy

- Learning evidence matters more than activity. Chat usage never changes mastery.
- Recommendations guide; they never prevent you from choosing any subject or topic.
- A confirmed curriculum is authoritative and cannot be silently rewritten by AI.
- Forge V1 stays small: one React client, one FastAPI app, and one local SQLite database.
- Deterministic tests are the primary judge of coding correctness.
- Gemini proposes and teaches; it never silently changes confirmed curriculum or mastery.

## Architecture

```text
React + TypeScript + Vite
            | HTTP/JSON
            v
         FastAPI
            v
         Services ------> LLMProvider ------> Gemini
            v
         SQLModel
            v
          SQLite
```

See [ARCHITECTURE.md](ARCHITECTURE.md) for service boundaries and future integration points.

## Prerequisites

- Windows 10 or 11
- Python 3.12 or newer
- Node.js 20 or newer and npm
- Git

## Windows setup

From PowerShell in the repository root:

### Backend

```powershell
cd apps\api
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
uvicorn app.main:app --reload
```

If PowerShell blocks activation, run this once in the current shell and activate again:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

The API runs at `http://127.0.0.1:8000`; interactive docs are at `http://127.0.0.1:8000/docs`. The database and default curriculum are created on first startup. Seeding is idempotent.

### Gemini setup

1. Obtain a Gemini API key from [Google AI Studio](https://aistudio.google.com/app/apikey).
2. Copy `apps/api/.env.example` to `apps/api/.env`.
3. Set `GEMINI_API_KEY` in `.env` and keep the file local.
4. Start or restart the backend, then start the frontend.
5. Open Settings and verify `Configured: Yes`.

```dotenv
GEMINI_API_KEY=replace-with-your-api-key
GEMINI_MODEL=gemini-3.8-flash
GEMINI_TUTOR_THINKING=low
GEMINI_DOUBT_THINKING=low
GEMINI_CURRICULUM_THINKING=medium
GEMINI_EXERCISE_THINKING=low
GEMINI_ANSWER_EVALUATION_THINKING=low
GEMINI_INTERVIEW_THINKING=low
GEMINI_INTERVIEW_EVALUATION_THINKING=medium
GEMINI_INPUT_PRICE_PER_MILLION=0.75
GEMINI_OUTPUT_PRICE_PER_MILLION=3.75
GEMINI_CACHED_INPUT_PRICE_PER_MILLION=0.075
```

Low thinking is used for tutoring, doubts, practice generation, and short-answer evaluation; medium is used for curriculum generation and its single repair attempt. Pricing values are configurable estimates, not authoritative Google billing, and must be updated when Google changes its rates.

### Frontend

Open a second PowerShell window in the repository root:

```powershell
cd apps\web
npm install
npm run dev
```

Open `http://localhost:5173`. Vite proxies local API calls to port 8000.

### Tests and build

```powershell
cd apps\api
.\.venv\Scripts\Activate.ps1
pytest -q

cd ..\web
npm run typecheck
npm run build
```

## Repository structure

```text
data/                         Versioned default curriculum and project profiles
apps/api/app/                 FastAPI application
apps/api/app/models/          SQLModel persistence entities
apps/api/app/schemas/         Request and response contracts
apps/api/app/routers/         HTTP endpoints
apps/api/app/services/        Seeding, catalog, dashboard, recommendations
apps/api/app/providers/       LLM abstraction and Gemini implementation
apps/api/scripts/             Optional manual Gemini smoke test
apps/api/tests/               Backend tests
apps/web/src/components/      Shared layout and UI components
apps/web/src/pages/           Route-level screens
apps/web/src/services/        Typed API client
apps/web/src/types/           Frontend API types
```

## Features

- Ten-track, 160-topic AI engineering curriculum with explicit prerequisites
- Idempotent startup seeding into SQLite
- Persistent learner topic state and future-ready domain tables
- Health, curriculum, track, topic, topic-state, and dashboard APIs
- Deterministic priority/mastery/prerequisite-aware recommendations
- Dashboard, expandable curriculum, and topic detail screens
- Manual access to every subject and topic
- Contextual Gemini doubt chat that never affects mastery
- Gemini 3.8 Flash tutoring through the official `google-genai` Interactions API
- Structured tutor turns and validated custom curriculum proposals
- Contextual doubt chat with compact conversation history
- Editable custom curriculum proposal, draft, confirmation, and activation workflow
- Active-curriculum dashboard aggregation and switching
- Safe AI status plus monthly token and estimated-cost tracking
- Friendly operation without a Gemini key and fake-provider automated tests
- Three-exercise Practice packs that reuse cached exercises and generate only missing ones
- Multiple choice, rubric-graded short answer, Python coding, and Python debugging exercises
- Monaco Python editor with a Pyodide module worker, visible sample runs, hidden submission tests, timeout recovery, hints, and attempt history
- Deterministic evidence weighting, hint penalties, confidence labels, and explicit 79/89 mastery gates
- Clean transfer checks and delayed-recall evidence, with assisted transfers excluded from advancement
- FSRS 6 review scheduling, deterministic score-to-rating mapping, due/upcoming queues, and review sessions
- Persistent daily plans with due reviews, recurring mistakes, DSA minimums, priorities, reasons, and skip/complete controls
- Priority-weighted track and curriculum readiness with coverage and high-priority gap explanations
- Seven deterministic interview blueprints: Quick, Full AI Engineer, Python/Backend, LLM/RAG, Project Deep Dive, System Design Basics, and Behavioral
- Bounded contextual follow-ups, reusable live coding, fixed-rubric scoring, topic-linked reports, saved sessions, and interview history
- Grounded Robin and Cognitive Memory Engine project profiles
- Configurable monthly Gemini cost estimate with warning thresholds and an optional nonessential-generation pause

Custom curriculum generation never writes directly to the active curriculum. The user must save a draft, review/edit it, explicitly confirm it, and separately activate it. Confirmed curricula cannot be structurally edited in Phase 2.

### Practice

Open any topic and choose **Practice**. Forge reuses suitable cached exercises and asks Gemini for a small structured pack only when needed. A coding exercise's generated reference is checked against its tests before use; invalid exercises are retired. Without a Gemini key, existing cached exercises remain usable. With no cache, Practice shows a configuration/unavailable message. Settings usage totals include practice generation and short-answer evaluation.

**Run** executes only visible sample tests and saves no scored attempt. **Submit** executes all coding tests and saves an attempt with score, feedback, submitted code, hint count, and grading source. MCQs are graded deterministically by the backend. Gemini evaluates short answers against a fixed rubric, and unavailable evaluation is saved as pending without a fabricated score. Completed attempts become immutable evidence; pending evaluations do not affect mastery.

Learner Python runs in a Pyodide module Web Worker, not on the React UI thread. A long-running worker is terminated at the exercise time limit (about five seconds by default), and the next run starts a new worker. Pyodide 314.0.7 is installed from npm and its core files are served locally by Vite, so execution does not depend on a runtime CDN. Monaco comes from npm packages `@monaco-editor/react` and `monaco-editor`. No new Python dependency is required.

Forge V1 is a local personal app. Browser-side execution is **not** a secure production sandbox, and submission tests are not truly secret from a technical user. A future public version would need hardened server-side code execution and revalidation. No arbitrary package installation is available in Practice.

### Manual Practice verification without Gemini

Use a separate disposable database; these commands never target the normal `forge.db`. In the API directory, set `FORGE_DATABASE_URL` to a path ending in `forge-practice-smoke.db`, then run `python -m scripts.manual_practice_fixture`. Start `uvicorn app.main:app --port 8001` in that shell. In the web directory, set `FORGE_API_PROXY_TARGET=http://127.0.0.1:8001` and run `npm run dev -- --port 5174`. The fixture prints its Python topic ID.

Open that topic on port 5174 and check: Practice is active; reveal a hint and submit the MCQ; submit the short answer (it should remain pending without Gemini); open the coding exercise and confirm Monaco loads; Run the starter code to see a failing sample; replace it with `def add(a, b): return a + b` on two correctly indented lines and Run, then Submit; finish the pack and check attempt history and the deterministic mastery breakdown on the topic page. To verify worker behavior before submitting, Run `print("hello forge")` with the required function and confirm stdout, Run syntax-invalid code and confirm a traceback, Run `while True: pass` on two lines and confirm a roughly five-second timeout, then Run `print(2 + 2)` with the function and confirm output `4`. The next run after timeout must succeed.

### Mastery, transfer, review, and planning

Mastery is calculated on the backend from the latest eight practice events. Multiple choice, short answer, and code/debug evidence have weights of 0.6, 0.8, and 1.0; hints reduce the event contribution. Practice alone is capped at 79. A clean, unassisted transfer result is required to reach 80–89, and a successful recall at least 24 hours later is required to reach 90–100. Tutor and doubt chat never create evidence or change mastery; asking for doubt help during an open transfer marks that transfer assisted.

Review scheduling uses `fsrs` 6 with a stored, versioned card payload. Forge converts scores deterministically: below 50 = Again, 50–69 = Hard, 70–89 = Good, and 90–100 = Easy; assisted evidence cannot rate above Good. The desired-retention setting applies to future scheduling decisions. The Review screen exposes due and upcoming work, and reuses validated exercises before asking Gemini for one targeted item.

The daily planner persists one plan per date. It schedules due review first, then recurring mistakes, the DSA minimum, transfer-ready/high-priority work, and other developing topics until the time target is reached. Every recommendation includes a reason. Skipping an item never removes manual access to any subject or topic.

Readiness is a priority-weighted learning summary, not an employment or interview-success probability. It reports ready/strong coverage and names the largest high-priority gaps.

### Mock interviews

Interview mode is assessment rather than tutoring. Each mode expands a code-controlled blueprint of required competencies, question types, section weights, and expected duration. Gemini phrases one question at a time using structured output. It may request at most one non-leading contextual follow-up. Free-form answers are evaluated against immutable dimension weights; Python coding and debugging reuse Monaco, the Pyodide worker, and deterministic tests without hints.

Detailed feedback stays hidden until completion. The final **Forge Interview Score** is a rubric score—not a hiring probability—and includes section results, strengths, priority gaps, communication feedback, and curriculum-topic links. Behavioral responses never affect technical mastery. Interview coding is saved as assessment history but does not directly rewrite topic mastery.

Project Deep Dive questions are grounded in the versioned profiles in `data/default-projects.json`. They cannot redefine a project or add unsupported claims. Active interviews disable Tutor and Forge Doubts through backend enforcement. A generation failure after an answer does not lose the response; the next question can be retried. Interviews can also be saved and resumed or explicitly abandoned.

### Gemini usage and budget guardrails

Settings displays successful calls, input/output/thinking/cached tokens, and estimated USD cost. The configurable monthly budget is a user-side estimate, not Google billing. Warning levels begin at 75%, 90%, and 100%. An optional switch can pause nonessential fresh practice/review generation at the estimated limit while cached material remains usable; it is off by default and does not silently block explicitly requested assessment or tutoring work.

### Manual Phase 4 verification without waiting 24 hours

Use a disposable database from `apps/api`: set `FORGE_DATABASE_URL` to a path ending in `forge-phase4-smoke.db`, then run `python -m scripts.manual_phase4_fixture`. Start the API on port 8001. Start the web app with `FORGE_API_PROXY_TARGET=http://127.0.0.1:8001` on port 5174. The fixture prints one transfer-ready topic and one due-review topic, using synthetic timestamps without weakening production rules. Verify the dashboard reasons, the 79 practice cap, an unassisted transfer advancing only to 89, the due review and next FSRS date, planner settings, and unrestricted Curriculum browsing. Automated tests cover the 24-hour delayed-recall unlock and later mastery decrease.

### Optional one-call Gemini smoke test

This command makes one paid API request and is never run by pytest:

```powershell
cd apps\api
.\.venv\Scripts\Activate.ps1
python scripts\gemini_smoke.py
```

It prints success, model, reply, and available token counts without printing the API key.

## Final V1 manual verification

Use a disposable database for destructive testing. Run the Phase 3 practice fixture and Phase 4 synthetic-time fixture as described above, then start both apps on the alternate ports. Verify, in order:

1. Open Dashboard, inspect today’s reasons, and manually choose a different topic.
2. Open Learn, ask a contextual doubt, and confirm neither action changes mastery.
3. Complete MCQ, short-answer, and Python Practice; test successful execution, syntax errors, timeout recovery, and a post-timeout run.
4. Inspect the mastery explanation, pass the fixture transfer without hints, and confirm the 89 cap plus future review.
5. Complete the due review and inspect the FSRS next date and planner update.
6. Open Interview and inspect all seven modes. With Gemini configured, start Quick Mock, answer a free-form question, complete a contextual follow-up when requested, solve coding without hints, and finish the report.
7. Follow a recommended weak-topic link, return to Interview history, save/resume another interview, and explicitly abandon it.
8. Create, edit, confirm, and activate a disposable custom curriculum; switch back to the default and verify prior state remains intact.
9. Inspect usage and automated budget-threshold tests; optionally set a very small disposable budget and enable the nonessential pause.
10. Restart backend and frontend, then verify plans, mastery, reviews, interviews, reports, settings, and active curriculum persist.

Automated tests use fake providers and deterministic clocks, so no live Gemini call or 24-hour wait is required.

## Privacy and local-first behavior

Curricula, answers, progress, interview history, and settings live in local SQLite. The Gemini key remains in the backend environment and is never sent to the browser. Content sent to Gemini is limited to the context needed for the requested tutoring, generation, or evaluation operation.

## Known limitations

- Forge V1 is a personal, local-first application with no accounts or multi-user isolation.
- Browser-side Python tests are appropriate for learning but not secure competitive assessment.
- LLM evaluation can be imperfect even with fixed rubrics and structured validation.
- Forge Interview Score reflects Forge’s rubric, not employer judgement or hiring probability.
- There is no production cloud deployment, authentication layer, or hardened server-side code sandbox.
- Forge has not undergone an empirical learning-outcome study.

## Resume-ready project summary

- Built a local-first adaptive AI tutoring platform using React, TypeScript, FastAPI, SQLModel, SQLite, and Gemini.
- Designed deterministic evidence-based mastery tracking with hint weighting, transfer verification, delayed recall, and FSRS spaced repetition.
- Built browser-isolated Python practice and interview coding with Monaco, Pyodide Web Workers, timeout recovery, and deterministic test grading.
- Implemented structured LLM tutoring, immutable custom curricula, adaptive daily planning, and semi-structured mock interviews with fixed rubrics and token/cost visibility.

## Future work

Forge V1’s product scope is frozen. No Phase 6 is planned in this repository; the next step is to use Forge for interview preparation, collect real study experience, and fix only evidence-backed reliability issues. No unsupported scale or learning-outcome claims are made.
