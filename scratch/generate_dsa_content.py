import json
import os

base_path = r"C:\My PC\git\Forge\content\ai-engineer\v1\dsa"

topics = [
    {
        "slug": "recursion",
        "keywords": ["recursion", "base case", "recursive case", "call stack", "stack overflow", "memoization", "tree recursion", "backtracking", "factorial", "fibonacci"],
        "sections": ["what-is-recursion", "base-case", "recursive-case", "call-stack-model", "stack-overflow", "fibonacci-example", "tree-recursion", "memoization-preview", "tail-recursion-awareness", "backtracking-preview", "common-mistakes", "interview-points"],
        "ex_prefix": "rec"
    },
    {
        "slug": "backtracking",
        "keywords": ["backtracking", "state", "explore", "restore", "pruning", "decision tree", "permutation", "combination", "subset"],
        "sections": ["what-is-backtracking", "decision-tree-model", "state-space", "explore-and-restore", "pruning", "subsets-template", "permutations-template", "combinations-template", "when-to-use", "common-mistakes", "interview-points"],
        "ex_prefix": "bt"
    },
    {
        "slug": "trees",
        "keywords": ["tree", "binary tree", "BST", "root", "leaf", "height", "traversal", "in-order", "pre-order", "post-order", "balance", "recursion"],
        "sections": ["what-is-a-tree", "tree-terminology", "binary-tree", "binary-search-tree", "tree-node-class", "in-order-traversal", "pre-order-traversal", "post-order-traversal", "tree-height", "bst-search", "bst-insert", "balance-awareness", "common-mistakes", "interview-points"],
        "ex_prefix": "tree"
    },
    {
        "slug": "bfs",
        "keywords": ["BFS", "breadth-first search", "level order", "queue", "shortest path", "unweighted", "visited", "neighbors", "layer"],
        "sections": ["what-is-bfs", "level-order-traversal", "queue-based-bfs", "visited-set", "shortest-path-property", "bfs-on-graph", "bfs-template", "when-to-use-bfs", "bfs-vs-dfs", "common-mistakes", "interview-points"],
        "ex_prefix": "bfs"
    },
    {
        "slug": "dfs",
        "keywords": ["DFS", "depth-first search", "recursive", "iterative", "stack", "visited", "pre-order", "post-order", "backtracking", "connected"],
        "sections": ["what-is-dfs", "recursive-dfs", "iterative-dfs", "pre-order-dfs", "post-order-dfs", "connected-components", "cycle-detection", "visited-tracking", "dfs-on-graph", "when-to-use-dfs", "common-mistakes", "interview-points"],
        "ex_prefix": "dfs"
    },
    {
        "slug": "heaps",
        "keywords": ["heap", "min heap", "max heap", "heapq", "priority queue", "top-k", "heappush", "heappop", "O(log n)", "merge streams"],
        "sections": ["what-is-a-heap", "min-heap-vs-max-heap", "heapq-module", "heappush-heappop", "heapify", "top-k-pattern", "merge-sorted-streams", "heap-sort-awareness", "custom-comparison", "heap-as-priority-queue", "common-mistakes", "interview-points"],
        "ex_prefix": "heap"
    },
    {
        "slug": "graphs",
        "keywords": ["graph", "vertex", "edge", "adjacency list", "directed", "undirected", "weighted", "BFS", "DFS", "connected component", "cycle"],
        "sections": ["what-is-a-graph", "vertices-and-edges", "directed-vs-undirected", "weighted-edges", "adjacency-list", "adjacency-matrix", "graph-traversal", "bfs-on-graph", "dfs-on-graph", "connected-components", "cycle-detection", "graph-in-python", "interview-points"],
        "ex_prefix": "graph"
    },
    {
        "slug": "dynamic-programming",
        "keywords": ["dynamic programming", "overlapping subproblems", "optimal substructure", "memoization", "tabulation", "top-down", "bottom-up", "state", "transition", "DP table"],
        "sections": ["what-is-dp", "overlapping-subproblems", "optimal-substructure", "top-down-memoization", "bottom-up-tabulation", "fibonacci-dp", "climbing-stairs-pattern", "1d-dp-template", "2d-dp-template", "state-transition", "dp-optimization-awareness", "common-mistakes", "when-to-use-dp", "interview-points"],
        "ex_prefix": "dp"
    }
]

sources = [
    {"source_id": "python-stdlib-docs", "title": "heapq", "url": "https://docs.python.org/3/library/heapq.html", "retrieved_at": "2026-09-23T00:00:00Z"},
    {"source_id": "python-stdlib-docs", "title": "Python Tutorial - Data Structures", "url": "https://docs.python.org/3/tutorial/datastructures.html", "retrieved_at": "2026-09-23T00:00:00Z"},
    {"source_id": "python-stdlib-docs", "title": "functools.lru_cache", "url": "https://docs.python.org/3/library/functools.html", "retrieved_at": "2026-09-23T00:00:00Z"}
]

for t in topics:
    slug = t["slug"]
    topic_dir = os.path.join(base_path, slug)
    os.makedirs(topic_dir, exist_ok=True)
    
    # Generate lesson.json
    lesson = {
        "curriculum_key": "default-ai-engineer",
        "track_slug": "dsa",
        "topic_slug": slug,
        "title": slug.replace('-', ' ').title(),
        "description": f"Learn about {slug.replace('-', ' ')} in Python.",
        "version": "1.0.0",
        "learning_objectives": [f"Understand {slug}", "Implement basic templates", "Recognize in interviews", "Write optimized code"],
        "prerequisites": [],
        "sections": [],
        "summary": [f"{slug} is a key concept.", "Mastering it helps in interviews.", "Practice the templates."],
        "interview_takeaways": ["Recognize the pattern", "Analyze complexity", "Discuss tradeoffs"],
        "common_mistakes": ["Off by one errors", "Forgetting base cases", "Ignoring edge cases"],
        "sources": sources,
        "content_hash": f"fixture-dsa-{slug}-v1",
        "generated_at": "2026-09-23T00:00:00Z"
    }
    
    for i, sec_slug in enumerate(t["sections"]):
        markdown_content = f"This section covers {sec_slug} in detail. "
        if i == 0:
            markdown_content += "\n\nKeywords to know: " + ", ".join(t["keywords"]) + ". "
        
        while len(markdown_content) < 150:
            markdown_content += " Exploring this concept is crucial for mastering Data Structures and Algorithms in technical interviews. It provides a solid foundation for more complex patterns. "

        lesson["sections"].append({
            "slug": sec_slug,
            "title": sec_slug.replace('-', ' ').title(),
            "order_index": i,
            "estimated_minutes": 5,
            "learning_objective": f"Understand {sec_slug} deeply.",
            "markdown": markdown_content,
            "examples": [
                {"language": "python", "code": "print('hello world')", "expected_output": "hello world\n", "explanation": "Basic example for context."}
            ],
            "key_points": [f"Key point about {sec_slug}."]
        })
        
    with open(os.path.join(topic_dir, "lesson.json"), "w", encoding='utf-8') as f:
        json.dump(lesson, f, indent=2)
        
    # Generate exercises.json
    exercises = []
    for i in range(1, 9):
        ex_type = "multiple_choice" if i % 2 == 1 else "short_answer"
        ex = {
            "key": f"{t['ex_prefix']}-{i}",
            "exercise_type": ex_type,
            "title": f"Exercise {i} for {slug}",
            "prompt_markdown": f"What is the core idea of {slug} in exercise {i}?",
            "difficulty": "easy" if ex_type == "multiple_choice" else "medium",
            "hints": ["Think about the definition.", "Review the lesson templates."],
            "content": {}
        }
        if ex_type == "multiple_choice":
            ex["content"] = {
                "choices": ["Option A", "Option B", "Option C", "Option D"],
                "correct_index": 1,
                "explanation": "Option B is correct based on the lesson."
            }
        else:
            ex["content"] = {
                "rubric": ["Mention time complexity", "Mention space complexity"],
                "reference_answer": f"The answer is related to {slug} principles.",
                "minimum_pass_score": 70
            }
        exercises.append(ex)
        
    with open(os.path.join(topic_dir, "exercises.json"), "w", encoding='utf-8') as f:
        json.dump(exercises, f, indent=2)
