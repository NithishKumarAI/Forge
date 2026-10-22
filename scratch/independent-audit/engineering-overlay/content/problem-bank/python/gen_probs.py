import json
import os

base_path = r"C:\My PC\git\Forge\content\problem-bank\python"
os.makedirs(base_path, exist_ok=True)

problems = [
    {
        "key": "python-merge-sorted-lists",
        "title": "Merge two sorted lists",
        "track": "python",
        "topic_tags": ["lists", "two-pointers"],
        "difficulty": "easy",
        "interview_frequency": "high",
        "estimated_minutes": 15,
        "statement_markdown": "Write a function `merge_sorted(a, b)` that takes two sorted lists and merges them into a single sorted list.",
        "constraints": ["Elements are integers.", "Lists are sorted in non-decreasing order."],
        "examples": [{"input": "[1,3,5], [2,4,6]", "output": "[1,2,3,4,5,6]", "explanation": "Merged list is sorted."}],
        "starter_code": "def merge_sorted(a: list[int], b: list[int]) -> list[int]:\n    pass",
        "hints": ["Use two pointers."],
        "explanation": "Iterate through both lists comparing elements.",
        "reference_solution": "def merge_sorted(a: list[int], b: list[int]) -> list[int]:\n    res = []\n    i, j = 0, 0\n    while i < len(a) and j < len(b):\n        if a[i] < b[j]:\n            res.append(a[i])\n            i += 1\n        else:\n            res.append(b[j])\n            j += 1\n    res.extend(a[i:])\n    res.extend(b[j:])\n    return res",
        "complexity": "O(n+m) time and O(n+m) space.",
        "validation": {
            "judge_mode": "function",
            "function_name": "merge_sorted",
            "sample_tests": [
                {"name": "sample", "args": [[1,3,5], [2,4,6]], "kwargs": {}, "expected": [1,2,3,4,5,6]},
                {"name": "empty_a", "args": [[], [1]], "kwargs": {}, "expected": [1]},
                {"name": "empty_b", "args": [[1], []], "kwargs": {}, "expected": [1]}
            ],
            "hidden_tests": [
                {"name": "hidden", "args": [[2,4], [1,3,5]], "kwargs": {}, "expected": [1,2,3,4,5]}
            ]
        },
        "source_type": "original",
        "version": "1.0.0",
        "mapped_topic": "dsa/two-pointers"
    },
    {
        "key": "python-stack-balanced-brackets",
        "title": "Balanced brackets",
        "track": "python",
        "topic_tags": ["stacks", "strings"],
        "difficulty": "easy",
        "interview_frequency": "high",
        "estimated_minutes": 15,
        "statement_markdown": "Write a function `is_balanced(s)` to check if brackets ()[]{} are balanced.",
        "constraints": ["String contains only bracket characters."],
        "examples": [{"input": "()[]{}", "output": "True", "explanation": "All brackets closed properly."}],
        "starter_code": "def is_balanced(s: str) -> bool:\n    pass",
        "hints": ["Use a stack to keep track of opening brackets."],
        "explanation": "Push opening brackets onto a stack. When encountering a closing bracket, pop the stack and check if they match.",
        "reference_solution": "def is_balanced(s: str) -> bool:\n    stack = []\n    mapping = {')': '(', ']': '[', '}': '{'}\n    for char in s:\n        if char in mapping:\n            top_element = stack.pop() if stack else '#'\n            if mapping[char] != top_element:\n                return False\n        else:\n            stack.append(char)\n    return not stack",
        "complexity": "O(n) time and O(n) space.",
        "validation": {
            "judge_mode": "function",
            "function_name": "is_balanced",
            "sample_tests": [
                {"name": "sample1", "args": ["()[]{}"], "kwargs": {}, "expected": True},
                {"name": "sample2", "args": ["([)]"], "kwargs": {}, "expected": False},
                {"name": "sample3", "args": ["{[]}"], "kwargs": {}, "expected": True},
                {"name": "empty", "args": [""], "kwargs": {}, "expected": True}
            ],
            "hidden_tests": [
                {"name": "hidden", "args": ["((("], "kwargs": {}, "expected": False}
            ]
        },
        "source_type": "original",
        "version": "1.0.0",
        "mapped_topic": "dsa/stacks"
    },
    {
        "key": "python-max-profit",
        "title": "Best stock trade",
        "track": "python",
        "topic_tags": ["arrays", "greedy"],
        "difficulty": "easy",
        "interview_frequency": "high",
        "estimated_minutes": 15,
        "statement_markdown": "Write `max_profit(prices)` to find the maximum profit from one transaction (buy then sell). Return 0 if no profit.",
        "constraints": ["List contains non-negative integers."],
        "examples": [{"input": "[7,1,5,3,6,4]", "output": "5", "explanation": "Buy at 1, sell at 6."}],
        "starter_code": "def max_profit(prices: list[int]) -> int:\n    pass",
        "hints": ["Track the minimum price seen so far."],
        "explanation": "Iterate through the prices, updating the minimum price seen and calculating the potential profit at each step.",
        "reference_solution": "def max_profit(prices: list[int]) -> int:\n    min_price = float('inf')\n    max_prof = 0\n    for price in prices:\n        if price < min_price:\n            min_price = price\n        elif price - min_price > max_prof:\n            max_prof = price - min_price\n    return max_prof",
        "complexity": "O(n) time and O(1) space.",
        "validation": {
            "judge_mode": "function",
            "function_name": "max_profit",
            "sample_tests": [
                {"name": "sample1", "args": [[7,1,5,3,6,4]], "kwargs": {}, "expected": 5},
                {"name": "sample2", "args": [[7,6,4,3,1]], "kwargs": {}, "expected": 0},
                {"name": "sample3", "args": [[1,2]], "kwargs": {}, "expected": 1}
            ],
            "hidden_tests": [
                {"name": "hidden", "args": [[2,4,1]], "kwargs": {}, "expected": 2}
            ]
        },
        "source_type": "original",
        "version": "1.0.0",
        "mapped_topic": "dsa/arrays"
    },
    {
        "key": "python-count-islands",
        "title": "Count connected regions",
        "track": "python",
        "topic_tags": ["graphs", "dfs"],
        "difficulty": "medium",
        "interview_frequency": "high",
        "estimated_minutes": 20,
        "statement_markdown": "Write `count_regions(grid)` to count 4-directionally connected regions of 1s in a binary grid.",
        "constraints": ["Grid can be empty.", "Grid elements are 0 or 1."],
        "examples": [{"input": "[[1,0],[0,1]]", "output": "2", "explanation": "Two disconnected 1s."}],
        "starter_code": "def count_regions(grid: list[list[int]]) -> int:\n    pass",
        "hints": ["Use DFS or BFS to traverse connected components."],
        "explanation": "Iterate through the grid. When encountering a 1, increment region count and use DFS to mark all connected 1s as visited.",
        "reference_solution": "def count_regions(grid: list[list[int]]) -> int:\n    if not grid:\n        return 0\n    regions = 0\n    rows, cols = len(grid), len(grid[0])\n    visited = set()\n    def dfs(r, c):\n        if r < 0 or c < 0 or r >= rows or c >= cols or grid[r][c] == 0 or (r, c) in visited:\n            return\n        visited.add((r, c))\n        dfs(r + 1, c)\n        dfs(r - 1, c)\n        dfs(r, c + 1)\n        dfs(r, c - 1)\n    for r in range(rows):\n        for c in range(cols):\n            if grid[r][c] == 1 and (r, c) not in visited:\n                regions += 1\n                dfs(r, c)\n    return regions",
        "complexity": "O(m*n) time and O(m*n) space.",
        "validation": {
            "judge_mode": "function",
            "function_name": "count_regions",
            "sample_tests": [
                {"name": "sample1", "args": [[[1,0],[0,1]]], "kwargs": {}, "expected": 2},
                {"name": "sample2", "args": [[[1,1],[1,0]]], "kwargs": {}, "expected": 1},
                {"name": "sample3", "args": [[[0,0],[0,0]]], "kwargs": {}, "expected": 0}
            ],
            "hidden_tests": [
                {"name": "hidden", "args": [[[1]]], "kwargs": {}, "expected": 1}
            ]
        },
        "source_type": "original",
        "version": "1.0.0",
        "mapped_topic": "dsa/graphs"
    },
    {
        "key": "python-find-duplicate",
        "title": "Find the duplicate number",
        "track": "python",
        "topic_tags": ["arrays", "hash-maps"],
        "difficulty": "easy",
        "interview_frequency": "high",
        "estimated_minutes": 15,
        "statement_markdown": "Write `find_duplicate(nums)` to find the one duplicate integer in a list of n+1 integers where each is in [1,n].",
        "constraints": ["List size > 1."],
        "examples": [{"input": "[1,3,4,2,2]", "output": "2", "explanation": "2 is duplicated."}],
        "starter_code": "def find_duplicate(nums: list[int]) -> int:\n    pass",
        "hints": ["Use a set to track seen numbers."],
        "explanation": "Store numbers in a set as you iterate. If a number is already in the set, it's the duplicate.",
        "reference_solution": "def find_duplicate(nums: list[int]) -> int:\n    seen = set()\n    for num in nums:\n        if num in seen:\n            return num\n        seen.add(num)\n    return -1",
        "complexity": "O(n) time and O(n) space.",
        "validation": {
            "judge_mode": "function",
            "function_name": "find_duplicate",
            "sample_tests": [
                {"name": "sample1", "args": [[1,3,4,2,2]], "kwargs": {}, "expected": 2},
                {"name": "sample2", "args": [[3,1,3,4,2]], "kwargs": {}, "expected": 3}
            ],
            "hidden_tests": [
                {"name": "hidden", "args": [[2,2]], "kwargs": {}, "expected": 2}
            ]
        },
        "source_type": "original",
        "version": "1.0.0",
        "mapped_topic": "dsa/hash-maps"
    },
    {
        "key": "python-missing-number",
        "title": "Missing number in range",
        "track": "python",
        "topic_tags": ["arrays", "math"],
        "difficulty": "easy",
        "interview_frequency": "high",
        "estimated_minutes": 15,
        "statement_markdown": "Write `missing_number(nums)` where list contains n distinct numbers from 0..n with one missing. Find it.",
        "constraints": ["List has size n."],
        "examples": [{"input": "[3,0,1]", "output": "2", "explanation": "2 is missing from 0..3."}],
        "starter_code": "def missing_number(nums: list[int]) -> int:\n    pass",
        "hints": ["Calculate the expected sum using n*(n+1)//2."],
        "explanation": "Compare the expected sum of 0..n with the actual sum of the array.",
        "reference_solution": "def missing_number(nums: list[int]) -> int:\n    n = len(nums)\n    expected = n * (n + 1) // 2\n    return expected - sum(nums)",
        "complexity": "O(n) time and O(1) space.",
        "validation": {
            "judge_mode": "function",
            "function_name": "missing_number",
            "sample_tests": [
                {"name": "sample1", "args": [[3,0,1]], "kwargs": {}, "expected": 2},
                {"name": "sample2", "args": [[0,1]], "kwargs": {}, "expected": 2},
                {"name": "sample3", "args": [[9,6,4,2,3,5,7,0,1]], "kwargs": {}, "expected": 8}
            ],
            "hidden_tests": [
                {"name": "hidden", "args": [[0]], "kwargs": {}, "expected": 1}
            ]
        },
        "source_type": "original",
        "version": "1.0.0",
        "mapped_topic": "dsa/arrays"
    },
    {
        "key": "python-longest-common-prefix",
        "title": "Longest common prefix",
        "track": "python",
        "topic_tags": ["strings", "arrays"],
        "difficulty": "easy",
        "interview_frequency": "high",
        "estimated_minutes": 15,
        "statement_markdown": "Write `longest_common_prefix(words)` to find the longest prefix common to all words.",
        "constraints": ["Words contain lowercase letters.", "List can be empty."],
        "examples": [{"input": "['flower','flow','flight']", "output": "'fl'", "explanation": "Common prefix is fl."}],
        "starter_code": "def longest_common_prefix(words: list[str]) -> str:\n    pass",
        "hints": ["Start with the first word as the prefix and shorten it until it matches."],
        "explanation": "Iterate through words, checking if the current prefix is a prefix of the word. If not, trim the prefix by one character at a time.",
        "reference_solution": "def longest_common_prefix(words: list[str]) -> str:\n    if not words:\n        return \"\"\n    prefix = words[0]\n    for word in words[1:]:\n        while not word.startswith(prefix):\n            prefix = prefix[:-1]\n            if not prefix:\n                return \"\"\n    return prefix",
        "complexity": "O(S) time where S is sum of all characters, O(1) space.",
        "validation": {
            "judge_mode": "function",
            "function_name": "longest_common_prefix",
            "sample_tests": [
                {"name": "sample1", "args": [["flower","flow","flight"]], "kwargs": {}, "expected": "fl"},
                {"name": "sample2", "args": [["dog","racecar"]], "kwargs": {}, "expected": ""},
                {"name": "sample3", "args": [["ab","ab"]], "kwargs": {}, "expected": "ab"}
            ],
            "hidden_tests": [
                {"name": "hidden", "args": [[]], "kwargs": {}, "expected": ""}
            ]
        },
        "source_type": "original",
        "version": "1.0.0",
        "mapped_topic": "python/strings"
    },
    {
        "key": "python-group-anagrams",
        "title": "Group anagrams together",
        "track": "python",
        "topic_tags": ["hash-maps", "strings"],
        "difficulty": "medium",
        "interview_frequency": "high",
        "estimated_minutes": 20,
        "statement_markdown": "Write `group_anagrams(words)` to group words that are anagrams. Return a list of groups, where each group is sorted alphabetically, and the list of groups is sorted by the first element.",
        "constraints": ["Words contain lowercase letters."],
        "examples": [{"input": "['eat','tea','ate']", "output": "[['ate','eat','tea']]", "explanation": "Anagrams are grouped and sorted."}],
        "starter_code": "def group_anagrams(words: list[str]) -> list[list[str]]:\n    pass",
        "hints": ["Use sorted strings as dictionary keys."],
        "explanation": "Iterate through words, sorting each to use as a hash map key. Group anagrams under the same key.",
        "reference_solution": "def group_anagrams(words: list[str]) -> list[list[str]]:\n    from collections import defaultdict\n    groups = defaultdict(list)\n    for w in words:\n        groups[tuple(sorted(w))].append(w)\n    res = []\n    for g in groups.values():\n        res.append(sorted(g))\n    return sorted(res, key=lambda x: x[0] if x else \"\")",
        "complexity": "O(n * k log k) time where k is max length of word, O(n*k) space.",
        "validation": {
            "judge_mode": "function",
            "function_name": "group_anagrams",
            "sample_tests": [
                {"name": "sample1", "args": [["eat","tea","ate"]], "kwargs": {}, "expected": [["ate","eat","tea"]]}
            ],
            "hidden_tests": [
                {"name": "hidden", "args": [["tan","nat"]], "kwargs": {}, "expected": [["nat","tan"]]}
            ]
        },
        "source_type": "original",
        "version": "1.0.0",
        "mapped_topic": "dsa/hash-maps"
    },
    {
        "key": "python-matrix-spiral",
        "title": "Spiral order matrix traversal",
        "track": "python",
        "topic_tags": ["arrays", "matrices"],
        "difficulty": "medium",
        "interview_frequency": "high",
        "estimated_minutes": 25,
        "statement_markdown": "Write `spiral_order(matrix)` to traverse an m x n matrix in spiral order.",
        "constraints": ["Matrix may be empty."],
        "examples": [{"input": "[[1,2,3],[4,5,6],[7,8,9]]", "output": "[1,2,3,6,9,8,7,4,5]", "explanation": "Trace edge inward."}],
        "starter_code": "def spiral_order(matrix: list[list[int]]) -> list[int]:\n    pass",
        "hints": ["Define bounds: top, bottom, left, right."],
        "explanation": "Maintain layer boundaries and loop while boundaries don't overlap, traversing in 4 directions.",
        "reference_solution": "def spiral_order(matrix: list[list[int]]) -> list[int]:\n    result = []\n    if not matrix:\n        return result\n    top, bottom = 0, len(matrix) - 1\n    left, right = 0, len(matrix[0]) - 1\n    while top <= bottom and left <= right:\n        for c in range(left, right + 1):\n            result.append(matrix[top][c])\n        top += 1\n        for r in range(top, bottom + 1):\n            result.append(matrix[r][right])\n        right -= 1\n        if top <= bottom:\n            for c in range(right, left - 1, -1):\n                result.append(matrix[bottom][c])\n            bottom -= 1\n        if left <= right:\n            for r in range(bottom, top - 1, -1):\n                result.append(matrix[r][left])\n            left += 1\n    return result",
        "complexity": "O(m*n) time and O(1) extra space.",
        "validation": {
            "judge_mode": "function",
            "function_name": "spiral_order",
            "sample_tests": [
                {"name": "sample1", "args": [[[1,2,3],[4,5,6],[7,8,9]]], "kwargs": {}, "expected": [1,2,3,6,9,8,7,4,5]},
                {"name": "sample2", "args": [[[1,2],[3,4]]], "kwargs": {}, "expected": [1,2,4,3]}
            ],
            "hidden_tests": [
                {"name": "hidden", "args": [[[1]]], "kwargs": {}, "expected": [1]}
            ]
        },
        "source_type": "original",
        "version": "1.0.0",
        "mapped_topic": "dsa/arrays"
    },
    {
        "key": "python-valid-parentheses-string",
        "title": "Minimum remove to make valid",
        "track": "python",
        "topic_tags": ["stacks", "strings"],
        "difficulty": "medium",
        "interview_frequency": "high",
        "estimated_minutes": 20,
        "statement_markdown": "Write `min_remove_count(s)` to return the minimum number of parentheses to remove to make the string valid. Only '(' and ')' chars matter.",
        "constraints": ["String only contains parentheses."],
        "examples": [{"input": "'())'", "output": "1", "explanation": "Remove one ')'."}],
        "starter_code": "def min_remove_count(s: str) -> int:\n    pass",
        "hints": ["Track unmatched open and unmatched close brackets."],
        "explanation": "Iterate to count unmatched close brackets and unmatched open brackets.",
        "reference_solution": "def min_remove_count(s: str) -> int:\n    unmatched_open = 0\n    unmatched_close = 0\n    for char in s:\n        if char == '(':\n            unmatched_open += 1\n        elif char == ')':\n            if unmatched_open > 0:\n                unmatched_open -= 1\n            else:\n                unmatched_close += 1\n    return unmatched_open + unmatched_close",
        "complexity": "O(n) time and O(1) space.",
        "validation": {
            "judge_mode": "function",
            "function_name": "min_remove_count",
            "sample_tests": [
                {"name": "sample1", "args": ["())"], "kwargs": {}, "expected": 1},
                {"name": "sample2", "args": ["(()"], "kwargs": {}, "expected": 1},
                {"name": "sample3", "args": ["()"], "kwargs": {}, "expected": 0},
                {"name": "sample4", "args": ["))))"], "kwargs": {}, "expected": 4}
            ],
            "hidden_tests": [
                {"name": "hidden", "args": ["((("], "kwargs": {}, "expected": 3}
            ]
        },
        "source_type": "original",
        "version": "1.0.0",
        "mapped_topic": "dsa/stacks"
    },
    {
        "key": "python-product-except-self",
        "title": "Product of array except self",
        "track": "python",
        "topic_tags": ["arrays", "prefix"],
        "difficulty": "medium",
        "interview_frequency": "high",
        "estimated_minutes": 25,
        "statement_markdown": "Write `product_except_self(nums)` to return an array where result[i] is the product of all elements except nums[i], without using division.",
        "constraints": ["Length is at least 2."],
        "examples": [{"input": "[1,2,3,4]", "output": "[24,12,8,6]", "explanation": "24 = 2*3*4, etc."}],
        "starter_code": "def product_except_self(nums: list[int]) -> list[int]:\n    pass",
        "hints": ["Use prefix and suffix products arrays."],
        "explanation": "Compute the prefix products moving forward, and suffix products moving backward.",
        "reference_solution": "def product_except_self(nums: list[int]) -> list[int]:\n    n = len(nums)\n    res = [1] * n\n    left = 1\n    for i in range(n):\n        res[i] = left\n        left *= nums[i]\n    right = 1\n    for i in range(n - 1, -1, -1):\n        res[i] *= right\n        right *= nums[i]\n    return res",
        "complexity": "O(n) time and O(1) space (ignoring output).",
        "validation": {
            "judge_mode": "function",
            "function_name": "product_except_self",
            "sample_tests": [
                {"name": "sample1", "args": [[1,2,3,4]], "kwargs": {}, "expected": [24,12,8,6]},
                {"name": "sample2", "args": [[2,3]], "kwargs": {}, "expected": [3,2]}
            ],
            "hidden_tests": [
                {"name": "hidden", "args": [[1,0]], "kwargs": {}, "expected": [0,1]}
            ]
        },
        "source_type": "original",
        "version": "1.0.0",
        "mapped_topic": "dsa/arrays"
    },
    {
        "key": "python-valid-bst",
        "title": "Validate binary search tree",
        "track": "python",
        "topic_tags": ["trees", "dfs"],
        "difficulty": "medium",
        "interview_frequency": "high",
        "estimated_minutes": 25,
        "statement_markdown": "Write `is_valid_bst(values)` where values is a level-order representation of a binary tree. Reconstruct the tree and validate if it's a BST.",
        "constraints": ["Values list can contain None."],
        "examples": [{"input": "[2,1,3]", "output": "True", "explanation": "Valid BST structure."}],
        "starter_code": "def is_valid_bst(values: list[int | None]) -> bool:\n    pass",
        "hints": ["Use a helper function to construct the tree.", "Use min and max bounds for node values in the recursion tree."],
        "explanation": "First convert the array to a node-based binary tree, then check if it satisfies the BST condition using a recursive function with lower and upper bounds.",
        "reference_solution": "def is_valid_bst(values: list[int | None]) -> bool:\n    if not values:\n        return True\n    \n    class TreeNode:\n        def __init__(self, val=0, left=None, right=None):\n            self.val = val\n            self.left = left\n            self.right = right\n\n    root = TreeNode(values[0])\n    queue = [root]\n    i = 1\n    while i < len(values):\n        node = queue.pop(0)\n        if i < len(values) and values[i] is not None:\n            node.left = TreeNode(values[i])\n            queue.append(node.left)\n        i += 1\n        if i < len(values) and values[i] is not None:\n            node.right = TreeNode(values[i])\n            queue.append(node.right)\n        i += 1\n        \n    def validate(node, low=-float('inf'), high=float('inf')):\n        if not node:\n            return True\n        if node.val <= low or node.val >= high:\n            return False\n        return validate(node.left, low, node.val) and validate(node.right, node.val, high)\n        \n    return validate(root)",
        "complexity": "O(n) time and O(n) space.",
        "validation": {
            "judge_mode": "function",
            "function_name": "is_valid_bst",
            "sample_tests": [
                {"name": "sample1", "args": [[2,1,3]], "kwargs": {}, "expected": True},
                {"name": "sample2", "args": [[5,1,4,None,None,3,6]], "kwargs": {}, "expected": False}
            ],
            "hidden_tests": [
                {"name": "hidden", "args": [[2,2,2]], "kwargs": {}, "expected": False}
            ]
        },
        "source_type": "original",
        "version": "1.0.0",
        "mapped_topic": "dsa/trees"
    }
]

for p in problems:
    with open(os.path.join(base_path, f"{p['key']}.json"), 'w') as f:
        json.dump(p, f, indent=2)

print("Files created successfully.")
