# Forge

Forge is a local-first placement preparation app with static lessons, deterministic assessment, coding practice, FSRS review and interview rehearsal. Product Forge V1 (Placement Foundations) is independent of historical curriculum revisions 1 and 2.

The nine-subject, three-level scope contains 157 planned topics. It is an outline, not a complete taught syllabus or a claim of interview readiness. All new Placement Foundations teaching and scored pools remain unpublished until independent human review through the content-release workflow. Existing 53 legacy lessons and the historical Arena bank remain available with their original provenance and unverified editorial status.

## Learning and assessment

- Learn reads immutable, curriculum-scoped lesson revisions. Reading and study minutes never award mastery.
- Static help searches the local lesson corpus and links to exact revisions/sections. Legacy conversations remain readable; there is no conversational generation.
- Practice selects published static questions deterministically, preferring unused items. Repetition supports learning without repeated mastery credit. Historical course questions remain clearly labeled legacy practice.
- Single-choice and multi-select questions use immutable answer identities. Numeric responses use exact Decimal strings, explicit units and inclusive tolerance; arbitrary mathematical expressions are not evaluated.
- Python/SQL Run uses public samples in the existing browser Pyodide/PGlite workers. Submit sends source and exact revision identity to bounded local verification workers; arbitrary client scores/pass flags are never accepted as independently verified results. Hidden fixtures and references stay behind the backend.
- Python Submit supports a restricted standard-library subset with process/memory/instruction/output/time limits. Unsupported capabilities or unavailable workers return no verification and no mastery credit. SQL Submit uses Node.js and a fresh PGlite database for every dataset, never Forge SQLite.
- Transfer uses reviewed independent variants, excludes prior exposure/reveal families and preserves selection on resume. Recall requires FSRS due state and at least 24 elapsed hours after a clean transfer. Empty/exhausted approved pools are shown explicitly; there is no generation fallback.
- Practice is capped at 79, clean transfer at 89, and qualified delayed recall is needed for 90+. Weak recall can lower mastery. Coding tracks need independent coding evidence. New qualifying approved Arena solves contribute once; ambiguous old Arena events are preserved without inferred credit.
- Objective interviews snapshot static items, exact revisions, fixed competencies and weights. Feedback is deferred until completion. Communication/project rehearsal stores written reflection with authored rubrics/examples and no automatic correctness score or technical mastery credit. Historical model-era interviews/reports remain readable without fabricated continuation.

This is a personal local assessment system, not secure remote proctoring. Runtime provider imports, model settings, API-key requirements and model SDK dependencies have been removed. Phase 5 adds fixed timed subject/level/mixed/coding tests, saved drafts/deadlines, and a timezone-aware daily planner with 5/6/8-hour net targets. Plans preserve completed/skipped work and leave unavailable content unallocated. Tests never award technical mastery; detailed feedback waits until completion.

The current authoring batch contains nine lesson candidates and nine validated assessment pools, all awaiting independent human review. **148 of 157 planned topics remain unauthored; no new Placement Foundations content is published.** See the [implementation report](docs/forge-v1/PHASE5_IMPLEMENTATION_REPORT.md), [all-topic inventory](docs/forge-v1/FINAL_CONTENT_COVERAGE.md), [release checklist](docs/forge-v1/FINAL_RELEASE_CHECKLIST.md) and [limitations](docs/forge-v1/KNOWN_LIMITATIONS.md).

## Setup

Python and Node.js must already be installed. From `apps/api`, create/activate a virtual environment and install `requirements.txt`. From `apps/web`, run:

```powershell
npm ci
npm run build
```

From `apps/api`, start the local app:

```powershell
python -m uvicorn app.main:app --host 127.0.0.1 --port 18100
```

No model key or Google SDK is needed. SQL submission verification also needs the installed Node/PGlite files. On Windows, `Open Forge.bat` builds no assets: install dependencies and build first. `Close Forge.bat` stops only the verified owned process. Launchers use process creation time, executable, exact command digest, owner identity and a per-runtime mutex; unverified stale state is quarantined. An isolated runtime requires an explicit database path. Never point verification at your learner database.

Relative data/content settings in `apps/api/.env.example` are anchored to the repository. Startup applies numbered, checksum-verified migrations and backs up populated file databases before upgrades. Existing active curriculum selections are preserved. Do not delete the learner database or immutable snapshot store to upgrade.

## Curriculum and content

The curriculum page provides edition/subject/level navigation and an explicit Placement Foundations draft workflow. Create, edit, review, confirm and activate are separate actions. Confirmed graphs are immutable. Manual custom drafts require no model. Existing curricula and manual topic routes remain accessible.

The content registry distinguishes historical baselines from effective reviewed releases. Registration or structural validation is not editorial approval. New lessons, assessment bundles and Arena revisions use digest-bound validation, independent human review and exact confirmed-graph publication. See [publication workflow](data/content-approvals/README.md), [assessment pool contracts](data/assessment-pools/README.md), and [teaching checklist](docs/forge-v1/TEACHING_QUALITY_CHECKLIST.md).

No new question bank or lesson has been human-approved by this work. Review packets are in `data/content-approvals/phase5/review/`; validation is not editorial approval. Corrected Two Sum 1.0.1 remains awaiting independent review/publication. Legacy adaptation notices and provenance gaps remain facts, not silently reapproved originals.

## Verification

From `apps/api`, using disposable databases/snapshots:

```powershell
python -m pytest -q
python -m scripts.course_builder.validate --track python
python -m scripts.course_builder.validate --track sql-postgresql
python -m scripts.course_builder.validate --track dsa
python -m scripts.problem_builder.validate
```

From `apps/web`:

```powershell
npm test
npm run typecheck
npm run build
npm run validate:sql-problems
```

Tests prohibit external network connections and use synthetic approved items only inside isolated fixture databases. Keep real learner data out of destructive/migration tests. Runtime import/startup tests explicitly forbid provider/Google SDK imports. See the [Phase 4 implementation report](docs/forge-v1/PHASE4_IMPLEMENTATION_REPORT.md) for exact results and remaining limitations.

## Optional development authoring

Provider-assisted authoring is isolated under `apps/api/scripts/authoring`; its optional requirements are separate from the runtime install. Existing course/problem builder commands may be used deliberately in that development environment, but never publish automatically and never run during startup or ordinary learning. Validation/publication does not require the optional SDK. Retired provider-era implementation/tests are preserved as non-importable text under `apps/api/scripts/legacy_runtime` for reference, not runtime fallback.
