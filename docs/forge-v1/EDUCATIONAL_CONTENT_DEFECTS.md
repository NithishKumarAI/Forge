# Educational content defects

**The current course is not reliable enough to be a beginner's sole learning platform.** This audit scanned all53 lessons,371 exercises and110 historical problem files, and attempted all258 example blocks in actual browser workers. It does not manufacture independent human approval or certify the absence of further semantic defects.

## Method and interpretation

Python:166 of189 standalone blocks matched their displayed stdout.23 failed as independently executed blocks: missing helpers/imports, unavailable host packages or nonportable/incorrect output expectations. These are not all algorithm errors. Learn currently displays code; it does not automatically reconstruct earlier section state.

SQL:37 of69 blocks executed in fresh PGlite databases;32 lacked declared tables/setup. Of the37,26 matched explicit tables,3 Indexes examples have material result/query defects,1 has a fixed expectation for CURRENT_TIMESTAMP,5 require Date/TZ/NULL display-context review, and2 use prose outputs requiring human comparison. Date/NULL serialization differences were deliberately not called wrong logical answers.

All110 historical coding contracts and the corrected Two Sum candidate passed the existing reference validator. Independent constant-answer mutants were rejected for all80 eligible Python/DSA functions. That does not prove all task constraints are enforced: four in-place counterexamples pass output-only tests. The SQL bank also passed30 problems/60 datasets.

## Specific factual and pedagogical findings

### E01 — python/functions/exercises.json

- Exact file: `content/ai-engineer/v1/python/functions/exercises.json`.
- Section/key: `functions-write`.
- Existing behavior/text: Generic normalization guidance omits zero/empty/negative behavior and a concrete solution.
- Why weak/wrong and expected behavior: State the input domain, boundary behavior and no-mutation promise; provide executable code and exact tests.
- Evidence/correction: Full Functions1.2.0 candidate replaces all seven exercises; six standalone examples execute.

### E02 — python/exceptions/lesson.json

- Exact file: `content/ai-engineer/v1/python/exceptions/lesson.json`.
- Section/key: `try-except-blocks`.
- Existing behavior/text: Treats except Exception as swallowing KeyboardInterrupt.
- Why weak/wrong and expected behavior: KeyboardInterrupt inherits BaseException outside Exception; distinguish bare except from except Exception.
- Evidence/correction: python-factual-probes.json; new exceptions1.2.0 factual patch; [Python exceptions](https://docs.python.org/3/library/exceptions.html).

### E03 — python/type-hints/lesson.json

- Exact file: `content/ai-engineer/v1/python/type-hints/lesson.json`.
- Section/key: `interview-check`.
- Existing behavior/text: Says annotations are stripped by the compiler.
- Why weak/wrong and expected behavior: Annotations are metadata available to inspection; automatic runtime type enforcement is a separate issue and evaluation behavior is version-dependent.
- Evidence/correction: python-factual-probes.json records __annotations__; new type-hints1.2.0 patch; [Python data model](https://docs.python.org/3/reference/datamodel.html).

### E04 — python/control-flow/lesson.json

- Exact file: `content/ai-engineer/v1/python/control-flow/lesson.json`.
- Section/key: `truthiness-and-falsiness`.
- Existing behavior/text: Says all objects outside the listed built-ins are truthy.
- Why weak/wrong and expected behavior: User-defined __bool__ or __len__ can make other objects falsy.
- Evidence/correction: python-factual-probes.json includes a falsy custom object; control-flow1.2.0 patch; [Python data model](https://docs.python.org/3/reference/datamodel.html#object.__bool__).

### E05 — sql-postgresql/relational-foundations/lesson.json

- Exact file: `content/ai-engineer/v1/sql-postgresql/relational-foundations/lesson.json`.
- Section/key: `keys-and-relationships`.
- Existing behavior/text: Defines a foreign key as referencing only a primary key.
- Why weak/wrong and expected behavior: A qualifying UNIQUE key can also be referenced; this lesson contradicts its own constraints-design companion.
- Evidence/correction: sql-factual-probes.json verifies a reference to UNIQUE; [PostgreSQL constraints](https://www.postgresql.org/docs/18/ddl-constraints.html).

### E06 — sql-postgresql/aggregation/lesson.json

- Exact file: `content/ai-engineer/v1/sql-postgresql/aggregation/lesson.json`.
- Section/key: `group-by-partitioning`.
- Existing behavior/text: Requires every selected column to be grouped or aggregated without qualification.
- Why weak/wrong and expected behavior: PostgreSQL permits columns functionally dependent on a grouped primary key.
- Evidence/correction: sql-factual-probes.json executes the counterexample; [PostgreSQL table expressions](https://www.postgresql.org/docs/current/queries-table-expressions.html).

### E07 — sql-postgresql/joins/lesson.json

- Exact file: `content/ai-engineer/v1/sql-postgresql/joins/lesson.json`.
- Section/key: `multi-table-joins-and-cartesian`.
- Existing behavior/text: Says omitting ON from a plain JOIN creates a Cartesian product.
- Why weak/wrong and expected behavior: Plain JOIN needs ON/USING or a qualifying join form; use CROSS JOIN/comma syntax for the Cartesian product.
- Evidence/correction: sql-factual-probes.json captures syntax rejection; [PostgreSQL table expressions](https://www.postgresql.org/docs/current/queries-table-expressions.html).

### E08 — sql-postgresql/subqueries/lesson.json

- Exact file: `content/ai-engineer/v1/sql-postgresql/subqueries/lesson.json`.
- Section/key: `scalar-subqueries`.
- Existing behavior/text: Says a scalar subquery returns exactly one row.
- Why weak/wrong and expected behavior: It may return zero rows, producing NULL; more than one row is rejected.
- Evidence/correction: sql-factual-probes.json; [PostgreSQL value expressions](https://www.postgresql.org/docs/18/sql-expressions.html).

### E09 — sql-postgresql/ctes/lesson.json

- Exact file: `content/ai-engineer/v1/sql-postgresql/ctes/lesson.json`.
- Section/key: `readability-and-subquery-comparison`.
- Existing behavior/text: Says PostgreSQL12+ CTEs are inlined by default unless explicitly materialized.
- Why weak/wrong and expected behavior: Inlining depends on recursion, side effects and reference count; multiply referenced CTEs can be materialized by default.
- Evidence/correction: sql-factual-probes.json captures a CTE Scan; [PostgreSQL WITH](https://www.postgresql.org/docs/18/queries-with.html).

### E10 — sql-postgresql/indexes/lesson.json

- Exact file: `content/ai-engineer/v1/sql-postgresql/indexes/lesson.json`.
- Section/key: `btree-fundamentals / composite-indexes-and-column-order`.
- Existing behavior/text: Two examples create empty tables but promise selected rows.
- Why weak/wrong and expected behavior: Insert the exact sample data or expect empty results.
- Evidence/correction: Actual browser PGlite results are empty; SQL Indexes1.2.0 candidate supplies explicit rows and verified fixtures.

### E11 — sql-postgresql/indexes/lesson.json

- Exact file: `content/ai-engineer/v1/sql-postgresql/indexes/lesson.json`.
- Section/key: `write-cost-and-index-tradeoffs`.
- Existing behavior/text: Filters pg_stat_user_indexes.relname using an index name; promises a fixed16kB size.
- Why weak/wrong and expected behavior: Use indexrelname for the index name; do not invent an environment-independent size.
- Evidence/correction: Actual query returns no rows. Indexes1.2.0 fixes catalog columns and removes the fixed size.

### E12 — sql-postgresql/indexes/lesson.json

- Exact file: `content/ai-engineer/v1/sql-postgresql/indexes/lesson.json`.
- Section/key: `write-cost-and-index-tradeoffs / explain-and-query-plans`.
- Existing behavior/text: Equates ten indexes with exactly eleven physical writes and claims Index Only Scan means zero heap fetches.
- Why weak/wrong and expected behavior: Distinguish logical maintenance, MVCC/HOT/vacuum, buffers and WAL; heap visibility checks may still fetch heap pages.
- Evidence/correction: Indexes1.2.0 correction; [PostgreSQL index-only scans](https://www.postgresql.org/docs/18/indexes-index-only-scans.html).

### E13 — sql-postgresql/postgresql-practicals/lesson.json

- Exact file: `content/ai-engineer/v1/sql-postgresql/postgresql-practicals/lesson.json`.
- Section/key: `identity-vs-serial`.
- Existing behavior/text: Claims identity prevents accidental sequence desynchronization.
- Why weak/wrong and expected behavior: BY DEFAULT identity accepts explicit values that need not advance its sequence.
- Evidence/correction: sql-factual-probes.json demonstrates a following default insert colliding with an explicit key; review wording and demonstrate sequence ownership versus advancement.

### E14 — dsa/big-o/lesson.json

- Exact file: `content/ai-engineer/v1/dsa/big-o/lesson.json`.
- Section/key: `worst-case-vs-amortized`.
- Existing behavior/text: Says CPython lists grow by doubling their capacity.
- Why weak/wrong and expected behavior: Explain proportional over-allocation and amortized behavior without assigning the wrong concrete growth policy.
- Evidence/correction: The [CPython3.12 source](https://github.com/python/cpython/blob/v3.12.0/Objects/listobject.c) implements mild proportional growth, not universal doubling. Its hardcoded byte-output example also differs in Pyodide.

### E15 — dsa/bfs/lesson.json

- Exact file: `content/ai-engineer/v1/dsa/bfs/lesson.json`.
- Section/key: `level-order-and-layers`.
- Existing behavior/text: Groups unweighted Dijkstra with DFS as exploring suboptimal deep paths first.
- Why weak/wrong and expected behavior: Dijkstra extracts the minimum-distance frontier; BFS avoids the unnecessary priority-queue cost for equal edge weights.
- Evidence/correction: Compare FIFO BFS with a min-priority queue; revise the conceptual explanation rather than teaching a false ordering property.

### E16 — dsa/arrays/lesson.json

- Exact file: `content/ai-engineer/v1/dsa/arrays/lesson.json`.
- Section/key: `from-naive-to-better`.
- Existing behavior/text: Calls an ordinary two-pass approach inherently too slow.
- Why weak/wrong and expected behavior: Two linear passes remain O(n); explain repeated work for a concrete problem and account for preprocessing/query counts.
- Evidence/correction: Inspect the actual prefix-sum example and its O(n) preprocessing; the blanket optimization story does not establish an asymptotic improvement.

### E17 — dsa/sets/lesson.json

- Exact file: `content/ai-engineer/v1/dsa/sets/lesson.json`.
- Section/key: `interview-use-cases`.
- Existing behavior/text: Describes collision chaining after correctly describing open addressing.
- Why weak/wrong and expected behavior: Use consistent implementation terminology and distinguish hash-table strategies.
- Evidence/correction: The two sections contradict each other; correct the implementation explanation in a new candidate.

### E18 — dsa/sliding-window/lesson.json

- Exact file: `content/ai-engineer/v1/dsa/sliding-window/lesson.json`.
- Section/key: `prerequisites`.
- Existing behavior/text: References python/basics, which is not an existing lesson identity in the corpus.
- Why weak/wrong and expected behavior: Provide a reviewed cross-track prerequisite mapping or the correct concrete lesson identity; do not infer one from the title.
- Evidence/correction: Complete prerequisite census records the unresolved reference;14 lessons also declare no prerequisites and need pedagogical review.

### E19 — python/virtual-environments/lesson.json

- Exact file: `content/ai-engineer/v1/python/virtual-environments/lesson.json`.
- Section/key: `why-isolation-matters / activation-and-path-mechanics / interpreter-selection`.
- Existing behavior/text: Expected output embeds developer-specific absolute Windows paths and assumes an active venv.
- Why weak/wrong and expected behavior: Use portable descriptive output and explicitly label host-only context; do not distribute private paths as universal answers.
- Evidence/correction: Browser outputs differ; exact source sections are locatable without repeating those private paths here.

### E20 — sql-postgresql/data-modification/lesson.json

- Exact file: `content/ai-engineer/v1/sql-postgresql/data-modification/lesson.json`.
- Section/key: `returning-clause`.
- Existing behavior/text: CURRENT_TIMESTAMP example promises one fixed September2026 timestamp.
- Why weak/wrong and expected behavior: Mark the timestamp as variable, inject a fixed value, or compare a controlled invariant.
- Evidence/correction: Actual October2026 execution returns current time; sql-output-comparisons.json records the nondeterministic expectation.

## Scored contract defects

### C01 — Tuple/list contradiction

- File: `content/problem-bank/dsa/dsa-two-sum-indices.json`; key `dsa-two-sum-indices`, original revision unchanged.
- The statement requires a tuple, while its fixtures/reference use lists. A tuple-returning implementation passed0/3 full tests even though it follows the stated return-type requirement.
- Expected: one explicit, consistent type, duplicate/no-solution policy and matching fixtures. Existing corrected1.0.1 candidate independently revalidated; it remains unpublished and unapproved.

### C02 — Input mutation and complexity are not certified by returned values

- Files: `content/problem-bank/dsa/dsa-move-zeroes.json`, `dsa-sort-colors.json`, `dsa-reverse-string.json`, `dsa-remove-duplicates-sorted.json`.
- Each statement requires in-place work. Four implementations that return newly allocated correct values pass all current output tests. This does not establish the promised mutation or space bound.
- Expected: a new reviewed contract that observes relevant post-call inputs, or revised candidate wording that explicitly limits grading to return/output correctness. Never relabel old100% output scores as proof of in-place or complexity proficiency. Legacy Arena remains unverified and grants no new approved mastery credit.
- Evidence: `audit-evidence/contract-probes.json` contains exact sources and results. This content/contract limitation remains a release blocker; historical contracts/evidence were not changed.

### C03 — Unspecified constraints and thin fixture depth

-38 problem files use the literal constraint placeholder “Reasonable constraints for the problem”.83 of110 have only one hidden test/dataset, in addition to their public/base examples.
- Expected: explicit input domain, bounds, tie/empty/duplicate policies, positive and negative fixtures, and typed behavior. Thin depth alone is a risk indicator, not proof of a wrong algorithm. Every problem and depth is in content-census.json.

## Exhaustive generic exercise findings

26 MCQs reward generic advice rather than the named topic;52 reference answers describe what a good answer should do instead of showing one;13 repair prompts omit the actual failing program/contract. These are exact detections, not a guess based on a lesson title.

- `content/ai-engineer/v1/dsa/arrays/exercises.json` / `arrays-tradeoff`: generic_objective_question. Expected: A topic-specific, fully specified task with a concrete worked answer, tested boundaries and an explanation tied to its actual inputs.
- `content/ai-engineer/v1/dsa/arrays/exercises.json` / `arrays-failure`: generic_objective_question. Expected: A topic-specific, fully specified task with a concrete worked answer, tested boundaries and an explanation tied to its actual inputs.
- `content/ai-engineer/v1/dsa/arrays/exercises.json` / `arrays-predict`: generic_reference_answer. Expected: A topic-specific, fully specified task with a concrete worked answer, tested boundaries and an explanation tied to its actual inputs.
- `content/ai-engineer/v1/dsa/arrays/exercises.json` / `arrays-fix`: generic_reference_answer. Expected: A topic-specific, fully specified task with a concrete worked answer, tested boundaries and an explanation tied to its actual inputs.
- `content/ai-engineer/v1/dsa/arrays/exercises.json` / `arrays-fix`: missing_program_contract. Expected: A topic-specific, fully specified task with a concrete worked answer, tested boundaries and an explanation tied to its actual inputs.
- `content/ai-engineer/v1/dsa/arrays/exercises.json` / `arrays-write`: generic_reference_answer. Expected: A topic-specific, fully specified task with a concrete worked answer, tested boundaries and an explanation tied to its actual inputs.
- `content/ai-engineer/v1/dsa/arrays/exercises.json` / `arrays-explain`: generic_reference_answer. Expected: A topic-specific, fully specified task with a concrete worked answer, tested boundaries and an explanation tied to its actual inputs.
- `content/ai-engineer/v1/dsa/dynamic-programming/exercises.json` / `dynamicprogr-tradeoff`: generic_objective_question. Expected: A topic-specific, fully specified task with a concrete worked answer, tested boundaries and an explanation tied to its actual inputs.
- `content/ai-engineer/v1/dsa/dynamic-programming/exercises.json` / `dynamicprogr-failure`: generic_objective_question. Expected: A topic-specific, fully specified task with a concrete worked answer, tested boundaries and an explanation tied to its actual inputs.
- `content/ai-engineer/v1/dsa/dynamic-programming/exercises.json` / `dynamicprogr-predict`: generic_reference_answer. Expected: A topic-specific, fully specified task with a concrete worked answer, tested boundaries and an explanation tied to its actual inputs.
- `content/ai-engineer/v1/dsa/dynamic-programming/exercises.json` / `dynamicprogr-fix`: generic_reference_answer. Expected: A topic-specific, fully specified task with a concrete worked answer, tested boundaries and an explanation tied to its actual inputs.
- `content/ai-engineer/v1/dsa/dynamic-programming/exercises.json` / `dynamicprogr-fix`: missing_program_contract. Expected: A topic-specific, fully specified task with a concrete worked answer, tested boundaries and an explanation tied to its actual inputs.
- `content/ai-engineer/v1/dsa/dynamic-programming/exercises.json` / `dynamicprogr-write`: generic_reference_answer. Expected: A topic-specific, fully specified task with a concrete worked answer, tested boundaries and an explanation tied to its actual inputs.
- `content/ai-engineer/v1/dsa/dynamic-programming/exercises.json` / `dynamicprogr-explain`: generic_reference_answer. Expected: A topic-specific, fully specified task with a concrete worked answer, tested boundaries and an explanation tied to its actual inputs.
- `content/ai-engineer/v1/dsa/hash-maps/exercises.json` / `hashmaps-tradeoff`: generic_objective_question. Expected: A topic-specific, fully specified task with a concrete worked answer, tested boundaries and an explanation tied to its actual inputs.
- `content/ai-engineer/v1/dsa/hash-maps/exercises.json` / `hashmaps-failure`: generic_objective_question. Expected: A topic-specific, fully specified task with a concrete worked answer, tested boundaries and an explanation tied to its actual inputs.
- `content/ai-engineer/v1/dsa/hash-maps/exercises.json` / `hashmaps-predict`: generic_reference_answer. Expected: A topic-specific, fully specified task with a concrete worked answer, tested boundaries and an explanation tied to its actual inputs.
- `content/ai-engineer/v1/dsa/hash-maps/exercises.json` / `hashmaps-fix`: generic_reference_answer. Expected: A topic-specific, fully specified task with a concrete worked answer, tested boundaries and an explanation tied to its actual inputs.
- `content/ai-engineer/v1/dsa/hash-maps/exercises.json` / `hashmaps-fix`: missing_program_contract. Expected: A topic-specific, fully specified task with a concrete worked answer, tested boundaries and an explanation tied to its actual inputs.
- `content/ai-engineer/v1/dsa/hash-maps/exercises.json` / `hashmaps-write`: generic_reference_answer. Expected: A topic-specific, fully specified task with a concrete worked answer, tested boundaries and an explanation tied to its actual inputs.
- `content/ai-engineer/v1/dsa/hash-maps/exercises.json` / `hashmaps-explain`: generic_reference_answer. Expected: A topic-specific, fully specified task with a concrete worked answer, tested boundaries and an explanation tied to its actual inputs.
- `content/ai-engineer/v1/dsa/sliding-window/exercises.json` / `slidingwindo-tradeoff`: generic_objective_question. Expected: A topic-specific, fully specified task with a concrete worked answer, tested boundaries and an explanation tied to its actual inputs.
- `content/ai-engineer/v1/dsa/sliding-window/exercises.json` / `slidingwindo-failure`: generic_objective_question. Expected: A topic-specific, fully specified task with a concrete worked answer, tested boundaries and an explanation tied to its actual inputs.
- `content/ai-engineer/v1/dsa/sliding-window/exercises.json` / `slidingwindo-predict`: generic_reference_answer. Expected: A topic-specific, fully specified task with a concrete worked answer, tested boundaries and an explanation tied to its actual inputs.
- `content/ai-engineer/v1/dsa/sliding-window/exercises.json` / `slidingwindo-fix`: generic_reference_answer. Expected: A topic-specific, fully specified task with a concrete worked answer, tested boundaries and an explanation tied to its actual inputs.
- `content/ai-engineer/v1/dsa/sliding-window/exercises.json` / `slidingwindo-fix`: missing_program_contract. Expected: A topic-specific, fully specified task with a concrete worked answer, tested boundaries and an explanation tied to its actual inputs.
- `content/ai-engineer/v1/dsa/sliding-window/exercises.json` / `slidingwindo-write`: generic_reference_answer. Expected: A topic-specific, fully specified task with a concrete worked answer, tested boundaries and an explanation tied to its actual inputs.
- `content/ai-engineer/v1/dsa/sliding-window/exercises.json` / `slidingwindo-explain`: generic_reference_answer. Expected: A topic-specific, fully specified task with a concrete worked answer, tested boundaries and an explanation tied to its actual inputs.
- `content/ai-engineer/v1/dsa/trees/exercises.json` / `trees-tradeoff`: generic_objective_question. Expected: A topic-specific, fully specified task with a concrete worked answer, tested boundaries and an explanation tied to its actual inputs.
- `content/ai-engineer/v1/dsa/trees/exercises.json` / `trees-failure`: generic_objective_question. Expected: A topic-specific, fully specified task with a concrete worked answer, tested boundaries and an explanation tied to its actual inputs.
- `content/ai-engineer/v1/dsa/trees/exercises.json` / `trees-predict`: generic_reference_answer. Expected: A topic-specific, fully specified task with a concrete worked answer, tested boundaries and an explanation tied to its actual inputs.
- `content/ai-engineer/v1/dsa/trees/exercises.json` / `trees-fix`: generic_reference_answer. Expected: A topic-specific, fully specified task with a concrete worked answer, tested boundaries and an explanation tied to its actual inputs.
- `content/ai-engineer/v1/dsa/trees/exercises.json` / `trees-fix`: missing_program_contract. Expected: A topic-specific, fully specified task with a concrete worked answer, tested boundaries and an explanation tied to its actual inputs.
- `content/ai-engineer/v1/dsa/trees/exercises.json` / `trees-write`: generic_reference_answer. Expected: A topic-specific, fully specified task with a concrete worked answer, tested boundaries and an explanation tied to its actual inputs.
- `content/ai-engineer/v1/dsa/trees/exercises.json` / `trees-explain`: generic_reference_answer. Expected: A topic-specific, fully specified task with a concrete worked answer, tested boundaries and an explanation tied to its actual inputs.
- `content/ai-engineer/v1/dsa/two-pointers/exercises.json` / `twopointers-tradeoff`: generic_objective_question. Expected: A topic-specific, fully specified task with a concrete worked answer, tested boundaries and an explanation tied to its actual inputs.
- `content/ai-engineer/v1/dsa/two-pointers/exercises.json` / `twopointers-failure`: generic_objective_question. Expected: A topic-specific, fully specified task with a concrete worked answer, tested boundaries and an explanation tied to its actual inputs.
- `content/ai-engineer/v1/dsa/two-pointers/exercises.json` / `twopointers-predict`: generic_reference_answer. Expected: A topic-specific, fully specified task with a concrete worked answer, tested boundaries and an explanation tied to its actual inputs.
- `content/ai-engineer/v1/dsa/two-pointers/exercises.json` / `twopointers-fix`: generic_reference_answer. Expected: A topic-specific, fully specified task with a concrete worked answer, tested boundaries and an explanation tied to its actual inputs.
- `content/ai-engineer/v1/dsa/two-pointers/exercises.json` / `twopointers-fix`: missing_program_contract. Expected: A topic-specific, fully specified task with a concrete worked answer, tested boundaries and an explanation tied to its actual inputs.
- `content/ai-engineer/v1/dsa/two-pointers/exercises.json` / `twopointers-write`: generic_reference_answer. Expected: A topic-specific, fully specified task with a concrete worked answer, tested boundaries and an explanation tied to its actual inputs.
- `content/ai-engineer/v1/dsa/two-pointers/exercises.json` / `twopointers-explain`: generic_reference_answer. Expected: A topic-specific, fully specified task with a concrete worked answer, tested boundaries and an explanation tied to its actual inputs.
- `content/ai-engineer/v1/python/async-await/exercises.json` / `asyncawait-tradeoff`: generic_objective_question. Expected: A topic-specific, fully specified task with a concrete worked answer, tested boundaries and an explanation tied to its actual inputs.
- `content/ai-engineer/v1/python/async-await/exercises.json` / `asyncawait-failure`: generic_objective_question. Expected: A topic-specific, fully specified task with a concrete worked answer, tested boundaries and an explanation tied to its actual inputs.
- `content/ai-engineer/v1/python/async-await/exercises.json` / `asyncawait-predict`: generic_reference_answer. Expected: A topic-specific, fully specified task with a concrete worked answer, tested boundaries and an explanation tied to its actual inputs.
- `content/ai-engineer/v1/python/async-await/exercises.json` / `asyncawait-fix`: generic_reference_answer. Expected: A topic-specific, fully specified task with a concrete worked answer, tested boundaries and an explanation tied to its actual inputs.
- `content/ai-engineer/v1/python/async-await/exercises.json` / `asyncawait-fix`: missing_program_contract. Expected: A topic-specific, fully specified task with a concrete worked answer, tested boundaries and an explanation tied to its actual inputs.
- `content/ai-engineer/v1/python/async-await/exercises.json` / `asyncawait-write`: generic_reference_answer. Expected: A topic-specific, fully specified task with a concrete worked answer, tested boundaries and an explanation tied to its actual inputs.
- `content/ai-engineer/v1/python/async-await/exercises.json` / `asyncawait-explain`: generic_reference_answer. Expected: A topic-specific, fully specified task with a concrete worked answer, tested boundaries and an explanation tied to its actual inputs.
- `content/ai-engineer/v1/python/collections/exercises.json` / `collections-tradeoff`: generic_objective_question. Expected: A topic-specific, fully specified task with a concrete worked answer, tested boundaries and an explanation tied to its actual inputs.
- `content/ai-engineer/v1/python/collections/exercises.json` / `collections-failure`: generic_objective_question. Expected: A topic-specific, fully specified task with a concrete worked answer, tested boundaries and an explanation tied to its actual inputs.
- `content/ai-engineer/v1/python/collections/exercises.json` / `collections-predict`: generic_reference_answer. Expected: A topic-specific, fully specified task with a concrete worked answer, tested boundaries and an explanation tied to its actual inputs.
- `content/ai-engineer/v1/python/collections/exercises.json` / `collections-fix`: generic_reference_answer. Expected: A topic-specific, fully specified task with a concrete worked answer, tested boundaries and an explanation tied to its actual inputs.
- `content/ai-engineer/v1/python/collections/exercises.json` / `collections-fix`: missing_program_contract. Expected: A topic-specific, fully specified task with a concrete worked answer, tested boundaries and an explanation tied to its actual inputs.
- `content/ai-engineer/v1/python/collections/exercises.json` / `collections-write`: generic_reference_answer. Expected: A topic-specific, fully specified task with a concrete worked answer, tested boundaries and an explanation tied to its actual inputs.
- `content/ai-engineer/v1/python/collections/exercises.json` / `collections-explain`: generic_reference_answer. Expected: A topic-specific, fully specified task with a concrete worked answer, tested boundaries and an explanation tied to its actual inputs.
- `content/ai-engineer/v1/python/debugging/exercises.json` / `debugging-tradeoff`: generic_objective_question. Expected: A topic-specific, fully specified task with a concrete worked answer, tested boundaries and an explanation tied to its actual inputs.
- `content/ai-engineer/v1/python/debugging/exercises.json` / `debugging-failure`: generic_objective_question. Expected: A topic-specific, fully specified task with a concrete worked answer, tested boundaries and an explanation tied to its actual inputs.
- `content/ai-engineer/v1/python/debugging/exercises.json` / `debugging-predict`: generic_reference_answer. Expected: A topic-specific, fully specified task with a concrete worked answer, tested boundaries and an explanation tied to its actual inputs.
- `content/ai-engineer/v1/python/debugging/exercises.json` / `debugging-fix`: generic_reference_answer. Expected: A topic-specific, fully specified task with a concrete worked answer, tested boundaries and an explanation tied to its actual inputs.
- `content/ai-engineer/v1/python/debugging/exercises.json` / `debugging-fix`: missing_program_contract. Expected: A topic-specific, fully specified task with a concrete worked answer, tested boundaries and an explanation tied to its actual inputs.
- `content/ai-engineer/v1/python/debugging/exercises.json` / `debugging-write`: generic_reference_answer. Expected: A topic-specific, fully specified task with a concrete worked answer, tested boundaries and an explanation tied to its actual inputs.
- `content/ai-engineer/v1/python/debugging/exercises.json` / `debugging-explain`: generic_reference_answer. Expected: A topic-specific, fully specified task with a concrete worked answer, tested boundaries and an explanation tied to its actual inputs.
- `content/ai-engineer/v1/python/functions/exercises.json` / `functions-tradeoff`: generic_objective_question. Expected: A topic-specific, fully specified task with a concrete worked answer, tested boundaries and an explanation tied to its actual inputs.
- `content/ai-engineer/v1/python/functions/exercises.json` / `functions-failure`: generic_objective_question. Expected: A topic-specific, fully specified task with a concrete worked answer, tested boundaries and an explanation tied to its actual inputs.
- `content/ai-engineer/v1/python/functions/exercises.json` / `functions-predict`: generic_reference_answer. Expected: A topic-specific, fully specified task with a concrete worked answer, tested boundaries and an explanation tied to its actual inputs.
- `content/ai-engineer/v1/python/functions/exercises.json` / `functions-fix`: generic_reference_answer. Expected: A topic-specific, fully specified task with a concrete worked answer, tested boundaries and an explanation tied to its actual inputs.
- `content/ai-engineer/v1/python/functions/exercises.json` / `functions-fix`: missing_program_contract. Expected: A topic-specific, fully specified task with a concrete worked answer, tested boundaries and an explanation tied to its actual inputs.
- `content/ai-engineer/v1/python/functions/exercises.json` / `functions-write`: generic_reference_answer. Expected: A topic-specific, fully specified task with a concrete worked answer, tested boundaries and an explanation tied to its actual inputs.
- `content/ai-engineer/v1/python/functions/exercises.json` / `functions-explain`: generic_reference_answer. Expected: A topic-specific, fully specified task with a concrete worked answer, tested boundaries and an explanation tied to its actual inputs.
- `content/ai-engineer/v1/python/syntax-data-types/exercises.json` / `syntaxdataty-tradeoff`: generic_objective_question. Expected: A topic-specific, fully specified task with a concrete worked answer, tested boundaries and an explanation tied to its actual inputs.
- `content/ai-engineer/v1/python/syntax-data-types/exercises.json` / `syntaxdataty-failure`: generic_objective_question. Expected: A topic-specific, fully specified task with a concrete worked answer, tested boundaries and an explanation tied to its actual inputs.
- `content/ai-engineer/v1/python/syntax-data-types/exercises.json` / `syntaxdataty-predict`: generic_reference_answer. Expected: A topic-specific, fully specified task with a concrete worked answer, tested boundaries and an explanation tied to its actual inputs.
- `content/ai-engineer/v1/python/syntax-data-types/exercises.json` / `syntaxdataty-fix`: generic_reference_answer. Expected: A topic-specific, fully specified task with a concrete worked answer, tested boundaries and an explanation tied to its actual inputs.
- `content/ai-engineer/v1/python/syntax-data-types/exercises.json` / `syntaxdataty-fix`: missing_program_contract. Expected: A topic-specific, fully specified task with a concrete worked answer, tested boundaries and an explanation tied to its actual inputs.
- `content/ai-engineer/v1/python/syntax-data-types/exercises.json` / `syntaxdataty-write`: generic_reference_answer. Expected: A topic-specific, fully specified task with a concrete worked answer, tested boundaries and an explanation tied to its actual inputs.
- `content/ai-engineer/v1/python/syntax-data-types/exercises.json` / `syntaxdataty-explain`: generic_reference_answer. Expected: A topic-specific, fully specified task with a concrete worked answer, tested boundaries and an explanation tied to its actual inputs.
- `content/ai-engineer/v1/sql-postgresql/transactions/exercises.json` / `transactions-tradeoff`: generic_objective_question. Expected: A topic-specific, fully specified task with a concrete worked answer, tested boundaries and an explanation tied to its actual inputs.
- `content/ai-engineer/v1/sql-postgresql/transactions/exercises.json` / `transactions-failure`: generic_objective_question. Expected: A topic-specific, fully specified task with a concrete worked answer, tested boundaries and an explanation tied to its actual inputs.
- `content/ai-engineer/v1/sql-postgresql/transactions/exercises.json` / `transactions-predict`: generic_reference_answer. Expected: A topic-specific, fully specified task with a concrete worked answer, tested boundaries and an explanation tied to its actual inputs.
- `content/ai-engineer/v1/sql-postgresql/transactions/exercises.json` / `transactions-fix`: generic_reference_answer. Expected: A topic-specific, fully specified task with a concrete worked answer, tested boundaries and an explanation tied to its actual inputs.
- `content/ai-engineer/v1/sql-postgresql/transactions/exercises.json` / `transactions-fix`: missing_program_contract. Expected: A topic-specific, fully specified task with a concrete worked answer, tested boundaries and an explanation tied to its actual inputs.
- `content/ai-engineer/v1/sql-postgresql/transactions/exercises.json` / `transactions-write`: generic_reference_answer. Expected: A topic-specific, fully specified task with a concrete worked answer, tested boundaries and an explanation tied to its actual inputs.
- `content/ai-engineer/v1/sql-postgresql/transactions/exercises.json` / `transactions-explain`: generic_reference_answer. Expected: A topic-specific, fully specified task with a concrete worked answer, tested boundaries and an explanation tied to its actual inputs.
- `content/ai-engineer/v1/sql-postgresql/window-functions/exercises.json` / `windowfuncti-tradeoff`: generic_objective_question. Expected: A topic-specific, fully specified task with a concrete worked answer, tested boundaries and an explanation tied to its actual inputs.
- `content/ai-engineer/v1/sql-postgresql/window-functions/exercises.json` / `windowfuncti-failure`: generic_objective_question. Expected: A topic-specific, fully specified task with a concrete worked answer, tested boundaries and an explanation tied to its actual inputs.
- `content/ai-engineer/v1/sql-postgresql/window-functions/exercises.json` / `windowfuncti-predict`: generic_reference_answer. Expected: A topic-specific, fully specified task with a concrete worked answer, tested boundaries and an explanation tied to its actual inputs.
- `content/ai-engineer/v1/sql-postgresql/window-functions/exercises.json` / `windowfuncti-fix`: generic_reference_answer. Expected: A topic-specific, fully specified task with a concrete worked answer, tested boundaries and an explanation tied to its actual inputs.
- `content/ai-engineer/v1/sql-postgresql/window-functions/exercises.json` / `windowfuncti-fix`: missing_program_contract. Expected: A topic-specific, fully specified task with a concrete worked answer, tested boundaries and an explanation tied to its actual inputs.
- `content/ai-engineer/v1/sql-postgresql/window-functions/exercises.json` / `windowfuncti-write`: generic_reference_answer. Expected: A topic-specific, fully specified task with a concrete worked answer, tested boundaries and an explanation tied to its actual inputs.
- `content/ai-engineer/v1/sql-postgresql/window-functions/exercises.json` / `windowfuncti-explain`: generic_reference_answer. Expected: A topic-specific, fully specified task with a concrete worked answer, tested boundaries and an explanation tied to its actual inputs.

## Incorrect Arena transfer directions

- `content/ai-engineer/v1/python/async-await/lesson.json` / `interview-summary`: tells the reader ordinary related Arena solves count as clean transfer. The runtime uses a distinct Arena source, requires approved content for new credit, and reserves clean transfer for the eligible unseen transfer context. Correct in a new candidate; do not rewrite old evidence.
- `content/ai-engineer/v1/python/collections/lesson.json` / `interview-summary`: tells the reader ordinary related Arena solves count as clean transfer. The runtime uses a distinct Arena source, requires approved content for new credit, and reserves clean transfer for the eligible unseen transfer context. Correct in a new candidate; do not rewrite old evidence.
- `content/ai-engineer/v1/python/debugging/lesson.json` / `interview-summary`: tells the reader ordinary related Arena solves count as clean transfer. The runtime uses a distinct Arena source, requires approved content for new credit, and reserves clean transfer for the eligible unseen transfer context. Correct in a new candidate; do not rewrite old evidence.
- `content/ai-engineer/v1/python/functions/lesson.json` / `interview-summary`: tells the reader ordinary related Arena solves count as clean transfer. The runtime uses a distinct Arena source, requires approved content for new credit, and reserves clean transfer for the eligible unseen transfer context. Correct in a new candidate; do not rewrite old evidence.
- `content/ai-engineer/v1/python/syntax-data-types/lesson.json` / `interview-summary`: tells the reader ordinary related Arena solves count as clean transfer. The runtime uses a distinct Arena source, requires approved content for new credit, and reserves clean transfer for the eligible unseen transfer context. Correct in a new candidate; do not rewrite old evidence.

## Every independently failing Python example

- `content/ai-engineer/v1/dsa/backtracking/lesson.json` / `arena-transfer` / example0: displayed stdout differs. Supply a complete runnable block, explicit environment/setup, or a correct portable expected output. Exact result is in independent-browser.json.
- `content/ai-engineer/v1/dsa/bfs/lesson.json` / `arena-transfer` / example0: NameError (name 'deque' is not defined). Supply a complete runnable block, explicit environment/setup, or a correct portable expected output. Exact result is in independent-browser.json.
- `content/ai-engineer/v1/dsa/big-o/lesson.json` / `worst-case-vs-amortized` / example0: displayed stdout differs. Supply a complete runnable block, explicit environment/setup, or a correct portable expected output. Exact result is in independent-browser.json.
- `content/ai-engineer/v1/dsa/binary-search/lesson.json` / `arena-transfer` / example0: NameError (name 'lower_bound' is not defined). Supply a complete runnable block, explicit environment/setup, or a correct portable expected output. Exact result is in independent-browser.json.
- `content/ai-engineer/v1/dsa/graphs/lesson.json` / `arena-transfer` / example0: NameError (name 'deque' is not defined). Supply a complete runnable block, explicit environment/setup, or a correct portable expected output. Exact result is in independent-browser.json.
- `content/ai-engineer/v1/dsa/linked-lists/lesson.json` / `in-place-reversal` / example0: NameError (name 'ListNode' is not defined). Supply a complete runnable block, explicit environment/setup, or a correct portable expected output. Exact result is in independent-browser.json.
- `content/ai-engineer/v1/dsa/linked-lists/lesson.json` / `dummy-node-technique` / example0: NameError (name 'ListNode' is not defined). Supply a complete runnable block, explicit environment/setup, or a correct portable expected output. Exact result is in independent-browser.json.
- `content/ai-engineer/v1/dsa/linked-lists/lesson.json` / `fast-slow-pointer-and-cycles` / example0: NameError (name 'ListNode' is not defined). Supply a complete runnable block, explicit environment/setup, or a correct portable expected output. Exact result is in independent-browser.json.
- `content/ai-engineer/v1/dsa/linked-lists/lesson.json` / `arena-transfer` / example0: NameError (name 'ListNode' is not defined). Supply a complete runnable block, explicit environment/setup, or a correct portable expected output. Exact result is in independent-browser.json.
- `content/ai-engineer/v1/dsa/queues/lesson.json` / `arena-transfer` / example0: displayed stdout differs. Supply a complete runnable block, explicit environment/setup, or a correct portable expected output. Exact result is in independent-browser.json.
- `content/ai-engineer/v1/python/comprehensions/lesson.json` / `generator-expressions` / example0: displayed stdout differs. Supply a complete runnable block, explicit environment/setup, or a correct portable expected output. Exact result is in independent-browser.json.
- `content/ai-engineer/v1/python/decorators/lesson.json` / `interview-check` / example0: NameError (name 'functools' is not defined). Supply a complete runnable block, explicit environment/setup, or a correct portable expected output. Exact result is in independent-browser.json.
- `content/ai-engineer/v1/python/testing/lesson.json` / `pytest-assertions` / example0: ModuleNotFoundError (No module named 'pytest'). Supply a complete runnable block, explicit environment/setup, or a correct portable expected output. Exact result is in independent-browser.json.
- `content/ai-engineer/v1/python/testing/lesson.json` / `fixtures-and-dependency-injection` / example0: ModuleNotFoundError (No module named 'pytest'). Supply a complete runnable block, explicit environment/setup, or a correct portable expected output. Exact result is in independent-browser.json.
- `content/ai-engineer/v1/python/virtual-environments/lesson.json` / `why-isolation-matters` / example0: displayed stdout differs. Supply a complete runnable block, explicit environment/setup, or a correct portable expected output. Exact result is in independent-browser.json.
- `content/ai-engineer/v1/python/virtual-environments/lesson.json` / `activation-and-path-mechanics` / example0: displayed stdout differs. Supply a complete runnable block, explicit environment/setup, or a correct portable expected output. Exact result is in independent-browser.json.
- `content/ai-engineer/v1/python/virtual-environments/lesson.json` / `interpreter-selection` / example0: displayed stdout differs. Supply a complete runnable block, explicit environment/setup, or a correct portable expected output. Exact result is in independent-browser.json.
- `content/ai-engineer/v1/python/virtual-environments/lesson.json` / `interview-check` / example0: displayed stdout differs. Supply a complete runnable block, explicit environment/setup, or a correct portable expected output. Exact result is in independent-browser.json.
- `content/ai-engineer/v1/sql-postgresql/database-python/lesson.json` / `connections-and-cursors` / example1: ModuleNotFoundError (No module named 'psycopg'). Supply a complete runnable block, explicit environment/setup, or a correct portable expected output. Exact result is in independent-browser.json.
- `content/ai-engineer/v1/sql-postgresql/database-python/lesson.json` / `parameterized-queries-and-security` / example1: NameError (name 'cur' is not defined). Supply a complete runnable block, explicit environment/setup, or a correct portable expected output. Exact result is in independent-browser.json.
- `content/ai-engineer/v1/sql-postgresql/database-python/lesson.json` / `transaction-boundaries` / example0: NameError (name 'conn' is not defined). Supply a complete runnable block, explicit environment/setup, or a correct portable expected output. Exact result is in independent-browser.json.
- `content/ai-engineer/v1/sql-postgresql/database-python/lesson.json` / `orm-and-sqlalchemy` / example0: ModuleNotFoundError (No module named 'sqlalchemy'). Supply a complete runnable block, explicit environment/setup, or a correct portable expected output. Exact result is in independent-browser.json.
- `content/ai-engineer/v1/sql-postgresql/database-python/lesson.json` / `interview-check` / example0: NameError (name 'cur' is not defined). Supply a complete runnable block, explicit environment/setup, or a correct portable expected output. Exact result is in independent-browser.json.

## Every SQL setup failure

- `content/ai-engineer/v1/sql-postgresql/aggregation/lesson.json` / `having-vs-where` / example0: relation "employees" does not exist. Declare a fresh-database fixture or explicit prerequisite setup; this is not automatically a wrong SQL algorithm.
- `content/ai-engineer/v1/sql-postgresql/aggregation/lesson.json` / `null-handling-in-aggregation` / example0: relation "employees" does not exist. Declare a fresh-database fixture or explicit prerequisite setup; this is not automatically a wrong SQL algorithm.
- `content/ai-engineer/v1/sql-postgresql/aggregation/lesson.json` / `interview-check` / example0: relation "employees" does not exist. Declare a fresh-database fixture or explicit prerequisite setup; this is not automatically a wrong SQL algorithm.
- `content/ai-engineer/v1/sql-postgresql/constraints-design/lesson.json` / `interview-check` / example0: relation "accounts" does not exist. Declare a fresh-database fixture or explicit prerequisite setup; this is not automatically a wrong SQL algorithm.
- `content/ai-engineer/v1/sql-postgresql/data-modification/lesson.json` / `update-operations` / example0: relation "products" does not exist. Declare a fresh-database fixture or explicit prerequisite setup; this is not automatically a wrong SQL algorithm.
- `content/ai-engineer/v1/sql-postgresql/data-modification/lesson.json` / `delete-operations` / example0: relation "products" does not exist. Declare a fresh-database fixture or explicit prerequisite setup; this is not automatically a wrong SQL algorithm.
- `content/ai-engineer/v1/sql-postgresql/data-modification/lesson.json` / `interview-check` / example0: relation "products" does not exist. Declare a fresh-database fixture or explicit prerequisite setup; this is not automatically a wrong SQL algorithm.
- `content/ai-engineer/v1/sql-postgresql/database-python/lesson.json` / `parameterized-queries-and-security` / example0: relation "users" does not exist. Declare a fresh-database fixture or explicit prerequisite setup; this is not automatically a wrong SQL algorithm.
- `content/ai-engineer/v1/sql-postgresql/indexes/lesson.json` / `explain-and-query-plans` / example0: relation "orders" does not exist. Declare a fresh-database fixture or explicit prerequisite setup; this is not automatically a wrong SQL algorithm.
- `content/ai-engineer/v1/sql-postgresql/indexes/lesson.json` / `interview-check` / example0: relation "customers" does not exist. Declare a fresh-database fixture or explicit prerequisite setup; this is not automatically a wrong SQL algorithm.
- `content/ai-engineer/v1/sql-postgresql/joins/lesson.json` / `outer-joins-left-right-full` / example0: relation "customers" does not exist. Declare a fresh-database fixture or explicit prerequisite setup; this is not automatically a wrong SQL algorithm.
- `content/ai-engineer/v1/sql-postgresql/joins/lesson.json` / `multi-table-joins-and-cartesian` / example0: relation "customers" does not exist. Declare a fresh-database fixture or explicit prerequisite setup; this is not automatically a wrong SQL algorithm.
- `content/ai-engineer/v1/sql-postgresql/joins/lesson.json` / `join-filtering-pitfalls` / example0: relation "customers" does not exist. Declare a fresh-database fixture or explicit prerequisite setup; this is not automatically a wrong SQL algorithm.
- `content/ai-engineer/v1/sql-postgresql/joins/lesson.json` / `interview-check` / example0: relation "customers" does not exist. Declare a fresh-database fixture or explicit prerequisite setup; this is not automatically a wrong SQL algorithm.
- `content/ai-engineer/v1/sql-postgresql/postgresql-practicals/lesson.json` / `interview-check` / example0: relation "model_configs" does not exist. Declare a fresh-database fixture or explicit prerequisite setup; this is not automatically a wrong SQL algorithm.
- `content/ai-engineer/v1/sql-postgresql/query-basics/lesson.json` / `where-filtering-and-logic` / example0: relation "employees" does not exist. Declare a fresh-database fixture or explicit prerequisite setup; this is not automatically a wrong SQL algorithm.
- `content/ai-engineer/v1/sql-postgresql/query-basics/lesson.json` / `in-between-and-like` / example0: relation "employees" does not exist. Declare a fresh-database fixture or explicit prerequisite setup; this is not automatically a wrong SQL algorithm.
- `content/ai-engineer/v1/sql-postgresql/query-basics/lesson.json` / `order-by-and-nulls` / example0: relation "employees" does not exist. Declare a fresh-database fixture or explicit prerequisite setup; this is not automatically a wrong SQL algorithm.
- `content/ai-engineer/v1/sql-postgresql/query-basics/lesson.json` / `limit-and-offset-pagination` / example0: relation "employees" does not exist. Declare a fresh-database fixture or explicit prerequisite setup; this is not automatically a wrong SQL algorithm.
- `content/ai-engineer/v1/sql-postgresql/query-basics/lesson.json` / `interview-check` / example0: relation "employees" does not exist. Declare a fresh-database fixture or explicit prerequisite setup; this is not automatically a wrong SQL algorithm.
- `content/ai-engineer/v1/sql-postgresql/subqueries/lesson.json` / `set-membership-in-any-all` / example0: relation "employees" does not exist. Declare a fresh-database fixture or explicit prerequisite setup; this is not automatically a wrong SQL algorithm.
- `content/ai-engineer/v1/sql-postgresql/subqueries/lesson.json` / `correlated-subqueries-and-exists` / example0: relation "employees" does not exist. Declare a fresh-database fixture or explicit prerequisite setup; this is not automatically a wrong SQL algorithm.
- `content/ai-engineer/v1/sql-postgresql/subqueries/lesson.json` / `interview-check` / example0: relation "employees" does not exist. Declare a fresh-database fixture or explicit prerequisite setup; this is not automatically a wrong SQL algorithm.
- `content/ai-engineer/v1/sql-postgresql/transactions/lesson.json` / `acid` / example0: relation "accounts" does not exist. Declare a fresh-database fixture or explicit prerequisite setup; this is not automatically a wrong SQL algorithm.
- `content/ai-engineer/v1/sql-postgresql/transactions/lesson.json` / `boundaries` / example0: relation "reservations" does not exist. Declare a fresh-database fixture or explicit prerequisite setup; this is not automatically a wrong SQL algorithm.
- `content/ai-engineer/v1/sql-postgresql/transactions/lesson.json` / `constraints` / example0: relation "inventory" does not exist. Declare a fresh-database fixture or explicit prerequisite setup; this is not automatically a wrong SQL algorithm.
- `content/ai-engineer/v1/sql-postgresql/transactions/lesson.json` / `concurrency` / example0: relation "inventory" does not exist. Declare a fresh-database fixture or explicit prerequisite setup; this is not automatically a wrong SQL algorithm.
- `content/ai-engineer/v1/sql-postgresql/window-functions/lesson.json` / `window-model` / example0: relation "sales" does not exist. Declare a fresh-database fixture or explicit prerequisite setup; this is not automatically a wrong SQL algorithm.
- `content/ai-engineer/v1/sql-postgresql/window-functions/lesson.json` / `ranking` / example0: relation "scores" does not exist. Declare a fresh-database fixture or explicit prerequisite setup; this is not automatically a wrong SQL algorithm.
- `content/ai-engineer/v1/sql-postgresql/window-functions/lesson.json` / `partitioned-ranking` / example0: relation "employees" does not exist. Declare a fresh-database fixture or explicit prerequisite setup; this is not automatically a wrong SQL algorithm.
- `content/ai-engineer/v1/sql-postgresql/window-functions/lesson.json` / `offset-functions` / example0: relation "monthly_revenue" does not exist. Declare a fresh-database fixture or explicit prerequisite setup; this is not automatically a wrong SQL algorithm.
- `content/ai-engineer/v1/sql-postgresql/window-functions/lesson.json` / `running-frames` / example0: relation "sales" does not exist. Declare a fresh-database fixture or explicit prerequisite setup; this is not automatically a wrong SQL algorithm.

## Per-lesson review ledger

All53 are historical unverified teaching, not independently reviewed Placement Foundations releases. The ledger records exact inspection scope without granting editorial approval.

- `content/ai-engineer/v1/dsa/arrays/lesson.json`: 7 exercises, 2 example blocks; 0 independent execution/context failures. Flags: generic_objective_question:2, generic_reference_answer:4, missing_program_contract:1.
- `content/ai-engineer/v1/dsa/backtracking/lesson.json`: 7 exercises, 5 example blocks; 1 independent execution/context failures. Flags: No template detector hit; full human semantic review still required.
- `content/ai-engineer/v1/dsa/bfs/lesson.json`: 7 exercises, 5 example blocks; 1 independent execution/context failures. Flags: No template detector hit; full human semantic review still required.
- `content/ai-engineer/v1/dsa/big-o/lesson.json`: 7 exercises, 5 example blocks; 1 independent execution/context failures. Flags: No template detector hit; full human semantic review still required.
- `content/ai-engineer/v1/dsa/binary-search/lesson.json`: 7 exercises, 5 example blocks; 1 independent execution/context failures. Flags: No template detector hit; full human semantic review still required.
- `content/ai-engineer/v1/dsa/dfs/lesson.json`: 7 exercises, 5 example blocks; 0 independent execution/context failures. Flags: No template detector hit; full human semantic review still required.
- `content/ai-engineer/v1/dsa/dynamic-programming/lesson.json`: 7 exercises, 2 example blocks; 0 independent execution/context failures. Flags: generic_objective_question:2, generic_reference_answer:4, missing_program_contract:1.
- `content/ai-engineer/v1/dsa/graphs/lesson.json`: 7 exercises, 5 example blocks; 1 independent execution/context failures. Flags: No template detector hit; full human semantic review still required.
- `content/ai-engineer/v1/dsa/hash-maps/lesson.json`: 7 exercises, 2 example blocks; 0 independent execution/context failures. Flags: generic_objective_question:2, generic_reference_answer:4, missing_program_contract:1.
- `content/ai-engineer/v1/dsa/heaps/lesson.json`: 7 exercises, 5 example blocks; 0 independent execution/context failures. Flags: No template detector hit; full human semantic review still required.
- `content/ai-engineer/v1/dsa/linked-lists/lesson.json`: 7 exercises, 5 example blocks; 4 independent execution/context failures. Flags: No template detector hit; full human semantic review still required.
- `content/ai-engineer/v1/dsa/queues/lesson.json`: 7 exercises, 5 example blocks; 1 independent execution/context failures. Flags: No template detector hit; full human semantic review still required.
- `content/ai-engineer/v1/dsa/recursion/lesson.json`: 7 exercises, 5 example blocks; 0 independent execution/context failures. Flags: No template detector hit; full human semantic review still required.
- `content/ai-engineer/v1/dsa/sets/lesson.json`: 7 exercises, 5 example blocks; 0 independent execution/context failures. Flags: No template detector hit; full human semantic review still required.
- `content/ai-engineer/v1/dsa/sliding-window/lesson.json`: 7 exercises, 2 example blocks; 0 independent execution/context failures. Flags: generic_objective_question:2, generic_reference_answer:4, missing_program_contract:1.
- `content/ai-engineer/v1/dsa/sorting/lesson.json`: 7 exercises, 5 example blocks; 0 independent execution/context failures. Flags: No template detector hit; full human semantic review still required.
- `content/ai-engineer/v1/dsa/stacks/lesson.json`: 7 exercises, 5 example blocks; 0 independent execution/context failures. Flags: No template detector hit; full human semantic review still required.
- `content/ai-engineer/v1/dsa/strings/lesson.json`: 7 exercises, 5 example blocks; 0 independent execution/context failures. Flags: No template detector hit; full human semantic review still required.
- `content/ai-engineer/v1/dsa/trees/lesson.json`: 7 exercises, 2 example blocks; 0 independent execution/context failures. Flags: generic_objective_question:2, generic_reference_answer:4, missing_program_contract:1.
- `content/ai-engineer/v1/dsa/two-pointers/lesson.json`: 7 exercises, 2 example blocks; 0 independent execution/context failures. Flags: generic_objective_question:2, generic_reference_answer:4, missing_program_contract:1.
- `content/ai-engineer/v1/python/async-await/lesson.json`: 7 exercises, 3 example blocks; 0 independent execution/context failures. Flags: repeated_worked_example:1, arena_transfer_claim:1, generic_objective_question:2, generic_reference_answer:4, missing_program_contract:1.
- `content/ai-engineer/v1/python/collections/lesson.json`: 7 exercises, 3 example blocks; 0 independent execution/context failures. Flags: repeated_worked_example:1, arena_transfer_claim:1, generic_objective_question:2, generic_reference_answer:4, missing_program_contract:1.
- `content/ai-engineer/v1/python/comprehensions/lesson.json`: 7 exercises, 6 example blocks; 1 independent execution/context failures. Flags: No template detector hit; full human semantic review still required.
- `content/ai-engineer/v1/python/control-flow/lesson.json`: 7 exercises, 7 example blocks; 0 independent execution/context failures. Flags: No template detector hit; full human semantic review still required.
- `content/ai-engineer/v1/python/debugging/lesson.json`: 7 exercises, 3 example blocks; 0 independent execution/context failures. Flags: repeated_worked_example:1, arena_transfer_claim:1, generic_objective_question:2, generic_reference_answer:4, missing_program_contract:1.
- `content/ai-engineer/v1/python/decorators/lesson.json`: 7 exercises, 6 example blocks; 1 independent execution/context failures. Flags: No template detector hit; full human semantic review still required.
- `content/ai-engineer/v1/python/exceptions/lesson.json`: 7 exercises, 6 example blocks; 0 independent execution/context failures. Flags: No template detector hit; full human semantic review still required.
- `content/ai-engineer/v1/python/file-handling/lesson.json`: 7 exercises, 6 example blocks; 0 independent execution/context failures. Flags: No template detector hit; full human semantic review still required.
- `content/ai-engineer/v1/python/functions/lesson.json`: 7 exercises, 3 example blocks; 0 independent execution/context failures. Flags: repeated_worked_example:1, arena_transfer_claim:1, generic_objective_question:2, generic_reference_answer:4, missing_program_contract:1.
- `content/ai-engineer/v1/python/generators/lesson.json`: 7 exercises, 6 example blocks; 0 independent execution/context failures. Flags: No template detector hit; full human semantic review still required.
- `content/ai-engineer/v1/python/iterators/lesson.json`: 7 exercises, 6 example blocks; 0 independent execution/context failures. Flags: No template detector hit; full human semantic review still required.
- `content/ai-engineer/v1/python/modules-packages/lesson.json`: 7 exercises, 6 example blocks; 0 independent execution/context failures. Flags: No template detector hit; full human semantic review still required.
- `content/ai-engineer/v1/python/oop/lesson.json`: 7 exercises, 6 example blocks; 0 independent execution/context failures. Flags: No template detector hit; full human semantic review still required.
- `content/ai-engineer/v1/python/reading-unfamiliar-code/lesson.json`: 7 exercises, 6 example blocks; 0 independent execution/context failures. Flags: No template detector hit; full human semantic review still required.
- `content/ai-engineer/v1/python/strings/lesson.json`: 7 exercises, 6 example blocks; 0 independent execution/context failures. Flags: No template detector hit; full human semantic review still required.
- `content/ai-engineer/v1/python/syntax-data-types/lesson.json`: 7 exercises, 5 example blocks; 0 independent execution/context failures. Flags: repeated_worked_example:1, arena_transfer_claim:1, generic_objective_question:2, generic_reference_answer:4, missing_program_contract:1.
- `content/ai-engineer/v1/python/testing/lesson.json`: 7 exercises, 6 example blocks; 2 independent execution/context failures. Flags: No template detector hit; full human semantic review still required.
- `content/ai-engineer/v1/python/type-hints/lesson.json`: 7 exercises, 6 example blocks; 0 independent execution/context failures. Flags: No template detector hit; full human semantic review still required.
- `content/ai-engineer/v1/python/virtual-environments/lesson.json`: 7 exercises, 6 example blocks; 4 independent execution/context failures. Flags: No template detector hit; full human semantic review still required.
- `content/ai-engineer/v1/sql-postgresql/aggregation/lesson.json`: 7 exercises, 5 example blocks; 3 independent execution/context failures. Flags: No template detector hit; full human semantic review still required.
- `content/ai-engineer/v1/sql-postgresql/constraints-design/lesson.json`: 7 exercises, 5 example blocks; 1 independent execution/context failures. Flags: No template detector hit; full human semantic review still required.
- `content/ai-engineer/v1/sql-postgresql/ctes/lesson.json`: 7 exercises, 5 example blocks; 0 independent execution/context failures. Flags: No template detector hit; full human semantic review still required.
- `content/ai-engineer/v1/sql-postgresql/data-modification/lesson.json`: 7 exercises, 5 example blocks; 3 independent execution/context failures. Flags: No template detector hit; full human semantic review still required.
- `content/ai-engineer/v1/sql-postgresql/database-python/lesson.json`: 7 exercises, 7 example blocks; 6 independent execution/context failures. Flags: No template detector hit; full human semantic review still required.
- `content/ai-engineer/v1/sql-postgresql/indexes/lesson.json`: 7 exercises, 5 example blocks; 2 independent execution/context failures. Flags: No template detector hit; full human semantic review still required.
- `content/ai-engineer/v1/sql-postgresql/joins/lesson.json`: 7 exercises, 6 example blocks; 4 independent execution/context failures. Flags: No template detector hit; full human semantic review still required.
- `content/ai-engineer/v1/sql-postgresql/postgresql-practicals/lesson.json`: 7 exercises, 5 example blocks; 1 independent execution/context failures. Flags: No template detector hit; full human semantic review still required.
- `content/ai-engineer/v1/sql-postgresql/query-basics/lesson.json`: 7 exercises, 6 example blocks; 5 independent execution/context failures. Flags: No template detector hit; full human semantic review still required.
- `content/ai-engineer/v1/sql-postgresql/relational-foundations/lesson.json`: 7 exercises, 5 example blocks; 0 independent execution/context failures. Flags: No template detector hit; full human semantic review still required.
- `content/ai-engineer/v1/sql-postgresql/subqueries/lesson.json`: 7 exercises, 5 example blocks; 3 independent execution/context failures. Flags: No template detector hit; full human semantic review still required.
- `content/ai-engineer/v1/sql-postgresql/transactions/lesson.json`: 7 exercises, 5 example blocks; 4 independent execution/context failures. Flags: generic_objective_question:2, generic_reference_answer:4, missing_program_contract:1.
- `content/ai-engineer/v1/sql-postgresql/values-expressions/lesson.json`: 7 exercises, 5 example blocks; 0 independent execution/context failures. Flags: No template detector hit; full human semantic review still required.
- `content/ai-engineer/v1/sql-postgresql/window-functions/lesson.json`: 7 exercises, 5 example blocks; 5 independent execution/context failures. Flags: generic_objective_question:2, generic_reference_answer:4, missing_program_contract:1.

## Provenance and accepted teaching status

The53 lessons cite sources but contain no new independent human attestation. Historical adapted/declared-original problem claims retain unresolved provenance/license chains; originality was not inferred from a JSON label. This audit does not accuse a source of copying without a verified comparison, and does not clear any historical redistribution blocker.

The18 existing Phase5 candidates were independently revalidated, still with0 reviews/releases. Their candidate pools are shallow and generic hints/transfer-independence claims need careful review. A structural pass does not establish a genuine transfer variant or good teaching.

## New correction drafts and exact review work

Five new1.2.0 lesson candidates are under `data/content-approvals/independent-audit/`: Functions, Exceptions, Type Hints, Control Flow and SQL Indexes. Functions replaces all seven template exercises and executes six exact Python examples. Indexes supplies four deterministic SQL fixtures and explicitly treats its EXPLAIN plan as environment-dependent. The other three are focused factual patches and inherit additional example/pedagogical review work. Their context declarations are not execution certifications.

All five have validation reports, exact digests, source references, worked answers, review packets and all-false checklists. No human identity, approval or publication was invented. Corrected Two Sum1.0.1 remains an existing separate candidate.

Finish outstanding drafts/fixtures, review alternative valid answers and grading scope, then obtain a real named independent human review. Only after all checks are genuinely satisfied may the existing publication CLI create a release targeting an exact confirmed graph. The original historical files remain unchanged.
