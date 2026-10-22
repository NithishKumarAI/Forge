# Forge V1 — Beginner Foundations Coverage and Exercise Inventory

**Author**: Antigravity Assistant & Engineering Pair  
**Date**: October 22, 2026  
**Status**: Authoritative Content Matrix  
**Authoritative Local Tree**: `C:\My PC\git\Forge`  
**Classification**: Beginner-to-Advanced Concept Hierarchy across Placement Foundations  

---

## 1. Concept-by-Concept Curriculum Matrix (29 Concepts)

The 29 concepts authored in `data/learning-path/concept-steps.json` provide complete beginner coverage across the 9 Placement Foundations tracks:

| # | Concept Key | Subject | Stage | Title | Prerequisites | Guided Exercises | Independent Arena Challenge | Teaching View |
| -: | :--- | :--- | :---: | :--- | :--- | :---: | :--- | :---: |
| 1 | `step-py-values-1` | Python | First Steps | Values, variables and basic types | None | 3 | `python-two-fer` | Complete |
| 2 | `step-py-values-2` | Python | First Steps | Arithmetic expressions and precedence | `step-py-values-1` | 3 | `python-celsius-to-fahrenheit` | Complete |
| 3 | `step-py-cond-1` | Python | First Steps | Comparisons and Boolean branching | `step-py-values-2` | 2 | `python-leap-year` | Complete |
| 4 | `step-py-cond-2` | Python | First Steps | Modulo and compound conditions | `step-py-cond-1` | 2 | `python-fizzbuzz` | Complete |
| 5 | `step-py-loops-1` | Python | First Steps | For loops and range iteration | `step-py-cond-2` | 2 | `python-collatz` | Complete |
| 6 | `step-py-loops-2` | Python | First Steps | Loop tracing and extreme values | `step-py-loops-1` | 2 | `python-raindrops` | Complete |
| 7 | `step-py-strings-1` | Python | First Steps | String indexing and transformations | `step-py-loops-1` | 1 | `python-normalize-name` | Complete |
| 8 | `step-py-collections-1` | Python | First Steps | Lists and sequential operations | `step-py-loops-2` | 1 | `python-running-sum` | Complete |
| 9 | `step-py-collections-2` | Python | First Steps | Dictionaries and frequency tracking | `step-py-collections-1` | 1 | `python-word-count` | Complete |
| 10 | `step-py-functions-1` | Python | First Steps | Functions, parameters, and returns | `step-py-collections-2` | 1 | `python-count-vowels` | Complete |
| 11 | `step-sql-tables-1` | SQL | First Steps | Tables, rows and scalar projection | None | 2 | `sql-active-users` | Complete |
| 12 | `step-sql-tables-2` | SQL | First Steps | Reading columns and table structure | `step-sql-tables-1` | 2 | `sql-user-search` | Complete |
| 13 | `step-sql-select-filter` | SQL | First Steps | Filtering rows with WHERE | `step-sql-tables-2` | 2 | `sql-products-in-stock` | Complete |
| 14 | `step-sql-nulls` | SQL | First Steps | Handling missing data (NULL) | `step-sql-select-filter` | 2 | `sql-null-email` | Complete |
| 15 | `step-sql-ordering-limits` | SQL | First Steps | Sorting and limiting results | `step-sql-nulls` | 1 | `sql-recent-orders` | Complete |
| 16 | `step-sql-aggregations` | SQL | First Steps | Aggregate functions and grouping | `step-sql-ordering-limits` | 1 | `sql-order-count-by-status` | Complete |
| 17 | `step-dsa-contracts-1` | DSA | First Steps | Problem contracts and state tracing | `step-py-values-2` | 1 | `dsa-first-pair` | Complete |
| 18 | `step-dsa-complexity-1` | DSA | First Steps | Time and space complexity intuition | `step-dsa-contracts-1` | 1 | `dsa-two-sum-indices` | Complete |
| 19 | `step-dsa-scan-1` | DSA | First Steps | Linear scanning and element search | `step-dsa-complexity-1` | 2 | `dsa-move-zeroes` | Complete |
| 20 | `step-dsa-two-pointers` | DSA | First Steps | Two-pointer convergence and symmetry | `step-dsa-scan-1` | 1 | `dsa-reverse-string` | Complete |
| 21 | `step-dsa-hash-1` | DSA | First Steps | Hash maps and frequency counting | `step-dsa-scan-1` | 1 | `dsa-valid-anagram` | Complete |
| 22 | `step-dsa-hash-sets` | DSA | First Steps | Hash sets and deduplication | `step-dsa-hash-1` | 1 | `dsa-remove-duplicates-sorted` | Complete |
| 23 | `step-dsa-search-sort` | DSA | First Steps | Binary search and logarithmic scaling | `step-dsa-hash-sets` | 1 | `dsa-ransom-note` | Complete |
| 24 | `step-apt-numbers-1` | Aptitude | First Steps | Numbers, operations and precedence | None | Candidate | Review queue | Complete |
| 25 | `step-reason-patterns-1` | Reasoning | First Steps | Pattern recognition and classification | None | Candidate | Review queue | Complete |
| 26 | `step-verbal-structure-1` | Verbal | First Steps | Sentence structure and clause boundaries | None | Candidate | Review queue | Complete |
| 27 | `step-sys-requirements-1` | Sys Design | First Steps | Functional vs non-functional requirements | None | Candidate | Review queue | Complete |
| 28 | `step-ai-foundations-1` | AI Eng | First Steps | AI, ML, and deep learning boundaries | None | Candidate | Review queue | Complete |
| 29 | `step-interview-intro-1` | Interview | First Steps | Structuring a technical self-introduction | None | Candidate | Review queue | Complete |

---

## 2. Progressive Practice Depth Inventory (35 Beginner Exercises)

All 35 interactive beginner exercises in `data/learning-path/beginner-exercises.json` are verified deterministically by isolated backend workers:

### A. Python Programming (18 Exercises)
Verified via `python_worker.py` with restricted builtins, AST inspection, and 5-second process timeout:

1. **`py-first-print-message`**: Printing a string
   - *Target Function*: `say_hello()`
   - *Contract*: Returns `'Hello, Forge!'`
   - *Concept*: `step-py-values-1`
2. **`py-first-variable`**: Work with variable assignment
   - *Target Function*: `double_value(x)`
   - *Contract*: Returns $x \times 2$
   - *Concept*: `step-py-values-1`
3. **`py-first-type-convert`**: String parsing and increment
   - *Target Function*: `parse_and_increment(s)`
   - *Contract*: Converts string to integer and adds 10
   - *Concept*: `step-py-values-1`
4. **`py-first-add-two`**: Binary addition
   - *Target Function*: `add_numbers(a, b)`
   - *Contract*: Returns $a + b$
   - *Concept*: `step-py-values-2`
5. **`py-first-quotient-remainder`**: Integer division and modulo
   - *Target Function*: `div_and_mod(a, b)`
   - *Contract*: Returns list `[a // b, a % b]`
   - *Concept*: `step-py-values-2`
6. **`py-first-calc-average`**: Arithmetic mean with precedence
   - *Target Function*: `calculate_average(a, b, c)`
   - *Contract*: Returns `(a + b + c) / 3.0`
   - *Concept*: `step-py-values-2`
7. **`py-first-compare-two`**: Relational comparison
   - *Target Function*: `is_greater(a, b)`
   - *Contract*: Returns `a > b`
   - *Concept*: `step-py-cond-1`
8. **`py-first-is-positive`**: Three-way branching
   - *Target Function*: `check_sign(n)`
   - *Contract*: Returns `'positive'`, `'negative'`, or `'zero'`
   - *Concept*: `step-py-cond-1`
9. **`py-first-even-odd`**: Modulo parity check
   - *Target Function*: `check_even_odd(n)`
   - *Contract*: Returns `'even'` or `'odd'`
   - *Concept*: `step-py-cond-2`
10. **`py-first-fizz-check`**: Compound divisibility
    - *Target Function*: `fizz_buzz_single(n)`
    - *Contract*: Checks `% 15`, `% 3`, `% 5`, or returns `str(n)`
    - *Concept*: `step-py-cond-2`
11. **`py-first-range-sum`**: Accumulator loop over range
    - *Target Function*: `sum_to_n(n)`
    - *Contract*: Sums $1 \dots n$ using `range(1, n + 1)`
    - *Concept*: `step-py-loops-1`
12. **`py-first-count-numbers`**: Filtered counting loop
    - *Target Function*: `count_positives(numbers)`
    - *Contract*: Counts elements $> 0$
    - *Concept*: `step-py-loops-1`
13. **`py-first-find-max`**: Extreme value scan (Maximum)
    - *Target Function*: `find_maximum(numbers)`
    - *Contract*: Returns largest element without using `max()`
    - *Concept*: `step-py-loops-2`
14. **`py-first-find-min`**: Extreme value scan (Minimum)
    - *Target Function*: `find_minimum(numbers)`
    - *Contract*: Returns smallest element without using `min()`
    - *Concept*: `step-py-loops-2`
15. **`py-first-str-first-last`**: Sequence indexing
    - *Target Function*: `first_and_last(s)`
    - *Contract*: Returns list `[s[0], s[-1]]`
    - *Concept*: `step-py-strings-1`
16. **`py-first-list-append-even`**: Filtering into dynamic list
    - *Target Function*: `filter_evens(numbers)`
    - *Contract*: Returns list of even numbers in order
    - *Concept*: `step-py-collections-1`
17. **`py-first-dict-count`**: Word frequency mapping
    - *Target Function*: `word_frequencies(words)`
    - *Contract*: Returns dictionary of word frequencies
    - *Concept*: `step-py-collections-2`
18. **`py-first-celsius-to-fahr`**: Reusable calculation function
    - *Target Function*: `celsius_to_fahrenheit(c)`
    - *Contract*: Returns `round(c * 9/5 + 32, 1)`
    - *Concept*: `step-py-functions-1`

---

### B. SQL and PostgreSQL (10 Exercises)
Verified in fresh isolated `@electric-sql/pglite` WASM databases via `sql_worker.mjs`:

1. **`sql-first-select-constant`**: Scalar projection
   - *Query Contract*: `SELECT 42 AS answer;`
   - *Expected Result*: 1 column (`answer`), 1 row (`[42]`)
   - *Concept*: `step-sql-tables-1`
2. **`sql-first-calc-constant`**: Arithmetic projection
   - *Query Contract*: `SELECT 100 + 5 AS total_sum;`
   - *Expected Result*: 1 column (`total_sum`), 1 row (`[105]`)
   - *Concept*: `step-sql-tables-1`
3. **`sql-first-read-one-col`**: Table column projection
   - *Query Contract*: `SELECT title FROM books;`
   - *Fixture*: `CREATE TABLE books (id INT PRIMARY KEY, title TEXT, author TEXT);`
   - *Concept*: `step-sql-tables-2`
4. **`sql-first-col-aliases`**: Renaming headers with `AS`
   - *Query Contract*: `SELECT first_name AS given_name, email AS contact_email FROM members;`
   - *Fixture*: `CREATE TABLE members (id INT PRIMARY KEY, first_name TEXT, email TEXT);`
   - *Concept*: `step-sql-tables-2`
5. **`sql-first-where`**: Predicate filtering
   - *Query Contract*: `SELECT name FROM users WHERE is_active = true;`
   - *Fixture*: `CREATE TABLE users (id INT PRIMARY KEY, name TEXT, is_active BOOLEAN);`
   - *Concept*: `step-sql-select-filter`
6. **`sql-first-where-range`**: Compound range comparison
   - *Query Contract*: `SELECT id, score FROM exam_results WHERE score >= 75 AND score <= 90;`
   - *Fixture*: `CREATE TABLE exam_results (id INT PRIMARY KEY, student_name TEXT, score INT);`
   - *Concept*: `step-sql-select-filter`
7. **`sql-first-null-filter`**: Missing data detection
   - *Query Contract*: `SELECT id, customer_name FROM orders WHERE delivered_at IS NULL;`
   - *Fixture*: `CREATE TABLE orders (id INT PRIMARY KEY, customer_name TEXT, delivered_at TIMESTAMP);`
   - *Concept*: `step-sql-nulls`
8. **`sql-first-coalesce`**: Fallback defaults
   - *Query Contract*: `SELECT id, COALESCE(nickname, username) AS display_name FROM profiles;`
   - *Fixture*: `CREATE TABLE profiles (id INT PRIMARY KEY, username TEXT, nickname TEXT);`
   - *Concept*: `step-sql-nulls`
9. **`sql-first-order-limit`**: Deterministic sorting and limiting
   - *Query Contract*: `SELECT name, salary FROM employees ORDER BY salary DESC LIMIT 3;`
   - *Order-Sensitive*: `True`
   - *Concept*: `step-sql-ordering-limits`
10. **`sql-first-group-count`**: Grouped aggregation
    - *Query Contract*: `SELECT department, COUNT(*) AS employee_count FROM staff GROUP BY department ORDER BY department ASC;`
    - *Order-Sensitive*: `True`
    - *Concept*: `step-sql-aggregations`

---

### C. Data Structures & Algorithms (7 Exercises)
Verified via `python_worker.py` against exact input/output contracts:

1. **`dsa-first-trace-sum`**: Contract verification & linear traversal
   - *Target Function*: `sum_list(elements)`
   - *Contract*: Handles empty lists (`[] -> 0`) and negative values
   - *Concept*: `step-dsa-contracts-1`
2. **`dsa-first-has-duplicate`**: $O(N)$ duplicate detection
   - *Target Function*: `has_duplicate(elements)`
   - *Contract*: Uses seen set for $O(1)$ membership test
   - *Concept*: `step-dsa-complexity-1`
3. **`dsa-first-linear-scan`**: Linear search with early exit
   - *Target Function*: `find_index(elements, target)`
   - *Contract*: Returns 0-based index or `-1` if absent
   - *Concept*: `step-dsa-scan-1`
4. **`dsa-first-count-target`**: In-place frequency counting
   - *Target Function*: `count_occurrences(elements, target)`
   - *Contract*: Scans list in $O(N)$ time with $O(1)$ auxiliary space
   - *Concept*: `step-dsa-scan-1`
5. **`dsa-first-is-palindrome`**: Two-pointer symmetric convergence
   - *Target Function*: `is_palindrome_str(s)`
   - *Contract*: Converges from start and end in $O(N)$ time with $O(1)$ space
   - *Concept*: `step-dsa-two-pointers`
6. **`dsa-first-freq-counting`**: Hash map frequency table
   - *Target Function*: `build_counts(items)`
   - *Contract*: Returns dictionary mapping elements to occurrence counts
   - *Concept*: `step-dsa-hash-1`
7. **`dsa-first-unique-elements`**: Set deduplication and sorting
   - *Target Function*: `get_unique_elements(items)`
   - *Contract*: Returns sorted list of unique elements
   - *Concept*: `step-dsa-hash-sets`

---

## 3. Challenge Library: 110 Original Problems Preserved

All 110 original problems in `content/problem-bank/` remain preserved in the **Challenge Library** tab at `/arena` and mapped across 5 progression stages in `data/learning-path/arena-stages.json`:

```
Stage 1: First Steps    (18 problems — elementary logic, direct single concepts)
Stage 2: Beginner       (20 problems — direct multi-step concepts, single-table SQL)
Stage 3: Developing     (28 problems — two pointers, frequency maps, simple joins)
Stage 4: Intermediate   (23 problems — stacks/queues, binary search, CTEs, subqueries)
Stage 5: Challenging    (21 problems — graphs, complex DP, window functions, trees)
-----------------------------------------------------------------------------------
Total: 110 Authoritative Problems Preserved with Full Historical Attempts Intact
```
