# Forge V1 Placement Foundations curriculum scope

Status: proposed scope for a new curriculum draft; no lessons or questions are authored here. Based on the local repository audit of 21 October 2026. This is a product coverage proposal, not an assertion about any employer's current exam pattern, selection process or question frequency.

## 1. Product and level boundaries

Forge V1 — Placement Foundations serves Indian freshers preparing for entry-level recruitment, including the companies named in the project brief and startups. It provides all nine subjects below at Levels 1–3. The curriculum must be explicitly reviewed, confirmed and activated as a new revision; neither existing confirmed curriculum is silently edited.

Forge V2 — Advanced Engineering later adds Levels 4–5 through the same app, backend, database, learning engine and assessment engine. Existing curriculum `version: 2` is historical revision metadata, not the advanced product edition. Existing `target_level` strings are not numeric product levels.

- **Level 1 — Understand and start:** terminology, small concrete examples, simple guided tasks, accurate mental models. No prior specialist knowledge assumed.
- **Level 2 — Apply independently:** varied standard tasks, multiple steps, debugging/explanation, explicit edge cases, reduced scaffolding.
- **Level 3 — Combine and transfer:** intermediate mixed tasks, timed objective sets, unfamiliar contexts, defensible choices and delayed recall. This does not mean advanced engineering specialization.
- **Levels 4–5 — Future scope:** advanced algorithms and engineering/AI depth; no second application or separate learner database.

Level placement describes content complexity. Reading a Level 3 lesson does not imply Level 3 competence or change mastery. Every subject and topic remains manually accessible; prerequisites and plans guide rather than lock learning.

## 2. Required subjects and planned coverage

### 1. Quantitative Aptitude (`quantitative-aptitude`)

Existing accepted content: none; no matching dedicated curriculum track or static problem bank.

- Level 1: number operations, factors/multiples, fractions/decimals, ratios/proportions, percentages, averages, units, estimation and translating a word problem into quantities.
- Level 2: profit/loss/discount, simple/compound interest, mixtures, work/rates, speed/time/distance, basic algebra and equations, tables/charts and data interpretation.
- Level 3: combined rate/percentage scenarios, sequences, basic counting and probability, elementary geometry/mensuration, mixed data interpretation and timed multistep problems.
- Objective evidence: original MCQs/numeric responses with explicit units, rounding/tolerance and independently checked worked solutions. Prevent ambiguous percentage bases, hidden assumptions and floating-point grading errors.
- Reference work needed: approve reputable public mathematics/education references and source records before authoring. Do not import proprietary aptitude banks or imply these proposed topics are a verified company syllabus.

### 2. Logical Reasoning (`logical-reasoning`)

Existing accepted content: none.

- Level 1: patterns, classification, ordering, directions, relations, statements and simple logical implication.
- Level 2: seating/arrangement constraints, syllogisms, ranking, coding/decoding conventions, truth/falsehood, series and structured elimination.
- Level 3: multiconstraint puzzles, data sufficiency, assumptions/conclusions, argument evaluation and timed mixed reasoning sets.
- Objective evidence: MCQ/structured solutions with explicit conventions, satisfiable constraints and unique-answer or valid-multiple-answer proofs. Use enumeration/solver-style verification in development where a small deterministic program can establish validity; no runtime model.
- Keep ambiguous “intended pattern” questions out of scored sets unless rules or accepted alternatives are explicit.

### 3. Verbal Ability and English (`verbal-english`)

Existing accepted content: none; historical interview topic titles do not provide a language course.

- Level 1: sentence structure, parts of speech in context, subject/verb agreement, tense consistency, articles/prepositions and reading short passages.
- Level 2: error correction, vocabulary in context, sentence ordering/connectors, paragraph comprehension, inference supported by text and clear workplace email structure.
- Level 3: longer passage analysis, argument structure/tone, editing for clarity, summarizing and timed mixed verbal sets; practical written communication rehearsal.
- Objective evidence: reviewed grammar/reading questions with an unambiguous accepted answer and explanatory alternatives. State the English usage/style convention and accept legitimate variants when the item permits them.
- Open writing is reflection with static examples/rubrics; do not turn keyword counts, spelling counts or a learner's self-rating into language mastery. Source and review language guidance before publication.

### 4. Python Programming (`python`)

Existing accepted material: 19 lessons and 133 concept exercises under `content/ai-engineer/v1/python`, plus 40 Python Arena problems. The course exercises contain no executable coding items; Arena supplies independent coding. Existing content is reusable after correctness, clarity, provenance and level review.

- Level 1: variables/basic types, expressions, input/output, conditions, loops, strings, lists/tuples/dicts/sets, simple functions and tracing execution.
- Level 2: decomposition, mutation/aliasing, comprehensions, common string/collection tasks, exceptions, files/JSON/CSV, modules/environments, basic classes, debugging and deterministic tests.
- Level 3: unfamiliar-code reading, iterator/generator fundamentals, practical typing, intermediate collection problems, test design/edge cases and simple concurrency awareness where prerequisite knowledge supports it.
- Objective evidence: original implementation/debug tasks executed in the Pyodide worker, typed expected values, boundary tests and visible examples. MCQs/checkpoints support learning but do not replace independent coding.
- Reuse mappings: `foundations` -> `syntax-data-types`; explicit bundles for `pythonic-programming`, `exceptions-files-data`, `modules-packages-environments`, `advanced-working-python`, `standard-library`, `concurrency`, and `testing-debugging-quality`. These consolidated topics need coverage decisions; do not guess equivalence from names.
- Keep advanced metaprogramming, production concurrency architectures and specialized package ecosystems outside V1's mandatory foundations.

### 5. SQL and PostgreSQL (`sql-postgresql`)

Existing accepted material: 14 lessons, 98 concept exercises and 30 SQL Arena problems. All existing SQL Arena references execute in PGlite; this does not validate every SQL lesson example or prose answer.

- Level 1: tables/rows/keys, relational thinking, SELECT, expressions/types, WHERE, ORDER BY, LIMIT, NULL and basic aggregation.
- Level 2: joins, grouping/HAVING, subqueries, CTEs, schema constraints/relationships, safe data modification and transactional reasoning.
- Level 3: window functions, multi-table intermediate queries, duplicate/null/order edge cases, indexes/EXPLAIN intuition, transaction concurrency basics and parameterized Python/database integration as guided static material.
- Objective evidence: isolated PGlite query fixtures with visible and alternate datasets, exact result columns and normalized rows. Declare order requirements. The current bank is SELECT/CTE oriented; do not claim it assesses safe DML, rollback or schema design until dedicated fixtures are added.
- Reuse all existing SQL topic keys. Fix legacy Arena mappings `sql-cs/subqueries`, `sql-cs/ctes`, `sql-cs/group-by` through explicit bindings to subqueries, ctes, aggregation.
- Defer database administration, replication internals and advanced PostgreSQL performance engineering to later levels. Forge learner data stays in SQLite; a lesson's SQL never executes there.

### 6. DSA and Problem Solving (`dsa`)

Existing accepted material: 20 lessons, 140 concept exercises, and 40 DSA Arena problems; several Python-bank problems also map to DSA competencies.

- Level 1: problem decomposition, tracing, input/output contracts, basic time/space complexity, arrays/strings, hashing/sets, straightforward search and basic sorting ideas.
- Level 2: two pointers, sliding windows, binary search, stacks/queues, linked lists, recursion, standard sorting applications, basic trees and breadth/depth traversal.
- Level 3: intermediate combinations, heaps/top-k, graph traversal, elementary backtracking and dynamic programming, correctness reasoning, edge cases and independent timed transfer tasks.
- Objective evidence: original Python function or stdin/stdout tasks, exact nested types, exceptions where specified, deterministic hidden tests and clearly stated constraints. A test pass alone does not prove asymptotic complexity; use input bounds and reviewed complexity reasoning.
- Explicit aliases: legacy `stacks` -> revision-2 `stack`, `queues` -> `queue-deque`; older `graph-basics` and `dynamic-programming-basics` require reviewed coverage mappings to graphs/DP rather than destructive renaming.
- Fix the known tuple/list contract contradiction in `dsa-two-sum-indices` in a new problem revision. Do not expose reference solutions before pass or Give Up.
- Advanced graph algorithms, advanced DP, segment trees and competition-focused techniques belong in Levels 4–5 unless separately approved as optional enrichment.

### 7. System Design Fundamentals (`system-design`)

Existing accepted static lessons: none. Reusable metadata: revision-2 `cs-fundamentals/system-design`, backend concepts, historical interview `system-design` blueprint and fixed rubric. These are not a shipped course.

- Level 1: requirements, client/server, HTTP/API boundaries, data flow, database roles, simple diagrams and a small single-service design.
- Level 2: schema/API choices, pagination, caching/queues at an introductory level, timeouts/retries, authentication/authorization and observable failures.
- Level 3: small application design tradeoffs, basic capacity estimates, reliability/security boundaries, failure recovery and explaining why a simple design meets stated requirements.
- Objective evidence: bounded scenarios/MCQs and structured data-flow or component-choice checks. Open architecture explanations use static rubrics and reflection; do not claim deterministic semantic grading of arbitrary designs.
- Incorporate networks, OS/process/thread basics and transactions where they explain the design. Do not create a broad standalone CS theory track. Large distributed systems internals are later-edition scope.

### 8. AI Fundamentals, Generative AI, RAG and Agentic AI (`ai-fundamentals`)

Existing accepted static lessons: none. Reusable topic metadata in historical `machine-learning`, `llm-engineering` and `rag` tracks and old interview blueprints.

- Level 1: AI/ML/generative AI distinctions, data/training/inference, basic evaluation, model limitations, bias/privacy and appropriate human judgment.
- Level 2: tokens/context, prompts/structured outputs, embeddings/similarity, retrieval/chunking/citations, RAG data flow, hallucinations and evaluation with fixed examples.
- Level 3: tool calling and bounded agent loops, state/memory, approval boundaries, retrieval/reranking tradeoffs, offline failure analysis, reliability/cost concepts and comparing recorded outputs against fixed criteria.
- Objective evidence: prewritten scenarios, trace ordering, failure classification, deterministic toy retrieval exercises and prerecorded input/output examples. Free-form critiques remain reflection. The Forge app itself never needs a live model to teach these concepts.
- Treat vendor API details and evolving model behavior as versioned material requiring dated reference review; do not turn current model marketing into timeless facts.
- Defer model training infrastructure, advanced math/optimization, production multi-agent orchestration and specialized distributed retrieval to Levels 4–5.

### 9. Interview Preparation and Communication (`interview-communication`)

Existing accepted static lessons: none. Reusable fixed interview blueprints, session/history/report tables, project profile format, interview UI and fixed rubric code. The existing project profiles are specific projects, not facts about every learner's experience.

- Level 1: introducing oneself, explaining a simple project honestly, listening/clarification, describing an approach and basic professional communication.
- Level 2: structured behavioral stories, project decisions/tradeoffs, explaining a bug/test, think-aloud coding, concise email answers and asking useful questions.
- Level 3: timed mixed technical mock interviews, follow-up handling, project/system-design discussion, reflection on evidence and communicating uncertainty without inventing experience.
- Objective evidence: technical MCQ/code/SQL tasks reuse their subject's scoring policy. Communication/project/behavioral answers are saved rehearsal with static rubric/model examples and self-reflection; they do not receive fabricated objective grades or modify technical mastery.
- Scored sessions block tutor/search/doubt-style help where it would reveal assessment content; detailed feedback is deferred until completion. At most one prewritten contextual follow-up per main question. Forge Interview Score is not a hiring probability or an employer-specific prediction.

## 3. Existing content reuse and approval gate

The current 53 lesson topics are a starting corpus for three subjects, not 53 finished subject/level cells. Six subjects need new static teaching; all nine need explicit level mappings, approved coverage specifications, reviewed assessment pools and consistent publication identities.

Python/SQL/DSA are foundational P0 priorities (existing revision-2 priorities 100/100/98). Keep them prioritized while allocating real time to aptitude, reasoning, English, revision and interviews. Advanced/role-specific historical backend, DevOps, frontend, ML, LLM and RAG topics remain in legacy curricula and can be selectively mapped to the new foundational subjects after review. Do not delete them or assume all are mandatory V1 topics.

The exact count of new lessons/questions is deliberately not estimated from titles. The next curriculum-design step is a versioned coverage specification with one record per competency: subject/level, outcome, prerequisites, source support, existing content links, missing lesson sections, deterministic assessment requirements, transfer/recall variants and approval status. Completion means every required record has accepted evidence; a title count or keyword match is insufficient.

## 4. Teaching contract for every published lesson

Each approved lesson must contain:

- A short purpose and prerequisites in accessible language.
- Small sections with a measurable learning objective and explained terminology.
- At least one useful real-world analogy when it aids understanding, without replacing a precise explanation.
- Worked examples with explicit assumptions, step-by-step reasoning, verified output/answer and readable formatting.
- Common mistakes tied to specific misconception checks.
- Practice in increasing difficulty with progressive hints and verified solutions.
- Knowledge checkpoints with stored answers/explanations or explicitly reflective status.
- A revision summary and links to deterministic recall items scheduled through existing FSRS machinery.
- Sources/provenance, licensing/attribution, immutable revision, validation evidence and explicit technical/clarity approval.

Do not force identical section templates into repetitive prose. Length/headings are minimum structural checks, not proof of pedagogy. A novice reviewer must be able to follow the explanation without unexplained jargon. Confirmed coverage and accepted lessons cannot be overridden by runtime behavior.

## 5. Daily study targets and subject balance

Expose 5/6/8-hour presets as 300/360/480 study minutes; breaks are separate and clearly labeled. The following are feasible budget examples for implementation tests, not a static timetable imposed on every learner:

- 300 minutes: review 30; Python/SQL/DSA 135 combined; quantitative/reasoning 60; English 30; interview 30; system-design/AI rotation 15.
- 360 minutes: review 40; Python/SQL/DSA 150; quantitative/reasoning 70; English 35; interview 35; system-design/AI rotation 30.
- 480 minutes: review 50; Python/SQL/DSA 210; quantitative/reasoning 90; English 45; interview 45; system-design/AI rotation 40.

The actual deterministic planner adapts to prerequisite needs, weak topics, due reviews, available approved content and user settings; rotation is measured across days where every subject cannot fit every day. Due backlog, minima and activity sizes cannot silently push the plan over budget. Plans are advisory, manual study remains available, and completed plan items/reading time never create mastery evidence.

## 6. Acceptance criteria for curriculum readiness

1. All nine subject keys and Levels 1–3 appear in an explicitly confirmed new curriculum release; no modification of existing confirmed structures.
2. Every required competency has reviewed source support, approved lesson coverage, practice and an assessment route appropriate to the skill. Unsupported free-text grading is explicitly reflection.
3. Python/SQL/DSA include independent coding evidence, reserved clean transfer variants and delayed recall; cap/assistance rules are unchanged unless a separate versioned policy is approved.
4. Every shipped example/reference solution and machine-gradable answer passes the appropriate deterministic checks. Open-text answers and explanations have recorded technical/clarity review.
5. The entire installed product works without a provider SDK, API key, model endpoint or external network. Teaching AI topics does not add runtime AI.
6. Source provenance and attribution survive serialization/publication; future Arena challenges are original and existing adapted-bank history is preserved with its true provenance.
7. Manual access to every subject/topic is preserved regardless of recommendation, proficiency or study target.
8. No claim of company-specific syllabus completeness, current test patterns or hiring probability is made without a separate current primary-source verification task.
