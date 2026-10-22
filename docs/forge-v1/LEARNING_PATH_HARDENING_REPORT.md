# Forge V1 — Learning-First Hardening & Audit Verification Report

**Author**: Antigravity Assistant & Engineering Pair  
**Date**: October 22, 2026  
**Status**: Complete, Verified & Hardened  
**Authoritative Local Tree**: `C:\My PC\git\Forge`  
**Classification**: Beginner Python/SQL/DSA path verified and hardened; remaining tracks documented honestly  

---

## 1. Executive Summary

This audit and hardening pass inspected and resolved all confirmed defects and security/integrity risks in the Forge learning-first redesign:

1. **Deterministic Bounded Verification**:
   - Replaced in-process `exec()` of arbitrary Python learner code with the bounded isolated execution system (`sys.executable -I -S WORKERS/python_worker.py`).
   - Replaced heuristic SQL string checks (`startswith("SELECT")`) with isolated PostgreSQL verification via `@electric-sql/pglite` and `sql_worker.mjs`.
2. **Real URL Resolution & Truthful Availability**:
   - Resolved all Continue Learning recommendations and concept step links to valid, real routes (`/arena/exercises/:key`, `/arena/problems/:key`, `/topics/:id/learn`, `/topics/:id`, `/curriculum`, `/review`, `/practice`).
   - Eradicated all broken fictional routes (such as `/learn/...`).
   - Truthfully classified unreviewed candidate lessons as `"candidate_unreviewed"`; never described unpublished material as `"available"`.
3. **Evidence-Based Concept Readiness**:
   - Stripped the ability of client state calls (`POST /api/learning-path/steps/:key/progress`) to establish completion or readiness without underlying evidence.
   - Required completion of 100% of authored guided exercises plus a verified passing `ArenaAttempt` on an independent problem before deriving `ready_to_advance`.
4. **Arena Stage Hierarchy & Prerequisite Hardening**:
   - Re-classified all 110 Arena problems across the 5 progression stages (`First Steps`, `Beginner`, `Developing`, `Intermediate`, `Challenging`) according to genuine prerequisite complexity.
   - Advanced algorithmic patterns (trees, BFS, prefix sums, hash bijections) were moved from beginner categories into Developing/Intermediate/Challenging.
5. **Exact Count Reconciliation**:
   - Reconciled all stage and topic counts across JSON manifests and markdown reports: 9 subjects, 157 syllabus topics, 25 concept steps, 14 First Steps beginner exercises, and 110 Arena problems.
6. **Full Suite & Real Browser Verification**:
   - Backend: 295 passed, 0 failed in 501s (`pytest`).
   - Frontend: 13 passed (13 test files), 54 passed (54 tests) (`vitest`).
   - Frontend production build: completed cleanly in 4.71s (`tsc -b && vite build`).
   - Real Browser Journey: 100% passed in Playwright Chromium with network denial against a disposable database.

---

## 2. Confirmed Issue Resolutions

### Issue 1: Beginner SQL Submissions Executed via Isolated PGlite System

- **Previous Defect**: Submissions were heuristically awarded 100% simply if the query began with `SELECT` or `WITH`, without verifying columns, rows, or database constraints.
- **Hardening Applied**:
  - Integrated `evaluate_beginner_exercise` in `apps/api/app/services/learning_path.py` with `app.services.assessment_judge.judge`.
  - Submissions are evaluated by the isolated worker `apps/api/app/workers/sql_worker.mjs` against `@electric-sql/pglite` inside an ephemeral, disposable database.
  - Queries must match exact expected column contracts, row values, and ordering rules. Syntax errors or mismatched rows fail with score `0.0`.
- **Regression Tests**:
  - `test_beginner_exercise_sql_incorrect_syntax_and_values`: Syntax error fails, column mismatch fails, wrong values fail, and valid queries succeed.

### Issue 2: Beginner Python/DSA Submissions Executed via Bounded Verifier

- **Previous Defect**: Submissions were executed in-process using Python's `compile()` and `exec()`, risking resource exhaustion and unbounded execution.
- **Hardening Applied**:
  - Removed `execute_python_beginner_test` entirely.
  - Submissions are evaluated via `app.services.assessment_judge.judge`, which spawns `sys.executable -I -S apps/api/app/workers/python_worker.py` with AST checks, restricted builtins, and a 5-second process timeout.
  - Infinite loops (`while True: pass`) time out safely and return `score: 0.0, passed: False`.
  - Disallowed built-ins (such as `open()`, `eval()`, `exec()`, `breakpoint()`) are caught and blocked during AST inspection.
- **Regression Tests**:
  - `test_beginner_exercise_python_infinite_loop_and_banned_builtins`: Infinite loop terminates and scores 0.0; banned built-ins fail closed.

### Issue 3: Truthful Recommendation URLs & Candidate Content Resolution

- **Previous Defect**: Early iterations linked recommendations to fictional routes (`/learn/step-...`), and candidate lessons were unconditionally assumed to be available.
- **Hardening Applied**:
  - `derive_step_action(session, concept, state)` inspects actual database-bound lessons via `bound_lessons(session, topic_row)` and manifests.
  - Only real, valid application routes are returned:
    - `/arena/exercises/:key` (for beginner guided exercises)
    - `/arena/problems/:key` (for independent practice)
    - `/topics/:id/learn` (when approved/bound lessons exist)
    - `/topics/:id` (topic syllabus overview)
    - `/curriculum?track=:key` (curriculum track overview)
    - `/review` (spaced repetition review)
    - `/practice` (active assessment session)
  - `ConceptStepDetail.availability_status` dynamically checks content resolution: if a topic has no bound lesson and no beginner exercises, it resolves to `"candidate_unreviewed"`, never claiming unreviewed candidates are `"available"`.
  - Recommendation priorities 3, 4, and 6 only select steps where `has_usable == True`.
- **Regression Tests**:
  - `test_recommendation_urls_are_resolvable`: Verifies all 9 subjects produce valid URLs with approved route prefixes.
  - `test_unpublished_candidate_lessons_not_claimed_available`: Verifies steps without approved lessons or exercises return `"candidate_unreviewed"`.

### Issue 4: Evidence-Based Concept Completion & False Readiness Prevention

- **Previous Defect**: Client could submit `POST /api/learning-path/steps/:key/progress?state=ready_to_advance` and fabricate completion without solving exercises.
- **Hardening Applied**:
  - `get_concept_step_progress` strictly computes state from verified database evidence:
    - `ready_to_advance`: requires all `guided_practice_refs` solved in `AppSetting` (`lp_ex_solved:<key>`) AND a passing `ArenaAttempt` on at least one `independent_practice_refs`.
    - `practising`: partial guided exercises solved or arena attempts recorded.
    - `learning`: reading progress in `ContentSectionProgress` or bookmarked intent.
    - `review_due`: expired FSRS schedule (`ReviewState.due_at <= now`).
  - `set_concept_step_progress` raises `ValueError` if client requests `ready_to_advance` or `retained` without satisfying the prerequisite evidence.
  - Router maps `ValueError` to HTTP 400 Bad Request.
- **Regression Tests**:
  - `test_false_readiness_prevented_without_verified_evidence`: Client is blocked from advancing; once guided exercises and independent arena attempts are verified, readiness is granted.
  - `test_prerequisite_violations_prevent_advancing`: Dependent concepts cannot advance while prerequisites remain incomplete; priority tier 3 elevates missing prerequisites.

### Issue 5: Arena Stage Difficulty Review (110 Problems)

- **Previous Defect**: Initial problem mapping classified advanced algorithmic challenges (such as BFS graph traversals or prefix sums) into beginner categories.
- **Hardening Applied**:
  - Re-mapped all 110 problems across 5 stages based on required reasoning steps, input/output complexity, algorithmic complexity, and prerequisites.
  - Generated authoritative `data/learning-path/arena-stages.json`:
    - **First Steps** (18 problems): Elementary I/O, simple scalar logic, constant queries, basic array scans.
    - **Beginner** (20 problems): Clean function contracts, basic math, simple conditionals, single-table SQL filters, linear search.
    - **Developing** (28 problems): Two pointers, basic sliding window, simple joins, group-by aggregations, basic recursion.
    - **Intermediate** (23 problems): Stacks/queues, BSTs, subqueries, CTEs, dynamic programming fundamentals.
    - **Challenging** (21 problems): Graphs, topological sort, complex DP, window functions, advanced tree operations.
- **Regression Tests**:
  - `test_arena_stages_manifest_integrity`: Validates 5 stages, 110 total mappings, and zero unmapped or orphaned problems.

### Issue 6: Reconciled Counts in Documentation & Reports

- **Previous Defect**: Inconsistencies existed between `placement-foundations-scope.json`, `arena-stages.json`, and markdown documentation tables.
- **Hardening Applied**:
  - Synchronized `BEGINNER_EXERCISE_COVERAGE.md` and `LEARNING_CONTENT_REVIEW_QUEUE.md` with authoritative counts:
    - **Placement Foundations Syllabus**: Exactly 157 topics across 9 subjects:
      - Python Programming: 21 topics
      - SQL and PostgreSQL: 18 topics
      - Data Structures & Algorithms: 19 topics
      - Quantitative Aptitude: 18 topics
      - Logical Reasoning: 15 topics
      - Verbal Ability & Communication: 17 topics
      - System Design Fundamentals: 15 topics
      - AI Fundamentals: 19 topics
      - Interview Communication: 15 topics
    - **Arena 5-Stage Breakdown**: Exactly 110 problems:
      - Python: 40 problems (9 First Steps, 10 Beginner, 10 Developing, 6 Intermediate, 5 Challenging)
      - SQL: 30 problems (6 First Steps, 6 Beginner, 5 Developing, 7 Intermediate, 6 Challenging)
      - DSA: 40 problems (3 First Steps, 4 Beginner, 13 Developing, 10 Intermediate, 10 Challenging)
    - **Concept Steps**: Exactly 25 steps defined in `data/learning-path/concept-steps.json`.
    - **First Steps Beginner Exercises**: Exactly 14 authored interactive exercises in `data/learning-path/beginner-exercises.json` (7 Python, 4 SQL, 3 DSA).

---

## 3. Comprehensive Verification Matrix

| Verification Tier | Command / Harness | Result | Notes |
| :--- | :--- | :---: | :--- |
| **Backend Learning Path Tests** | `pytest apps/api/tests/test_learning_path.py` | **17 / 17 PASSED** | Includes all 6 audit regression tests. |
| **Full Backend Pytest Suite** | `pytest apps/api/tests -q` | **295 / 295 PASSED** | Zero regressions across all historical tests; run duration: 501s. |
| **Frontend TypeScript Typecheck** | `npm --prefix apps/web run typecheck` | **PASSED (0 errors)** | Full `tsc -b` validation across all components and hooks. |
| **Frontend Vitest Unit Suite** | `npm --prefix apps/web test -- --run` | **54 / 54 PASSED** | 13 test files passed; PGlite isolation & navigation verified. |
| **Frontend Production Build** | `npm --prefix apps/web run build` | **PASSED (0 errors)** | Production bundle built in 4.71s with zero bundle errors. |
| **Real Browser Learning Journey** | `scripts/run_learning_path_browser_journey.py` | **100% PASSED** | Playwright Chromium on network-denied loopback with disposable DB. |

### Real Browser Journey Checkpoints Passed:
1. `Step 1`: Opened dashboard (`/`); confirmed "Welcome back to Forge." hero header.
2. `Step 2`: Confirmed zero legacy manual planner controls (no "Today's study plan", no 5/6/8-hour buttons, no unallocated minute alerts).
3. `Step 3`: Verified Continue Learning hero card displays concept and links directly to beginner exercise.
4. `Step 4`: Verified Focus Subject switcher instantly updates recommendations without route reloads.
5. `Step 5`: Solved Python beginner exercise (`py-first-print-message`) via Monaco editor; verified isolated worker execution and 100% pass score.
6. `Step 6`: Navigated to `/arena`; verified all 5 exercise stages (`First Steps`, `Beginner`, `Developing`, `Intermediate`, `Challenging`).
7. `Step 7`: Solved SQL beginner exercise (`sql-first-select-constant`) via Monaco editor; verified PGlite rejects wrong query and accepts correct query.
8. `Step 8`: Navigated to `/curriculum`; confirmed all 9 subjects and 157 topics remain manually accessible.
9. `Step 9`: Tested mobile responsive layout (viewport 390x844); confirmed zero horizontal scroll overflow and valid keyboard focus outline.

---

## 4. Preservation & Migration Safeguards

- **Zero Schema Mutations**: All existing SQLite schema migrations (1 through 6) remain frozen with intact SHA-256 checksums.
- **Historical Data Preserved**: No learner records, attempt histories, or study session tables were modified or dropped.
- **No Fabricated Approvals**: Candidate lessons awaiting editorial review retain their candidate status.
- **Local Working Tree**: All modifications exist only in the working tree; zero git commits or pushes have been executed.

---

## 5. Remaining Content Gaps & Transparent Roadmap

1. **First Steps Exercise Coverage**:
   - 14 First Steps exercises (7 Python, 4 SQL, 3 DSA) are authored and verified.
   - Additional First Steps exercises can be authored for non-coding tracks (Quantitative Aptitude, Logical Reasoning, Verbal & Communication) as interactive question sets.
2. **Candidate Lesson Editorial Queue**:
   - 53 legacy reference lessons (`content/ai-engineer/v1/`) remain baseline reference material.
   - Placement Foundations candidate lessons in `data/content-approvals/independent-audit/` await formal human editorial review before release.
3. **Advanced Stages Progression**:
   - Stages 2–5 (Beginner, Developing, Intermediate, Challenging) are currently powered by the 110 mapped Arena problems. Authored guided steps for these higher tiers will be introduced in Forge V2.
