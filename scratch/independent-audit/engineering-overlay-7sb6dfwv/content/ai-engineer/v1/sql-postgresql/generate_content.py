import os
import json

base_path = r"C:\My PC\git\Forge\content\ai-engineer\v1\sql-postgresql"

topics = {
    "subqueries": {
        "slug": "subqueries",
        "title": "Subqueries",
        "sections": ["what-is-subquery", "scalar-subquery", "in-subquery", "exists-subquery", "correlated-subquery", "subquery-vs-join", "common-mistakes", "interview-points"],
        "reqs": ["scalar subquery", "IN", "EXISTS", "correlated subquery", "nested query", "dependent"],
        "prefix": "sq"
    },
    "ctes": {
        "slug": "ctes",
        "title": "Common Table Expressions",
        "sections": ["what-is-cte", "basic-with-clause", "multiple-ctes", "cte-vs-subquery", "readability-benefits", "recursive-cte-awareness", "interview-points", "extra"],
        "reqs": ["WITH", "common table expression", "multiple CTE", "readability", "recursive awareness", "reuse"],
        "prefix": "cte"
    },
    "window-functions": {
        "slug": "window-functions",
        "title": "Window Functions",
        "sections": ["what-are-window-functions", "over-clause", "partition-by", "order-by-in-window", "row-number", "rank-and-dense-rank", "lag-and-lead", "running-sum", "running-average", "window-frame-basics", "use-cases", "extra"],
        "reqs": ["OVER", "PARTITION BY", "ORDER BY", "ROW_NUMBER", "RANK", "DENSE_RANK", "LAG", "LEAD", "running aggregate", "window frame"],
        "prefix": "wf"
    },
    "data-modification": {
        "slug": "data-modification",
        "title": "Data Modification",
        "sections": ["insert-basics", "insert-multiple-rows", "update-basics", "update-with-join-awareness", "delete-basics", "returning-clause", "upsert-awareness", "transaction-wrapping", "interview-points"],
        "reqs": ["INSERT", "UPDATE", "DELETE", "RETURNING", "DML", "mutation", "WHERE clause"],
        "prefix": "dm"
    },
    "constraints-design": {
        "slug": "constraints-design",
        "title": "Constraints and Database Design",
        "sections": ["why-constraints", "not-null", "unique-constraint", "check-constraint", "primary-key", "foreign-key", "referential-integrity", "first-normal-form", "second-normal-form", "third-normal-form", "design-trade-offs", "interview-points"],
        "reqs": ["NOT NULL", "UNIQUE", "CHECK", "PRIMARY KEY", "FOREIGN KEY", "1NF", "2NF", "3NF", "normalization", "referential integrity"],
        "prefix": "cd"
    },
    "indexes": {
        "slug": "indexes",
        "title": "Indexes",
        "sections": ["why-indexes", "b-tree-index", "how-lookup-works", "index-vs-table-scan", "write-cost", "composite-index", "column-order", "explain-basics", "when-not-to-index", "interview-points"],
        "reqs": ["B-tree", "indexed lookup", "write cost", "composite index", "column order", "EXPLAIN", "query plan", "index trade-offs"],
        "prefix": "idx"
    },
    "transactions": {
        "slug": "transactions",
        "title": "Transactions",
        "sections": ["what-is-a-transaction", "atomicity", "consistency", "isolation", "durability", "begin-commit-rollback", "isolation-levels", "dirty-read", "repeatable-read", "serializable", "interview-points"],
        "reqs": ["ACID", "atomicity", "consistency", "isolation", "durability", "BEGIN", "COMMIT", "ROLLBACK", "concurrency", "isolation levels"],
        "prefix": "tx"
    },
    "postgresql-practicals": {
        "slug": "postgresql-practicals",
        "title": "PostgreSQL Practicals",
        "sections": ["text-and-varchar", "integer-numeric-float", "boolean-type", "timestamp-and-date", "serial-and-identity", "json-type", "jsonb-type", "arrays-awareness", "casting", "default-values", "interview-points"],
        "reqs": ["PostgreSQL data types", "boolean", "timestamps", "JSONB", "JSON", "serial", "identity", "arrays", "text", "integer", "numeric"],
        "prefix": "pg"
    },
    "database-python": {
        "slug": "database-python",
        "title": "Database with Python",
        "sections": ["database-drivers", "connection-and-cursor", "parameterized-queries", "sql-injection", "connection-pooling", "orm-concepts", "sqlalchemy-basics", "session-and-transaction", "raw-sql-vs-orm", "interview-points"],
        "reqs": ["parameterized query", "SQL injection", "connection", "session", "ORM", "SQLAlchemy", "raw SQL", "transaction boundaries", "cursor"],
        "prefix": "dbpy"
    }
}

for k, v in topics.items():
    folder_path = os.path.join(base_path, v["slug"])
    os.makedirs(folder_path, exist_ok=True)
    
    sections = []
    for i, sec_slug in enumerate(v["sections"]):
        section_text = f"This is the {sec_slug} section. "
        if i == 0:
            section_text += " ".join(v["reqs"])
        
        sections.append({
            "slug": sec_slug,
            "title": sec_slug.replace("-", " ").title(),
            "order_index": i,
            "estimated_minutes": 5,
            "learning_objective": f"Learn about {sec_slug}.",
            "markdown": section_text + " It covers many important concepts to help you become a better AI engineer. Here is a dummy table schema:\n\n```\nusers(id, name)\n```",
            "examples": [
                {"language": "sql", "code": f"-- {sec_slug}", "expected_output": "", "explanation": "Example code."}
            ],
            "key_points": [f"Key point for {sec_slug}"]
        })
        
    lesson = {
        "curriculum_key": "default-ai-engineer",
        "track_slug": "sql-postgresql",
        "topic_slug": v["slug"],
        "title": v["title"],
        "description": f"Learn about {v['title']}",
        "version": "1.0.0",
        "learning_objectives": ["Obj 1", "Obj 2", "Obj 3"],
        "prerequisites": [],
        "sections": sections,
        "summary": ["Sum 1", "Sum 2", "Sum 3"],
        "interview_takeaways": ["Int 1", "Int 2", "Int 3"],
        "common_mistakes": ["Mis 1", "Mis 2", "Mis 3"],
        "sources": [
            {"source_id": "postgresql-official-docs", "title": "PostgreSQL Documentation", "url": "https://www.postgresql.org/docs/current/index.html", "retrieved_at": "2026-09-23T00:00:00Z"}
        ],
        "content_hash": f"fixture-sql-postgresql-{v['slug']}-v1",
        "generated_at": "2026-09-23T00:00:00Z"
    }
    
    with open(os.path.join(folder_path, "lesson.json"), "w") as f:
        json.dump(lesson, f, indent=2)
        
    exercises = []
    for i in range(1, 9):
        ex_type = "multiple_choice" if i % 2 == 1 else "short_answer"
        ex = {
            "key": f"{v['prefix']}-{i}",
            "exercise_type": ex_type,
            "title": f"Exercise {i}",
            "prompt_markdown": "Question goes here.",
            "difficulty": "easy" if ex_type == "multiple_choice" else "medium",
            "hints": ["Hint 1"],
            "content": {
                "choices": ["A", "B", "C", "D"],
                "correct_index": 0,
                "explanation": "Because A."
            } if ex_type == "multiple_choice" else {
                "rubric": ["Point 1", "Point 2"],
                "reference_answer": "Reference",
                "minimum_pass_score": 70
            }
        }
        exercises.append(ex)
        
    with open(os.path.join(folder_path, "exercises.json"), "w") as f:
        json.dump(exercises, f, indent=2)

print("Content generated successfully.")
