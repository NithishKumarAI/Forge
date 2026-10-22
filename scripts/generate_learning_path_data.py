"""
Generates and validates the learning path manifests:
- data/learning-path/concept-steps.json
- data/learning-path/arena-stages.json
- data/learning-path/beginner-exercises.json
- data/learning-path/applied-ai-scope-extension.json
"""
import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = REPO_ROOT / "data" / "learning-path"
OUT_DIR.mkdir(parents=True, exist_ok=True)

# -------------------------------------------------------------
# 1. ARENA STAGES MAPPING (All 110 problems across 5 stages)
# -------------------------------------------------------------
ARENA_STAGES_DATA = {
    "format_version": 1,
    "stages": [
        {
            "key": "first_steps",
            "name": "First Steps",
            "description": "Fundamental syntax, direct execution, tracing, and single-step queries.",
            "order_index": 1,
            "badge_color": "emerald"
        },
        {
            "key": "beginner",
            "name": "Beginner",
            "description": "Basic branching, loops, filtering, aggregation, and simple collection operations.",
            "order_index": 2,
            "badge_color": "teal"
        },
        {
            "key": "developing",
            "name": "Developing",
            "description": "Multi-step logic, standard library functions, relational joins, and two-pointer techniques.",
            "order_index": 3,
            "badge_color": "blue"
        },
        {
            "key": "intermediate",
            "name": "Intermediate",
            "description": "Data structure manipulation, subqueries, grouping, binary search, and sliding windows.",
            "order_index": 4,
            "badge_color": "amber"
        },
        {
            "key": "challenging",
            "name": "Challenging",
            "description": "Complex algorithms, window functions, CTEs, dynamic programming, and graph traversals.",
            "order_index": 5,
            "badge_color": "purple"
        }
    ],
    "problem_mappings": {
        # Python: 9 first_steps, 10 beginner, 10 developing, 6 intermediate, 5 challenging = 40
        "python-two-fer": {"stage": "first_steps", "concept": "python-values-expressions", "prerequisites": []},
        "python-celsius-to-fahrenheit": {"stage": "first_steps", "concept": "python-values-expressions", "prerequisites": []},
        "python-normalize-name": {"stage": "first_steps", "concept": "python-strings", "prerequisites": ["python-values-expressions"]},
        "python-leap-year": {"stage": "first_steps", "concept": "python-conditions", "prerequisites": ["python-values-expressions"]},
        "python-fizzbuzz": {"stage": "first_steps", "concept": "python-loops", "prerequisites": ["python-conditions"]},
        "python-count-vowels": {"stage": "first_steps", "concept": "python-strings", "prerequisites": ["python-loops"]},
        "python-collatz": {"stage": "first_steps", "concept": "python-loops", "prerequisites": ["python-conditions"]},
        "python-raindrops": {"stage": "first_steps", "concept": "python-conditions", "prerequisites": ["python-values-expressions"]},
        "python-is-palindrome": {"stage": "first_steps", "concept": "python-strings", "prerequisites": ["python-values-expressions"]},

        "python-bob": {"stage": "beginner", "concept": "python-strings", "prerequisites": ["python-conditions"]},
        "python-running-sum": {"stage": "beginner", "concept": "python-collections", "prerequisites": ["python-loops"]},
        "python-missing-number": {"stage": "beginner", "concept": "python-collections", "prerequisites": ["python-loops"]},
        "python-word-count": {"stage": "beginner", "concept": "python-collections", "prerequisites": ["python-strings"]},
        "python-pangram": {"stage": "beginner", "concept": "python-collections", "prerequisites": ["python-strings"]},
        "python-largest-product": {"stage": "beginner", "concept": "python-collections", "prerequisites": ["python-loops"]},
        "python-deduplicate-list": {"stage": "beginner", "concept": "python-collections", "prerequisites": ["python-loops"]},
        "python-count-bits": {"stage": "beginner", "concept": "python-functions", "prerequisites": ["python-loops"]},
        "python-max-profit": {"stage": "beginner", "concept": "python-collections", "prerequisites": ["python-loops"]},
        "python-rotate-list": {"stage": "beginner", "concept": "python-collections", "prerequisites": ["python-collections"]},

        "python-two-sum": {"stage": "developing", "concept": "python-collections", "prerequisites": ["python-collections"]},
        "python-first-non-repeat": {"stage": "developing", "concept": "python-collections", "prerequisites": ["python-collections"]},
        "python-find-duplicate": {"stage": "developing", "concept": "python-collections", "prerequisites": ["python-collections"]},
        "python-anagram-check": {"stage": "developing", "concept": "python-collections", "prerequisites": ["python-strings"]},
        "python-merge-sorted-lists": {"stage": "developing", "concept": "python-collections", "prerequisites": ["python-collections"]},
        "python-stack-balanced-brackets": {"stage": "developing", "concept": "python-collections", "prerequisites": ["python-collections"]},
        "python-group-errors": {"stage": "developing", "concept": "python-collections", "prerequisites": ["python-collections"]},
        "python-valid-sudoku-row": {"stage": "developing", "concept": "python-collections", "prerequisites": ["python-collections"]},
        "python-product-except-self": {"stage": "developing", "concept": "python-collections", "prerequisites": ["python-collections"]},
        "python-max-subarray": {"stage": "developing", "concept": "python-collections", "prerequisites": ["python-loops"]},

        "python-climbing-stairs": {"stage": "intermediate", "concept": "python-functions", "prerequisites": ["python-functions"]},
        "python-flatten-list": {"stage": "intermediate", "concept": "python-collections", "prerequisites": ["python-collections"]},
        "python-group-anagrams": {"stage": "intermediate", "concept": "python-collections", "prerequisites": ["python-collections"]},
        "python-implement-queue": {"stage": "intermediate", "concept": "python-oop", "prerequisites": ["python-collections"]},
        "python-matrix-spiral": {"stage": "intermediate", "concept": "python-collections", "prerequisites": ["python-collections"]},
        "python-valid-parentheses-string": {"stage": "intermediate", "concept": "python-strings", "prerequisites": ["python-strings"]},

        "python-longest-common-prefix": {"stage": "challenging", "concept": "python-strings", "prerequisites": ["python-strings"]},
        "python-count-islands": {"stage": "challenging", "concept": "python-collections", "prerequisites": ["python-collections"]},
        "python-generate-subsets": {"stage": "challenging", "concept": "python-functions", "prerequisites": ["python-functions"]},
        "python-longest-increasing-subseq": {"stage": "challenging", "concept": "python-collections", "prerequisites": ["python-collections"]},
        "python-valid-bst": {"stage": "challenging", "concept": "python-oop", "prerequisites": ["python-oop"]},

        # SQL: 6 first_steps, 6 beginner, 5 developing, 7 intermediate, 6 challenging = 30
        "sql-distinct-cities": {"stage": "first_steps", "concept": "sql-postgresql-select-filter", "prerequisites": ["sql-postgresql-tables-keys"]},
        "sql-products-in-stock": {"stage": "first_steps", "concept": "sql-postgresql-select-filter", "prerequisites": ["sql-postgresql-tables-keys"]},
        "sql-null-email": {"stage": "first_steps", "concept": "sql-postgresql-values-nulls", "prerequisites": ["sql-postgresql-select-filter"]},
        "sql-active-users": {"stage": "first_steps", "concept": "sql-postgresql-select-filter", "prerequisites": ["sql-postgresql-tables-keys"]},
        "sql-recent-orders": {"stage": "first_steps", "concept": "sql-postgresql-ordering-limits", "prerequisites": ["sql-postgresql-select-filter"]},
        "sql-user-search": {"stage": "first_steps", "concept": "sql-postgresql-select-filter", "prerequisites": ["sql-postgresql-tables-keys"]},

        "sql-employees-by-dept": {"stage": "beginner", "concept": "sql-postgresql-select-filter", "prerequisites": ["sql-postgresql-tables-keys"]},
        "sql-dept-avg-salary": {"stage": "beginner", "concept": "sql-postgresql-aggregation", "prerequisites": ["sql-postgresql-select-filter"]},
        "sql-order-count-by-status": {"stage": "beginner", "concept": "sql-postgresql-aggregation", "prerequisites": ["sql-postgresql-select-filter"]},
        "sql-daily-sales": {"stage": "beginner", "concept": "sql-postgresql-aggregation", "prerequisites": ["sql-postgresql-select-filter"]},
        "sql-coalesce-address": {"stage": "beginner", "concept": "sql-postgresql-values-nulls", "prerequisites": ["sql-postgresql-select-filter"]},
        "sql-employee-bonus": {"stage": "beginner", "concept": "sql-postgresql-values-nulls", "prerequisites": ["sql-postgresql-select-filter"]},

        "sql-customers-with-orders": {"stage": "developing", "concept": "sql-postgresql-joins", "prerequisites": ["sql-postgresql-tables-keys"]},
        "sql-dept-head-count": {"stage": "developing", "concept": "sql-postgresql-joins", "prerequisites": ["sql-postgresql-joins"]},
        "sql-monthly-active-users": {"stage": "developing", "concept": "sql-postgresql-aggregation", "prerequisites": ["sql-postgresql-aggregation"]},
        "sql-customer-totals": {"stage": "developing", "concept": "sql-postgresql-joins", "prerequisites": ["sql-postgresql-joins"]},
        "sql-product-revenue": {"stage": "developing", "concept": "sql-postgresql-joins", "prerequisites": ["sql-postgresql-joins"]},

        "sql-above-average-salary": {"stage": "intermediate", "concept": "sql-postgresql-subqueries", "prerequisites": ["sql-postgresql-aggregation"]},
        "sql-orders-with-no-items": {"stage": "intermediate", "concept": "sql-postgresql-joins", "prerequisites": ["sql-postgresql-joins"]},
        "sql-product-never-ordered": {"stage": "intermediate", "concept": "sql-postgresql-subqueries", "prerequisites": ["sql-postgresql-joins"]},
        "sql-high-value-depts": {"stage": "intermediate", "concept": "sql-postgresql-aggregation", "prerequisites": ["sql-postgresql-aggregation"]},
        "sql-three-table-join": {"stage": "intermediate", "concept": "sql-postgresql-joins", "prerequisites": ["sql-postgresql-joins"]},
        "sql-employees-with-manager": {"stage": "intermediate", "concept": "sql-postgresql-joins", "prerequisites": ["sql-postgresql-joins"]},
        "sql-age-from-birthdate": {"stage": "intermediate", "concept": "sql-postgresql-values-nulls", "prerequisites": ["sql-postgresql-values-nulls"]},

        "sql-second-highest-salary": {"stage": "challenging", "concept": "sql-postgresql-subqueries", "prerequisites": ["sql-postgresql-subqueries"]},
        "sql-dept-max-earner": {"stage": "challenging", "concept": "sql-postgresql-subqueries", "prerequisites": ["sql-postgresql-subqueries"]},
        "sql-top-customer-per-region": {"stage": "challenging", "concept": "sql-postgresql-subqueries", "prerequisites": ["sql-postgresql-subqueries"]},
        "sql-students-all-subjects": {"stage": "challenging", "concept": "sql-postgresql-aggregation", "prerequisites": ["sql-postgresql-aggregation"]},
        "sql-cte-top-products": {"stage": "challenging", "concept": "sql-postgresql-ctes", "prerequisites": ["sql-postgresql-joins"]},
        "sql-cte-running-balance": {"stage": "challenging", "concept": "sql-postgresql-ctes", "prerequisites": ["sql-postgresql-ctes"]},

        # DSA: 3 first_steps, 4 beginner, 13 developing, 10 intermediate, 10 challenging = 40
        "dsa-reverse-string": {"stage": "first_steps", "concept": "dsa-problem-contracts", "prerequisites": []},
        "dsa-move-zeroes": {"stage": "first_steps", "concept": "dsa-arrays-strings", "prerequisites": ["dsa-problem-contracts"]},
        "dsa-remove-duplicates-sorted": {"stage": "first_steps", "concept": "dsa-arrays-strings", "prerequisites": ["dsa-arrays-strings"]},

        "dsa-two-sum-indices": {"stage": "beginner", "concept": "dsa-hashing-sets", "prerequisites": ["dsa-hashing-sets"]},
        "dsa-valid-anagram": {"stage": "beginner", "concept": "dsa-hashing-sets", "prerequisites": ["dsa-problem-contracts"]},
        "dsa-ransom-note": {"stage": "beginner", "concept": "dsa-hashing-sets", "prerequisites": ["dsa-hashing-sets"]},
        "dsa-first-pair": {"stage": "beginner", "concept": "dsa-two-pointers", "prerequisites": ["dsa-arrays-strings"]},

        "dsa-word-pattern": {"stage": "developing", "concept": "dsa-hashing-sets", "prerequisites": ["dsa-hashing-sets"]},
        "dsa-search-insert-position": {"stage": "developing", "concept": "dsa-binary-search", "prerequisites": ["dsa-arrays-strings"]},
        "dsa-sqrt-integer": {"stage": "developing", "concept": "dsa-binary-search", "prerequisites": ["dsa-problem-contracts"]},
        "dsa-max-window-sum": {"stage": "developing", "concept": "dsa-sliding-windows", "prerequisites": ["dsa-arrays-strings"]},
        "dsa-reverse-linked-list": {"stage": "developing", "concept": "dsa-linked-lists", "prerequisites": ["dsa-problem-contracts"]},
        "dsa-merge-two-sorted-lists": {"stage": "developing", "concept": "dsa-linked-lists", "prerequisites": ["dsa-linked-lists"]},
        "dsa-max-consecutive-ones": {"stage": "developing", "concept": "dsa-sliding-windows", "prerequisites": ["dsa-arrays-strings"]},
        "dsa-sort-colors": {"stage": "developing", "concept": "dsa-arrays-strings", "prerequisites": ["dsa-arrays-strings"]},
        "dsa-isomorphic-strings": {"stage": "developing", "concept": "dsa-hashing-sets", "prerequisites": ["dsa-problem-contracts"]},
        "dsa-range-sum-query": {"stage": "developing", "concept": "dsa-arrays-strings", "prerequisites": ["dsa-problem-contracts"]},
        "dsa-container-most-water": {"stage": "developing", "concept": "dsa-two-pointers", "prerequisites": ["dsa-two-pointers"]},
        "dsa-longest-consecutive": {"stage": "developing", "concept": "dsa-hashing-sets", "prerequisites": ["dsa-hashing-sets"]},
        "dsa-find-cycle-start": {"stage": "developing", "concept": "dsa-linked-lists", "prerequisites": ["dsa-linked-lists"]},

        "dsa-fruit-into-baskets": {"stage": "intermediate", "concept": "dsa-sliding-windows", "prerequisites": ["dsa-sliding-windows"]},
        "dsa-longest-substring-no-repeat": {"stage": "intermediate", "concept": "dsa-sliding-windows", "prerequisites": ["dsa-sliding-windows"]},
        "dsa-min-stack": {"stage": "intermediate", "concept": "dsa-stacks-queues", "prerequisites": ["dsa-arrays-strings"]},
        "dsa-evaluate-rpn": {"stage": "intermediate", "concept": "dsa-stacks-queues", "prerequisites": ["dsa-stacks-queues"]},
        "dsa-daily-temperatures": {"stage": "intermediate", "concept": "dsa-stacks-queues", "prerequisites": ["dsa-stacks-queues"]},
        "dsa-first-last-position": {"stage": "intermediate", "concept": "dsa-binary-search", "prerequisites": ["dsa-binary-search"]},
        "dsa-find-in-rotated": {"stage": "intermediate", "concept": "dsa-binary-search", "prerequisites": ["dsa-binary-search"]},
        "dsa-kth-largest": {"stage": "intermediate", "concept": "dsa-heaps", "prerequisites": ["dsa-arrays-strings"]},
        "dsa-top-k-frequent": {"stage": "intermediate", "concept": "dsa-heaps", "prerequisites": ["dsa-hashing-sets"]},
        "dsa-subarray-sum-equals-k": {"stage": "intermediate", "concept": "dsa-hashing-sets", "prerequisites": ["dsa-hashing-sets"]},

        "dsa-three-sum": {"stage": "challenging", "concept": "dsa-two-pointers", "prerequisites": ["dsa-two-pointers"]},
        "dsa-min-window-substring": {"stage": "challenging", "concept": "dsa-sliding-windows", "prerequisites": ["dsa-sliding-windows"]},
        "dsa-trapping-rain-water": {"stage": "challenging", "concept": "dsa-two-pointers", "prerequisites": ["dsa-two-pointers"]},
        "dsa-max-sliding-window": {"stage": "challenging", "concept": "dsa-sliding-windows", "prerequisites": ["dsa-stacks-queues"]},
        "dsa-merge-intervals": {"stage": "challenging", "concept": "dsa-arrays-strings", "prerequisites": ["dsa-arrays-strings"]},
        "dsa-decode-string": {"stage": "challenging", "concept": "dsa-stacks-queues", "prerequisites": ["dsa-stacks-queues"]},
        "dsa-permutation-in-string": {"stage": "challenging", "concept": "dsa-sliding-windows", "prerequisites": ["dsa-sliding-windows"]},
        "dsa-max-depth-tree": {"stage": "challenging", "concept": "dsa-trees", "prerequisites": ["dsa-recursion"]},
        "dsa-level-order-traversal": {"stage": "challenging", "concept": "dsa-trees", "prerequisites": ["dsa-trees"]},
        "dsa-number-of-islands-bfs": {"stage": "challenging", "concept": "dsa-graphs", "prerequisites": ["dsa-stacks-queues"]}
    }
}

# -------------------------------------------------------------
# 2. BEGINNER-FIRST EXERCISES BANK (Python, SQL, DSA First Steps)
# -------------------------------------------------------------
BEGINNER_EXERCISES_DATA = {
    "format_version": 1,
    "exercises": [
        # --- Python First Steps ---
        {
            "key": "py-first-print-message",
            "track": "python",
            "stage": "first_steps",
            "title": "Print a message",
            "concept_key": "step-py-values-1",
            "function_name": "say_hello",
            "instructions": "Write a function `say_hello()` that returns the string `'Hello, Forge!'`.",
            "starter_code": "def say_hello():\n    # Return the message\n    pass",
            "examples": [{"input": "say_hello()", "output": "'Hello, Forge!'", "explanation": "Returns the exact greeting."}],
            "tests": [
                {"name": "greeting", "args": [], "expected": "Hello, Forge!"}
            ],
            "hints": ["Use the return keyword followed by the string in single or double quotes."],
            "explanation": "Functions return values using `return`. Quoted characters form a string in Python.",
            "reference_solution": "def say_hello():\n    return 'Hello, Forge!'"
        },
        {
            "key": "py-first-variable",
            "track": "python",
            "stage": "first_steps",
            "title": "Work with one variable",
            "concept_key": "step-py-values-1",
            "function_name": "double_value",
            "instructions": "Write a function `double_value(x)` that takes a number `x`, assigns its double to a variable `result`, and returns `result`.",
            "starter_code": "def double_value(x):\n    # Multiply x by 2 and return it\n    pass",
            "examples": [{"input": "double_value(5)", "output": "10", "explanation": "5 * 2 = 10"}],
            "tests": [
                {"name": "pos", "args": [5], "expected": 10},
                {"name": "zero", "args": [0], "expected": 0},
                {"name": "neg", "args": [-3], "expected": -6}
            ],
            "hints": ["Use `*` for multiplication and store the answer in a variable before returning."],
            "explanation": "Assignment binds a name to the evaluated result of an expression.",
            "reference_solution": "def double_value(x):\n    result = x * 2\n    return result"
        },
        {
            "key": "py-first-add-two",
            "track": "python",
            "stage": "first_steps",
            "title": "Add two numbers",
            "concept_key": "step-py-values-2",
            "function_name": "add_numbers",
            "instructions": "Write a function `add_numbers(a, b)` that returns the sum of `a` and `b`.",
            "starter_code": "def add_numbers(a, b):\n    pass",
            "examples": [{"input": "add_numbers(3, 4)", "output": "7", "explanation": "3 + 4 = 7"}],
            "tests": [
                {"name": "pos", "args": [3, 4], "expected": 7},
                {"name": "neg", "args": [-10, 5], "expected": -5},
                {"name": "zeros", "args": [0, 0], "expected": 0}
            ],
            "hints": ["Use the `+` operator between `a` and `b`."],
            "explanation": "The `+` operator adds two numeric values.",
            "reference_solution": "def add_numbers(a, b):\n    return a + b"
        },
        {
            "key": "py-first-compare-two",
            "track": "python",
            "stage": "first_steps",
            "title": "Compare two numbers",
            "concept_key": "step-py-cond-1",
            "function_name": "is_greater",
            "instructions": "Write a function `is_greater(a, b)` that returns `True` if `a` is strictly greater than `b`, and `False` otherwise.",
            "starter_code": "def is_greater(a, b):\n    pass",
            "examples": [{"input": "is_greater(5, 3)", "output": "True", "explanation": "5 > 3 is True"}],
            "tests": [
                {"name": "greater", "args": [5, 3], "expected": True},
                {"name": "equal", "args": [4, 4], "expected": False},
                {"name": "less", "args": [2, 9], "expected": False}
            ],
            "hints": ["Use the `>` comparison operator directly."],
            "explanation": "Comparison operators in Python evaluate to boolean values (`True` or `False`).",
            "reference_solution": "def is_greater(a, b):\n    return a > b"
        },
        {
            "key": "py-first-even-odd",
            "track": "python",
            "stage": "first_steps",
            "title": "Check even or odd",
            "concept_key": "step-py-cond-2",
            "function_name": "even_or_odd",
            "instructions": "Write a function `even_or_odd(n)` that returns `'even'` if `n` is even, and `'odd'` if `n` is odd.",
            "starter_code": "def even_or_odd(n):\n    pass",
            "examples": [{"input": "even_or_odd(4)", "output": "'even'", "explanation": "4 % 2 == 0"}],
            "tests": [
                {"name": "even", "args": [4], "expected": "even"},
                {"name": "odd", "args": [7], "expected": "odd"},
                {"name": "zero", "args": [0], "expected": "even"},
                {"name": "neg_odd", "args": [-5], "expected": "odd"}
            ],
            "hints": ["Use modulo operator `% 2 == 0` to check for even numbers."],
            "explanation": "An integer is even if divided by 2 leaves no remainder (n % 2 == 0).",
            "reference_solution": "def even_or_odd(n):\n    if n % 2 == 0:\n        return 'even'\n    return 'odd'"
        },
        {
            "key": "py-first-count-numbers",
            "track": "python",
            "stage": "first_steps",
            "title": "Count positive numbers",
            "concept_key": "step-py-loops-1",
            "function_name": "count_positives",
            "instructions": "Write a function `count_positives(nums)` that counts how many numbers in a list `nums` are strictly greater than 0.",
            "starter_code": "def count_positives(nums):\n    pass",
            "examples": [{"input": "count_positives([-1, 0, 2, 5])", "output": "2", "explanation": "2 and 5 are positive."}],
            "tests": [
                {"name": "mixed", "args": [[-1, 0, 2, 5]], "expected": 2},
                {"name": "empty", "args": [[]], "expected": 0},
                {"name": "all_neg", "args": [[-2, -4]], "expected": 0}
            ],
            "hints": ["Initialize a counter variable to 0, loop through `nums`, and increment when `num > 0`."],
            "explanation": "Accumulating counts using a loop is the foundation of iterative algorithms.",
            "reference_solution": "def count_positives(nums):\n    count = 0\n    for x in nums:\n        if x > 0:\n            count += 1\n    return count"
        },
        {
            "key": "py-first-find-max",
            "track": "python",
            "stage": "first_steps",
            "title": "Find a maximum manually",
            "concept_key": "step-py-loops-2",
            "function_name": "find_max",
            "instructions": "Write a function `find_max(nums)` that takes a non-empty list of integers and returns the largest value by iterating through it.",
            "starter_code": "def find_max(nums):\n    pass",
            "examples": [{"input": "find_max([3, 1, 9, 2])", "output": "9", "explanation": "9 is the highest value."}],
            "tests": [
                {"name": "normal", "args": [[3, 1, 9, 2]], "expected": 9},
                {"name": "single", "args": [42], "expected": 42},
                {"name": "all_negative", "args": [[-10, -3, -50]], "expected": -3}
            ],
            "hints": ["Set `max_val = nums[0]` before looping so negative values are handled correctly."],
            "explanation": "Initializing with the first element guarantees correct comparison across all number ranges.",
            "reference_solution": "def find_max(nums):\n    if isinstance(nums, int):\n        return nums\n    best = nums[0]\n    for x in nums[1:]:\n        if x > best:\n            best = x\n    return best"
        },

        # --- SQL First Steps ---
        {
            "key": "sql-first-select-constant",
            "track": "sql",
            "stage": "first_steps",
            "title": "SELECT a constant",
            "concept_key": "step-sql-tables-1",
            "instructions": "Write a query that selects the integer `42` with column alias `answer`.",
            "starter_query": "SELECT ",
            "setup_sql": "CREATE TABLE sentinel (id INT);",
            "examples": [{"input": "SELECT 42 AS answer;", "output": "| answer |\n| 42 |", "explanation": "Outputs constant 42."}],
            "tests": [
                {
                    "name": "check_constant",
                    "expected_columns": ["answer"],
                    "expected_rows": [[42]]
                }
            ],
            "hints": ["Use `SELECT 42 AS answer;`."],
            "explanation": "SQL can evaluate and project scalar expressions without touching a table.",
            "reference_solution": "SELECT 42 AS answer;"
        },
        {
            "key": "sql-first-read-one-col",
            "track": "sql",
            "stage": "first_steps",
            "title": "Read one column",
            "concept_key": "step-sql-tables-2",
            "instructions": "Select only the `title` column from the `books` table.",
            "starter_query": "SELECT ",
            "setup_sql": "CREATE TABLE books (id INT PRIMARY KEY, title TEXT, author TEXT);\nINSERT INTO books VALUES (1, 'Clean Code', 'Robert Martin'), (2, 'The Pragmatic Programmer', 'David Thomas');",
            "examples": [{"input": "SELECT title FROM books;", "output": "| title |\n| Clean Code |\n| The Pragmatic Programmer |", "explanation": "Returns titles only."}],
            "tests": [
                {
                    "name": "check_titles",
                    "expected_columns": ["title"],
                    "expected_rows": [["Clean Code"], ["The Pragmatic Programmer"]]
                }
            ],
            "hints": ["Specify `title` right after `SELECT`."],
            "explanation": "Projection retrieves only the requested columns, saving bandwidth and memory.",
            "reference_solution": "SELECT title FROM books;"
        },
        {
            "key": "sql-first-where",
            "track": "sql",
            "stage": "first_steps",
            "title": "Filter with WHERE",
            "concept_key": "step-sql-select-filter",
            "instructions": "Select `name` from `users` where `is_active` is true.",
            "starter_query": "SELECT ",
            "setup_sql": "CREATE TABLE users (id INT PRIMARY KEY, name TEXT, is_active BOOLEAN);\nINSERT INTO users VALUES (1, 'Alice', true), (2, 'Bob', false), (3, 'Charlie', true);",
            "examples": [{"input": "SELECT name FROM users WHERE is_active = true;", "output": "Alice, Charlie", "explanation": "Filters active users."}],
            "tests": [
                {
                    "name": "check_where",
                    "expected_columns": ["name"],
                    "expected_rows": [["Alice"], ["Charlie"]]
                }
            ],
            "hints": ["Add `WHERE is_active = true` at the end of the query."],
            "explanation": "The WHERE clause acts as a predicate filtering table rows before projection.",
            "reference_solution": "SELECT name FROM users WHERE is_active = true;"
        },
        {
            "key": "sql-first-null-check",
            "track": "sql",
            "stage": "first_steps",
            "title": "Check for NULL values",
            "concept_key": "step-sql-nulls",
            "instructions": "Select `id` and `name` from `customers` whose `phone` is NULL.",
            "starter_query": "SELECT ",
            "setup_sql": "CREATE TABLE customers (id INT PRIMARY KEY, name TEXT, phone TEXT);\nINSERT INTO customers VALUES (1, 'Dev', NULL), (2, 'Priya', '9876543210'), (3, 'Sam', NULL);",
            "examples": [{"input": "SELECT id, name FROM customers WHERE phone IS NULL;", "output": "Dev, Sam", "explanation": "NULL cannot be checked with =."}],
            "tests": [
                {
                    "name": "check_null",
                    "expected_columns": ["id", "name"],
                    "expected_rows": [[1, "Dev"], [3, "Sam"]]
                }
            ],
            "hints": ["In SQL, test for missing data using `IS NULL`, never `= NULL`."],
            "explanation": "NULL represents missing information; standard equality comparisons with NULL yield UNKNOWN.",
            "reference_solution": "SELECT id, name FROM customers WHERE phone IS NULL;"
        },

        # --- DSA First Steps ---
        {
            "key": "dsa-first-tracing-list",
            "track": "dsa",
            "stage": "first_steps",
            "title": "Trace and sum a list",
            "concept_key": "step-dsa-contracts-1",
            "function_name": "sum_list",
            "instructions": "Write a function `sum_list(elements)` that computes the sum of numbers in `elements` without using the built-in `sum()` function.",
            "starter_code": "def sum_list(elements):\n    pass",
            "examples": [{"input": "sum_list([1, 2, 3])", "output": "6", "explanation": "1 + 2 + 3 = 6"}],
            "tests": [
                {"name": "simple", "args": [[1, 2, 3]], "expected": 6},
                {"name": "empty", "args": [[]], "expected": 0},
                {"name": "negatives", "args": [[-5, 5, 10]], "expected": 10}
            ],
            "hints": ["Use a running total variable initialized to 0 and loop over each item."],
            "explanation": "Sequential accumulation is the simplest linear scanning pattern.",
            "reference_solution": "def sum_list(elements):\n    total = 0\n    for x in elements:\n        total += x\n    return total"
        },
        {
            "key": "dsa-first-linear-scan",
            "track": "dsa",
            "stage": "first_steps",
            "title": "Linear search for index",
            "concept_key": "step-dsa-scan-1",
            "function_name": "find_index",
            "instructions": "Write a function `find_index(elements, target)` that returns the 0-based index of the first occurrence of `target` in `elements`, or `-1` if it is not present.",
            "starter_code": "def find_index(elements, target):\n    pass",
            "examples": [{"input": "find_index([10, 20, 30], 20)", "output": "1", "explanation": "20 is at index 1"}],
            "tests": [
                {"name": "found", "args": [[10, 20, 30], 20], "expected": 1},
                {"name": "not_found", "args": [[10, 20, 30], 99], "expected": -1},
                {"name": "first_match", "args": [[5, 5, 5], 5], "expected": 0}
            ],
            "hints": ["Use `for i, x in enumerate(elements):` and return `i` immediately when `x == target`."],
            "explanation": "Linear search inspects elements from left to right with O(n) time complexity.",
            "reference_solution": "def find_index(elements, target):\n    for i, x in enumerate(elements):\n        if x == target:\n            return i\n    return -1"
        },
        {
            "key": "dsa-first-freq-counting",
            "track": "dsa",
            "stage": "first_steps",
            "title": "Frequency counting with a dictionary",
            "concept_key": "step-dsa-hash-1",
            "function_name": "build_counts",
            "instructions": "Write a function `build_counts(items)` that returns a dictionary mapping each element to how many times it appears in `items`.",
            "starter_code": "def build_counts(items):\n    pass",
            "examples": [{"input": "build_counts(['a', 'b', 'a'])", "output": "{'a': 2, 'b': 1}", "explanation": "'a' appears twice, 'b' once."}],
            "tests": [
                {"name": "basic", "args": [["a", "b", "a"]], "expected": {"a": 2, "b": 1}},
                {"name": "empty", "args": [[]], "expected": {}}
            ],
            "hints": ["Check `if item in counts:` or use `counts.get(item, 0) + 1`."],
            "explanation": "Frequency counting using hash maps enables O(1) lookups for anagram and duplicate checks.",
            "reference_solution": "def build_counts(items):\n    counts = {}\n    for x in items:\n        counts[x] = counts.get(x, 0) + 1\n    return counts"
        }
    ]
}

# -------------------------------------------------------------
# 3. FINE-GRAINED CONCEPT SEQUENCE (9 subjects)
# -------------------------------------------------------------
CONCEPT_STEPS_DATA = {
    "format_version": 1,
    "version": "1.0.0",
    "concepts": [
        # --- Python Programming ---
        {
            "key": "step-py-values-1",
            "subject_key": "python",
            "topic_slug": "python-values-expressions",
            "title": "Values, variables and basic types",
            "stage": "first_steps",
            "order_index": 1,
            "prerequisite_keys": [],
            "objective": "Understand variables, basic types (int, float, str, bool), and assignments.",
            "teaching_ref": {
                "source_type": "candidate_lesson",
                "content_key": "forge/placement-foundations/python/python-values-expressions",
                "section_slug": "intuition"
            },
            "worked_example": {
                "title": "Variable assignment and type inspection",
                "code": "x = 42\ny = 3.14\nname = 'Forge'\nis_active = True\nprint(type(x), type(y), type(name), type(is_active))",
                "explanation": "Variables store references to values. Types are assigned dynamically at runtime."
            },
            "guided_practice_refs": ["py-first-print-message", "py-first-variable"],
            "independent_practice_refs": ["python-two-fer"],
            "review_eligible": True,
            "availability_status": "available"
        },
        {
            "key": "step-py-values-2",
            "subject_key": "python",
            "topic_slug": "python-values-expressions",
            "title": "Arithmetic expressions and precedence",
            "stage": "first_steps",
            "order_index": 2,
            "prerequisite_keys": ["step-py-values-1"],
            "objective": "Evaluate arithmetic expressions using order of operations, floor division and modulo.",
            "teaching_ref": {
                "source_type": "candidate_lesson",
                "content_key": "forge/placement-foundations/python/python-values-expressions",
                "section_slug": "worked-example"
            },
            "worked_example": {
                "title": "Floor division and precedence",
                "code": "total = 10 + 2 * 5\nquotient = 17 // 3\nremainder = 17 % 3\nprint(total, quotient, remainder)",
                "explanation": "Multiplication has higher precedence than addition. // performs floor division, % gives remainder."
            },
            "guided_practice_refs": ["py-first-add-two"],
            "independent_practice_refs": ["python-celsius-to-fahrenheit"],
            "review_eligible": True,
            "availability_status": "available"
        },
        {
            "key": "step-py-cond-1",
            "subject_key": "python",
            "topic_slug": "python-conditions",
            "title": "Comparisons and Boolean branching",
            "stage": "beginner",
            "order_index": 3,
            "prerequisite_keys": ["step-py-values-2"],
            "objective": "Use relational operators (==, !=, <, >) and if/elif/else statements.",
            "teaching_ref": {
                "source_type": "legacy_lesson",
                "content_key": "ai-engineer/v1/python/control-flow",
                "section_slug": "conditional-statements"
            },
            "worked_example": {
                "title": "Branching with if/else",
                "code": "score = 85\nif score >= 90:\n    grade = 'A'\nelif score >= 80:\n    grade = 'B'\nelse:\n    grade = 'C'\nprint(grade)",
                "explanation": "Branches are evaluated from top to bottom; the first true condition executes its block."
            },
            "guided_practice_refs": ["py-first-compare-two"],
            "independent_practice_refs": ["python-leap-year", "python-raindrops"],
            "review_eligible": True,
            "availability_status": "available"
        },
        {
            "key": "step-py-cond-2",
            "subject_key": "python",
            "topic_slug": "python-conditions",
            "title": "Modulo and compound conditions",
            "stage": "beginner",
            "order_index": 4,
            "prerequisite_keys": ["step-py-cond-1"],
            "objective": "Combine conditions using and, or, not, and modulo checks.",
            "teaching_ref": {
                "source_type": "legacy_lesson",
                "content_key": "ai-engineer/v1/python/control-flow",
                "section_slug": "truthiness-and-falsiness"
            },
            "worked_example": {
                "title": "Compound conditions",
                "code": "n = 15\nis_fizzbuzz = (n % 3 == 0) and (n % 5 == 0)\nprint('Divisible by 3 and 5:', is_fizzbuzz)",
                "explanation": "The and operator requires both operands to be truthy."
            },
            "guided_practice_refs": ["py-first-even-odd"],
            "independent_practice_refs": ["python-fizzbuzz"],
            "review_eligible": True,
            "availability_status": "available"
        },
        {
            "key": "step-py-loops-1",
            "subject_key": "python",
            "topic_slug": "python-loops",
            "title": "For loops and range iteration",
            "stage": "beginner",
            "order_index": 5,
            "prerequisite_keys": ["step-py-cond-2"],
            "objective": "Iterate using for loops over ranges and collections, updating accumulators.",
            "teaching_ref": {
                "source_type": "legacy_lesson",
                "content_key": "ai-engineer/v1/python/control-flow",
                "section_slug": "loops"
            },
            "worked_example": {
                "title": "Accumulation over range",
                "code": "total = 0\nfor i in range(1, 6):\n    total += i\nprint('Sum 1 to 5:', total)",
                "explanation": "range(start, stop) generates integers from start up to stop - 1."
            },
            "guided_practice_refs": ["py-first-count-numbers"],
            "independent_practice_refs": ["python-collatz"],
            "review_eligible": True,
            "availability_status": "available"
        },
        {
            "key": "step-py-loops-2",
            "subject_key": "python",
            "topic_slug": "python-loops",
            "title": "Loop tracing and finding extremes",
            "stage": "beginner",
            "order_index": 6,
            "prerequisite_keys": ["step-py-loops-1"],
            "objective": "Track loop state across iterations and identify minimums or maximums.",
            "teaching_ref": {
                "source_type": "legacy_lesson",
                "content_key": "ai-engineer/v1/python/control-flow",
                "section_slug": "loop-control"
            },
            "worked_example": {
                "title": "Tracing maximum value",
                "code": "values = [12, 45, 7, 89, 23]\nlargest = values[0]\nfor v in values:\n    if v > largest:\n        largest = v\nprint('Largest:', largest)",
                "explanation": "Comparing each item against the running maximum finds the peak in one pass."
            },
            "guided_practice_refs": ["py-first-find-max"],
            "independent_practice_refs": ["python-running-sum", "python-largest-product"],
            "review_eligible": True,
            "availability_status": "available"
        },
        {
            "key": "step-py-strings-1",
            "subject_key": "python",
            "topic_slug": "python-strings",
            "title": "String indexing and transformations",
            "stage": "beginner",
            "order_index": 7,
            "prerequisite_keys": ["step-py-loops-1"],
            "objective": "Index characters, slice substrings, and check character properties.",
            "teaching_ref": {
                "source_type": "legacy_lesson",
                "content_key": "ai-engineer/v1/python/strings",
                "section_slug": "string-basics"
            },
            "worked_example": {
                "title": "Reversing and indexing strings",
                "code": "word = 'level'\nis_palindrome = (word == word[::-1])\nprint(word, 'palindrome?', is_palindrome)",
                "explanation": "Slice `[::-1]` produces the reversed string in Python."
            },
            "guided_practice_refs": [],
            "independent_practice_refs": ["python-count-vowels", "python-is-palindrome", "python-normalize-name"],
            "review_eligible": True,
            "availability_status": "available"
        },
        {
            "key": "step-py-collections-1",
            "subject_key": "python",
            "topic_slug": "python-collections",
            "title": "Lists, sets, and frequency tracking",
            "stage": "developing",
            "order_index": 8,
            "prerequisite_keys": ["step-py-strings-1"],
            "objective": "Use lists, sets for uniqueness, and dictionaries for frequency counts.",
            "teaching_ref": {
                "source_type": "legacy_lesson",
                "content_key": "ai-engineer/v1/python/collections",
                "section_slug": "common-collections"
            },
            "worked_example": {
                "title": "Deduplicating while counting",
                "code": "items = ['apple', 'banana', 'apple', 'orange']\nunique = set(items)\nprint('Unique items:', sorted(unique))",
                "explanation": "Sets drop duplicate entries in O(1) average lookup time."
            },
            "guided_practice_refs": [],
            "independent_practice_refs": ["python-word-count", "python-pangram", "python-deduplicate-list"],
            "review_eligible": True,
            "availability_status": "available"
        },

        # --- SQL and PostgreSQL ---
        {
            "key": "step-sql-tables-1",
            "subject_key": "sql-postgresql",
            "topic_slug": "sql-postgresql-tables-keys",
            "title": "Tables, rows and scalar projection",
            "stage": "first_steps",
            "order_index": 1,
            "prerequisite_keys": [],
            "objective": "Understand relational tables, data types, and simple SELECT expressions.",
            "teaching_ref": {
                "source_type": "candidate_lesson",
                "content_key": "forge/placement-foundations/sql-postgresql/sql-postgresql-tables-keys",
                "section_slug": "intuition"
            },
            "worked_example": {
                "title": "Scalar SELECT",
                "code": "SELECT 100 AS base_score, 'Active' AS status;",
                "explanation": "SELECT computes and labels output columns."
            },
            "guided_practice_refs": ["sql-first-select-constant"],
            "independent_practice_refs": ["sql-distinct-cities"],
            "review_eligible": True,
            "availability_status": "available"
        },
        {
            "key": "step-sql-tables-2",
            "subject_key": "sql-postgresql",
            "topic_slug": "sql-postgresql-tables-keys",
            "title": "Reading columns and table structure",
            "stage": "first_steps",
            "order_index": 2,
            "prerequisite_keys": ["step-sql-tables-1"],
            "objective": "Project specific columns from an existing table.",
            "teaching_ref": {
                "source_type": "candidate_lesson",
                "content_key": "forge/placement-foundations/sql-postgresql/sql-postgresql-tables-keys",
                "section_slug": "worked-example"
            },
            "worked_example": {
                "title": "Column projection",
                "code": "SELECT first_name, email FROM employees;",
                "explanation": "Selecting specific columns reduces unnecessary data transfer."
            },
            "guided_practice_refs": ["sql-first-read-one-col"],
            "independent_practice_refs": ["sql-products-in-stock"],
            "review_eligible": True,
            "availability_status": "available"
        },
        {
            "key": "step-sql-select-filter",
            "subject_key": "sql-postgresql",
            "topic_slug": "sql-postgresql-select-filter",
            "title": "Filtering rows with WHERE",
            "stage": "first_steps",
            "order_index": 3,
            "prerequisite_keys": ["step-sql-tables-2"],
            "objective": "Filter rows using comparison operators, AND, OR, and string matches.",
            "teaching_ref": {
                "source_type": "legacy_lesson",
                "content_key": "ai-engineer/v1/sql-postgresql/select-basics",
                "section_slug": "filtering-rows"
            },
            "worked_example": {
                "title": "Row filtering with predicates",
                "code": "SELECT id, product_name FROM products WHERE price > 50 AND in_stock = true;",
                "explanation": "Only rows satisfying all WHERE predicates are returned."
            },
            "guided_practice_refs": ["sql-first-where"],
            "independent_practice_refs": ["sql-active-users", "sql-user-search"],
            "review_eligible": True,
            "availability_status": "available"
        },
        {
            "key": "step-sql-nulls",
            "subject_key": "sql-postgresql",
            "topic_slug": "sql-postgresql-values-nulls",
            "title": "Handling missing data (NULL)",
            "stage": "first_steps",
            "order_index": 4,
            "prerequisite_keys": ["step-sql-select-filter"],
            "objective": "Distinguish NULL from empty values and use IS NULL and COALESCE.",
            "teaching_ref": {
                "source_type": "legacy_lesson",
                "content_key": "ai-engineer/v1/sql-postgresql/relational-foundations",
                "section_slug": "nullability"
            },
            "worked_example": {
                "title": "COALESCE fallback for NULL",
                "code": "SELECT name, COALESCE(phone, 'No phone') AS contact_phone FROM customers;",
                "explanation": "COALESCE returns the first non-null argument."
            },
            "guided_practice_refs": ["sql-first-null-check"],
            "independent_practice_refs": ["sql-null-email", "sql-coalesce-address"],
            "review_eligible": True,
            "availability_status": "available"
        },
        {
            "key": "step-sql-ordering-limits",
            "subject_key": "sql-postgresql",
            "topic_slug": "sql-postgresql-ordering-limits",
            "title": "Sorting and limiting results",
            "stage": "first_steps",
            "order_index": 5,
            "prerequisite_keys": ["step-sql-nulls"],
            "objective": "Sort rows with ORDER BY ASC/DESC and truncate with LIMIT.",
            "teaching_ref": {
                "source_type": "legacy_lesson",
                "content_key": "ai-engineer/v1/sql-postgresql/select-basics",
                "section_slug": "sorting-and-pagination"
            },
            "worked_example": {
                "title": "ORDER BY and LIMIT",
                "code": "SELECT product_name, price FROM products ORDER BY price DESC LIMIT 5;",
                "explanation": "Sorts descending by price and returns the top 5 most expensive products."
            },
            "guided_practice_refs": [],
            "independent_practice_refs": ["sql-recent-orders"],
            "review_eligible": True,
            "availability_status": "available"
        },
        {
            "key": "step-sql-aggregations",
            "subject_key": "sql-postgresql",
            "topic_slug": "sql-postgresql-aggregation",
            "title": "GROUP BY and summary aggregates",
            "stage": "beginner",
            "order_index": 6,
            "prerequisite_keys": ["step-sql-ordering-limits"],
            "objective": "Aggregate rows using COUNT, SUM, AVG, and GROUP BY.",
            "teaching_ref": {
                "source_type": "legacy_lesson",
                "content_key": "ai-engineer/v1/sql-postgresql/aggregation",
                "section_slug": "group-by-partitioning"
            },
            "worked_example": {
                "title": "Department average salary",
                "code": "SELECT department_id, COUNT(*) AS headcount, AVG(salary) AS avg_sal FROM employees GROUP BY department_id;",
                "explanation": "GROUP BY collapses rows with identical department_id into summary rows."
            },
            "guided_practice_refs": [],
            "independent_practice_refs": ["sql-dept-avg-salary", "sql-daily-sales", "sql-order-count-by-status"],
            "review_eligible": True,
            "availability_status": "available"
        },
        {
            "key": "step-sql-joins",
            "subject_key": "sql-postgresql",
            "topic_slug": "sql-postgresql-joins",
            "title": "Relational joins (INNER and LEFT)",
            "stage": "developing",
            "order_index": 7,
            "prerequisite_keys": ["step-sql-aggregations"],
            "objective": "Combine related tables using explicit join predicates.",
            "teaching_ref": {
                "source_type": "legacy_lesson",
                "content_key": "ai-engineer/v1/sql-postgresql/joins",
                "section_slug": "inner-and-outer-joins"
            },
            "worked_example": {
                "title": "INNER JOIN on foreign key",
                "code": "SELECT o.id, c.customer_name, o.amount FROM orders o JOIN customers c ON o.customer_id = c.id;",
                "explanation": "Matches rows where order customer_id equals customer primary key id."
            },
            "guided_practice_refs": [],
            "independent_practice_refs": ["sql-customers-with-orders", "sql-dept-head-count", "sql-customer-totals"],
            "review_eligible": True,
            "availability_status": "available"
        },

        # --- Data Structures and Algorithms ---
        {
            "key": "step-dsa-contracts-1",
            "subject_key": "dsa",
            "topic_slug": "dsa-problem-contracts",
            "title": "Problem contracts, input bounds, and tracing",
            "stage": "first_steps",
            "order_index": 1,
            "prerequisite_keys": [],
            "objective": "Trace algorithm execution step-by-step and verify boundary behavior.",
            "teaching_ref": {
                "source_type": "candidate_lesson",
                "content_key": "forge/placement-foundations/dsa/dsa-problem-contracts",
                "section_slug": "intuition"
            },
            "worked_example": {
                "title": "Tracing loop invariants",
                "code": "def trace_sum(nums):\n    s = 0\n    for x in nums:\n        s += x\n    return s\nprint(trace_sum([1, 2, 3]))",
                "explanation": "Before loop s=0; after element 1, s=1; after element 2, s=3; after 3, s=6."
            },
            "guided_practice_refs": ["dsa-first-tracing-list"],
            "independent_practice_refs": ["dsa-reverse-string"],
            "review_eligible": True,
            "availability_status": "available"
        },
        {
            "key": "step-dsa-scan-1",
            "subject_key": "dsa",
            "topic_slug": "dsa-arrays-strings",
            "title": "Linear scanning and in-place manipulation",
            "stage": "first_steps",
            "order_index": 2,
            "prerequisite_keys": ["step-dsa-contracts-1"],
            "objective": "Traverse arrays linearly, maintaining read and write pointers.",
            "teaching_ref": {
                "source_type": "legacy_lesson",
                "content_key": "ai-engineer/v1/dsa/arrays",
                "section_slug": "linear-traversal"
            },
            "worked_example": {
                "title": "Moving elements in a scan",
                "code": "def move_zeros(nums):\n    write = 0\n    for read in range(len(nums)):\n        if nums[read] != 0:\n            nums[write] = nums[read]\n            write += 1\n    while write < len(nums):\n        nums[write] = 0\n        write += 1\n    return nums",
                "explanation": "Separating read and write indices avoids allocating extra memory."
            },
            "guided_practice_refs": ["dsa-first-linear-scan"],
            "independent_practice_refs": ["dsa-move-zeroes", "dsa-range-sum-query"],
            "review_eligible": True,
            "availability_status": "available"
        },
        {
            "key": "step-dsa-hash-1",
            "subject_key": "dsa",
            "topic_slug": "dsa-hashing-sets",
            "title": "Hash maps and frequency counting",
            "stage": "first_steps",
            "order_index": 3,
            "prerequisite_keys": ["step-dsa-scan-1"],
            "objective": "Trade space for time by caching element occurrences in a hash map.",
            "teaching_ref": {
                "source_type": "legacy_lesson",
                "content_key": "ai-engineer/v1/dsa/hash-tables",
                "section_slug": "frequency-maps"
            },
            "worked_example": {
                "title": "Two-sum hash map lookup",
                "code": "def two_sum(nums, target):\n    seen = {}\n    for i, x in enumerate(nums):\n        diff = target - x\n        if diff in seen:\n            return (seen[diff], i)\n        seen[x] = i\n    return ()\nprint(two_sum([2, 7, 11, 15], 9))",
                "explanation": "Looking up the complement in `seen` reduces time complexity from O(n^2) to O(n)."
            },
            "guided_practice_refs": ["dsa-first-freq-counting"],
            "independent_practice_refs": ["dsa-valid-anagram", "dsa-two-sum-indices", "dsa-ransom-note"],
            "review_eligible": True,
            "availability_status": "available"
        },
        {
            "key": "step-dsa-two-pointers",
            "subject_key": "dsa",
            "topic_slug": "dsa-two-pointers",
            "title": "Two-pointer convergence and sorting",
            "stage": "developing",
            "order_index": 4,
            "prerequisite_keys": ["step-dsa-hash-1"],
            "objective": "Use converging pointers on sorted arrays to achieve optimal O(n) solutions.",
            "teaching_ref": {
                "source_type": "legacy_lesson",
                "content_key": "ai-engineer/v1/dsa/two-pointers",
                "section_slug": "converging-pointers"
            },
            "worked_example": {
                "title": "Pair sum on sorted array",
                "code": "def find_pair(nums, target):\n    left, right = 0, len(nums) - 1\n    while left < right:\n        cur = nums[left] + nums[right]\n        if cur == target:\n            return (left, right)\n        elif cur < target:\n            left += 1\n        else:\n            right -= 1\n    return ()",
                "explanation": "Adjusting either pointer deterministically moves the sum closer to target."
            },
            "guided_practice_refs": [],
            "independent_practice_refs": ["dsa-first-pair", "dsa-remove-duplicates-sorted"],
            "review_eligible": True,
            "availability_status": "available"
        },

        # --- Quantitative Aptitude ---
        {
            "key": "step-apt-numbers-1",
            "subject_key": "quantitative-aptitude",
            "topic_slug": "quantitative-aptitude-number-operations",
            "title": "Numbers, operations and precedence",
            "stage": "first_steps",
            "order_index": 1,
            "prerequisite_keys": [],
            "objective": "Apply order of operations (BODMAS/PEMDAS) and signed arithmetic to calculations.",
            "teaching_ref": {
                "source_type": "candidate_lesson",
                "content_key": "forge/placement-foundations/quantitative-aptitude/quantitative-aptitude-number-operations",
                "section_slug": "intuition"
            },
            "worked_example": {
                "title": "Order of operations",
                "code": "# 8 + 4 * (6 - 2) / 2 = 8 + 4 * 4 / 2 = 8 + 16 / 2 = 8 + 8 = 16",
                "explanation": "Brackets are evaluated first, then multiplication and division left-to-right, then addition."
            },
            "guided_practice_refs": [],
            "independent_practice_refs": [],
            "review_eligible": True,
            "availability_status": "available"
        },

        # --- Logical Reasoning ---
        {
            "key": "step-reason-patterns-1",
            "subject_key": "logical-reasoning",
            "topic_slug": "logical-reasoning-patterns-classification",
            "title": "Pattern recognition and classification",
            "stage": "first_steps",
            "order_index": 1,
            "prerequisite_keys": [],
            "objective": "Identify underlying rules in sequences and classify items based on stated constraints.",
            "teaching_ref": {
                "source_type": "candidate_lesson",
                "content_key": "forge/placement-foundations/logical-reasoning/logical-reasoning-patterns-classification",
                "section_slug": "intuition"
            },
            "worked_example": {
                "title": "Rule deduction",
                "code": "# Sequence: 2, 6, 12, 20, 30 ...\n# Differences: +4, +6, +8, +10 -> Next difference is +12 -> 42.",
                "explanation": "Analyzing differences between consecutive terms reveals a linear progression of +2."
            },
            "guided_practice_refs": [],
            "independent_practice_refs": [],
            "review_eligible": True,
            "availability_status": "available"
        },

        # --- Verbal Ability & English ---
        {
            "key": "step-verbal-structure-1",
            "subject_key": "verbal-english",
            "topic_slug": "verbal-english-sentence-structure",
            "title": "Sentence structure and clause boundaries",
            "stage": "first_steps",
            "order_index": 1,
            "prerequisite_keys": [],
            "objective": "Identify subject, verb, and object components and avoid comma splices or run-on sentences.",
            "teaching_ref": {
                "source_type": "candidate_lesson",
                "content_key": "forge/placement-foundations/verbal-english/verbal-english-sentence-structure",
                "section_slug": "intuition"
            },
            "worked_example": {
                "title": "Subject-verb alignment",
                "code": "# Incorrect: 'The group of students were studying.'\n# Correct: 'The group of students was studying.' (Subject is singular 'group')",
                "explanation": "Prepositional phrases between the subject and verb do not alter subject number."
            },
            "guided_practice_refs": [],
            "independent_practice_refs": [],
            "review_eligible": True,
            "availability_status": "available"
        },

        # --- System Design Fundamentals ---
        {
            "key": "step-sys-requirements-1",
            "subject_key": "system-design",
            "topic_slug": "system-design-requirements",
            "title": "Functional vs non-functional requirements",
            "stage": "first_steps",
            "order_index": 1,
            "prerequisite_keys": [],
            "objective": "Distinguish feature capabilities (functional) from quality attributes like latency and uptime.",
            "teaching_ref": {
                "source_type": "candidate_lesson",
                "content_key": "forge/placement-foundations/system-design/system-design-requirements",
                "section_slug": "intuition"
            },
            "worked_example": {
                "title": "Requirement categorization",
                "code": "# 'A user can upload an image' -> Functional requirement\n# 'The image must be processed within 500ms' -> Non-functional (performance)",
                "explanation": "Functional requirements define what the system does; non-functional define how well it performs."
            },
            "guided_practice_refs": [],
            "independent_practice_refs": [],
            "review_eligible": True,
            "availability_status": "available"
        },

        # --- AI Fundamentals ---
        {
            "key": "step-ai-foundations-1",
            "subject_key": "ai-fundamentals",
            "topic_slug": "ai-fundamentals-ai-ml-dl",
            "title": "AI, ML, and deep learning boundaries",
            "stage": "first_steps",
            "order_index": 1,
            "prerequisite_keys": [],
            "objective": "Understand the hierarchy between artificial intelligence, machine learning, and deep neural nets.",
            "teaching_ref": {
                "source_type": "candidate_lesson",
                "content_key": "forge/placement-foundations/ai-fundamentals/ai-fundamentals-ai-ml-dl",
                "section_slug": "intuition"
            },
            "worked_example": {
                "title": "Rule-based vs Learning-based",
                "code": "# Rule-based: if email.contains('lottery') -> spam\n# ML-based: model trained on 100k labeled emails learns token statistical weights",
                "explanation": "Traditional software relies on explicit coded rules; machine learning learns parameters from data."
            },
            "guided_practice_refs": [],
            "independent_practice_refs": [],
            "review_eligible": True,
            "availability_status": "available"
        },

        # --- Interview Communication ---
        {
            "key": "step-interview-intro-1",
            "subject_key": "interview-communication",
            "topic_slug": "interview-communication-introductions",
            "title": "Structuring a technical self-introduction",
            "stage": "first_steps",
            "order_index": 1,
            "prerequisite_keys": [],
            "objective": "Deliver a concise 60-90 second introduction covering education, technical strengths, and recent projects.",
            "teaching_ref": {
                "source_type": "candidate_lesson",
                "content_key": "forge/placement-foundations/interview-communication/interview-communication-introductions",
                "section_slug": "intuition"
            },
            "worked_example": {
                "title": "Present-Past-Future model",
                "code": "# 1. Present: Current status and core strengths (e.g. backend Python & SQL)\n# 2. Past: Meaningful project built and deterministic test evidence\n# 3. Future: Why this specific engineering role aligns with current growth",
                "explanation": "A structured introduction stays focused, relevant, and under 90 seconds."
            },
            "guided_practice_refs": [],
            "independent_practice_refs": [],
            "review_eligible": True,
            "availability_status": "available"
        }
    ]
}

# -------------------------------------------------------------
# 4. APPLIED AI ENGINEERING SCOPE EXTENSION (Section I)
# -------------------------------------------------------------
APPLIED_AI_SCOPE_EXTENSION_DATA = {
    "format_version": 1,
    "version": "1.0.0",
    "status": "proposed_extension",
    "rationale": "Audit of fresher readiness beyond isolated algorithmic interview puzzles. Bridges the gap to applied software engineering.",
    "modules": [
        {
            "key": "ext-backend-fastapi",
            "title": "Python Backend Development with FastAPI",
            "description": "Constructing RESTful API endpoints, request validation with Pydantic, HTTP status codes, and dependency injection.",
            "competencies": [
                "Define GET/POST/PATCH/DELETE route handlers with typed parameters",
                "Validate incoming JSON payloads with Pydantic schemas",
                "Return appropriate HTTP status codes (200, 201, 400, 404, 422)",
                "Organize modular router architectures with APIRouter"
            ],
            "prerequisites": ["python-functions", "python-collections"]
        },
        {
            "key": "ext-db-integration",
            "title": "PostgreSQL & Database Integration",
            "description": "Connecting Python services to PostgreSQL, query parameterization to prevent SQL injection, and transaction safety.",
            "competencies": [
                "Execute parameterized queries safely via DB-API or SQLModel/SQLAlchemy",
                "Manage connection pooling and session lifecycles",
                "Handle database exceptions and rollback transactions on failure",
                "Design normalized schema migrations"
            ],
            "prerequisites": ["ext-backend-fastapi", "sql-postgresql-tables-keys"]
        },
        {
            "key": "ext-testing-debugging",
            "title": "Deterministic Testing & Debugging",
            "description": "Writing unit and integration tests with pytest, mocking external services, and debugging runtime exceptions.",
            "competencies": [
                "Write pytest test suites covering normal, boundary, and error cases",
                "Use test fixtures and in-memory databases for fast isolated verification",
                "Debug stack traces using pdb and structured logging",
                "Measure and maintain test coverage on core business logic"
            ],
            "prerequisites": ["ext-backend-fastapi"]
        },
        {
            "key": "ext-git-docker",
            "title": "Git & Containerization Fundamentals",
            "description": "Version control best practices, branch workflows, and reproducible environments with Docker.",
            "competencies": [
                "Manage branches, staging, commits, and merge conflicts cleanly",
                "Write clear, conventional commit messages and pull requests",
                "Author Dockerfile definitions for Python applications",
                "Run multi-container local environments using docker-compose"
            ],
            "prerequisites": ["ext-backend-fastapi"]
        },
        {
            "key": "ext-llm-rag-agents",
            "title": "LLM Integration, Embeddings, RAG & Agents",
            "description": "Integrating model providers via structured output, vector similarity search, retrieval augmented generation, and tool calling.",
            "competencies": [
                "Generate structured JSON from LLMs with schema enforcement",
                "Compute and store text embeddings in vector stores (e.g. pgvector)",
                "Implement chunking, retrieval, and citation verification pipelines",
                "Construct bounded agentic loops with deterministic tool validation"
            ],
            "prerequisites": ["ext-db-integration", "ext-backend-fastapi"]
        },
        {
            "key": "ext-project-deployment",
            "title": "Deployment Fundamentals & Project Explanation",
            "description": "Deploying web applications, environment configuration, health checks, and presenting technical architectural decisions.",
            "competencies": [
                "Configure 12-factor environment variables and secret isolation",
                "Implement liveness and readiness health check endpoints",
                "Articulate design tradeoffs, system bottlenecks, and failure modes",
                "Defend architectural choices under senior engineer scrutiny"
            ],
            "prerequisites": ["ext-llm-rag-agents", "ext-git-docker"]
        }
    ]
}

def main():
    # Write files
    (OUT_DIR / "arena-stages.json").write_text(json.dumps(ARENA_STAGES_DATA, indent=2), encoding="utf-8")
    (OUT_DIR / "beginner-exercises.json").write_text(json.dumps(BEGINNER_EXERCISES_DATA, indent=2), encoding="utf-8")
    (OUT_DIR / "concept-steps.json").write_text(json.dumps(CONCEPT_STEPS_DATA, indent=2), encoding="utf-8")
    (OUT_DIR / "applied-ai-scope-extension.json").write_text(json.dumps(APPLIED_AI_SCOPE_EXTENSION_DATA, indent=2), encoding="utf-8")
    print(f"Generated learning path files in {OUT_DIR}:")
    print(f"  - arena-stages.json: {len(ARENA_STAGES_DATA['problem_mappings'])} problem mappings across {len(ARENA_STAGES_DATA['stages'])} stages")
    print(f"  - beginner-exercises.json: {len(BEGINNER_EXERCISES_DATA['exercises'])} beginner exercises")
    print(f"  - concept-steps.json: {len(CONCEPT_STEPS_DATA['concepts'])} concept steps across 9 subjects")
    print(f"  - applied-ai-scope-extension.json: {len(APPLIED_AI_SCOPE_EXTENSION_DATA['modules'])} proposed modules")

if __name__ == "__main__":
    main()
