# Human review packet: sql-postgresql-tables-keys

UNPUBLISHED. Agent-authored material. No human approval is present. The checked references are factual references; no publisher text or illustrations are redistributed.

Review the exact JSON and validation reports. If any candidate changes, validation/review digests must be regenerated; an old approval cannot cover new bytes.

## lesson

Candidate: `candidates\sql-postgresql-tables-keys.lesson.json`
Candidate SHA-256: `e64a8cd92b7dc7180b7145d9fdd14162592a79e9dafc7422ce3f9b2b95cc98be`
Validation: `validation\sql-postgresql-tables-keys.lesson.validation.json`

Provenance and factual references:
```json
{
  "origin": "original",
  "author": "Forge coding agent \u2014 draft author, not a human reviewer",
  "sources": [
    {
      "source_id": "postgresql-tables",
      "url": "https://www.postgresql.org/docs/18/ddl-constraints.html",
      "usage": "factual_reference",
      "status": "resolved",
      "upstream_revision": null,
      "notice": "Original Forge prose and questions; no source text/images redistributed. Human factual/coverage review pending."
    }
  ]
}
```

### Goal and intuition

A relational table records one kind of thing in rows; named columns describe it. A primary key identifies a row uniquely and cannot be NULL. A foreign key constrains references to another table: it is not automatically unique. A nullable foreign key may be NULL; NOT NULL is a separate requirement. Think of each library member having one member number, while many loan rows can refer to that number.

### A worked example and why it works

Suppose members has primary key id with rows 2 and 8. Loans has its own primary key id and a nullable member_id referencing members(id). Two loans may both refer to member 2. A loan with member_id 99 is invalid because no member 99 exists. A NULL member_id is allowed unless NOT NULL is added. To inspect existing identifiers, `SELECT id FROM members ORDER BY id` returns 2 then 8. ORDER BY is needed when order matters; storage order is not a result guarantee.

### Guided practice, independent practice and revision

Guided: distinguish members.id, which identifies a member, from loans.member_id, which refers to one. To find loans without an assigned member use `WHERE member_id IS NULL`; `= NULL` is not that test. Independent: can members with IDs 2 and 8 share the same display name?

<details><summary>Reasoning</summary>Yes, if only id is the primary key and name has no uniqueness constraint. A display name is not necessarily an identifier. Conversely, inserting id 2 twice violates the primary key.</details>

Revision: state what each row represents, find its primary key, describe each reference, consider nullable fields, and state result ordering. Forge Run/Submit use disposable PGlite databases. Learner SQL never runs against Forge history. The coding items inspect supplied schemas; they do not claim to assess unrestricted database administration or live application migrations.

## assessment

Candidate: `candidates\sql-postgresql-tables-keys.assessment.json`
Candidate SHA-256: `67e9ed9cf183e53875f15b3428fb2e58f56818558e0dfc0b7cd1ec297c0bff68`
Validation: `validation\sql-postgresql-tables-keys.assessment.validation.json`

Provenance and factual references:
```json
{
  "origin": "original",
  "author": "Forge coding agent \u2014 draft author, not a human reviewer",
  "sources": [
    {
      "source_id": "postgresql-tables",
      "url": "https://www.postgresql.org/docs/18/ddl-constraints.html",
      "usage": "factual_reference",
      "status": "resolved",
      "upstream_revision": null,
      "notice": "Original Forge prose and questions; no source text/images redistributed. Human factual/coverage review pending."
    }
  ]
}
```

### guided-identifiers (practice)

Return every members.id from the supplied members table in increasing id order. The primary key is id; include no other column.

Select the primary-key column from members and order by id; do not hard-code the visible values.

Exact scoring contract / worked solution / fixtures:
```json
{
  "columns": [
    "id"
  ],
  "ordered": true,
  "starter_code": "SELECT ",
  "reference_solution": "SELECT id FROM members ORDER BY id",
  "public_dataset": {
    "setup_sql": "CREATE TABLE members(id int PRIMARY KEY); INSERT INTO members VALUES (2),(8); CREATE TABLE loans(id int PRIMARY KEY,member_id int REFERENCES members(id)); INSERT INTO loans VALUES (4,2),(7,NULL),(9,2);"
  },
  "datasets": [
    {
      "setup_sql": "CREATE TABLE members(id int PRIMARY KEY); INSERT INTO members VALUES (2),(8); CREATE TABLE loans(id int PRIMARY KEY,member_id int REFERENCES members(id)); INSERT INTO loans VALUES (4,2),(7,NULL),(9,2);",
      "expected_rows": [
        [
          2
        ],
        [
          8
        ]
      ]
    },
    {
      "setup_sql": "CREATE TABLE members(id int PRIMARY KEY); INSERT INTO members VALUES (3),(10),(14); CREATE TABLE loans(id int PRIMARY KEY,member_id int REFERENCES members(id)); INSERT INTO loans VALUES (1,NULL),(5,10),(8,NULL);",
      "expected_rows": [
        [
          3
        ],
        [
          10
        ],
        [
          14
        ]
      ]
    },
    {
      "setup_sql": "CREATE TABLE members(id int PRIMARY KEY); CREATE TABLE loans(id int PRIMARY KEY,member_id int REFERENCES members(id));",
      "expected_rows": []
    }
  ],
  "negative_solutions": [
    "SELECT 2 AS id"
  ]
}
```

### independent-foreign-key (practice)

Two loan rows reference the same existing members.id. There is no UNIQUE constraint on loans.member_id. Is this permitted by that foreign key?

Several loans can reference one member unless another constraint forbids it.

Exact scoring contract / worked solution / fixtures:
```json
{
  "choices": {
    "a": "No, every foreign-key value must occur only once.",
    "b": "Yes, the reference alone does not require uniqueness."
  },
  "correct": [
    "b"
  ]
}
```

### transfer-unassigned (transfer)

Loans has its own id and a nullable member_id referencing members(id). Return the IDs of loans that have no assigned member, in increasing loan id order. Do not return member identifiers.

Inspect the specified key column; use IS NULL for an unassigned optional reference and ORDER BY for deterministic order.

Exact scoring contract / worked solution / fixtures:
```json
{
  "columns": [
    "id"
  ],
  "ordered": true,
  "starter_code": "SELECT ",
  "reference_solution": "SELECT id FROM loans WHERE member_id IS NULL ORDER BY id",
  "public_dataset": {
    "setup_sql": "CREATE TABLE members(id int PRIMARY KEY); INSERT INTO members VALUES (2),(8); CREATE TABLE loans(id int PRIMARY KEY,member_id int REFERENCES members(id)); INSERT INTO loans VALUES (4,2),(7,NULL),(9,2);"
  },
  "datasets": [
    {
      "setup_sql": "CREATE TABLE members(id int PRIMARY KEY); INSERT INTO members VALUES (2),(8); CREATE TABLE loans(id int PRIMARY KEY,member_id int REFERENCES members(id)); INSERT INTO loans VALUES (4,2),(7,NULL),(9,2);",
      "expected_rows": [
        [
          7
        ]
      ]
    },
    {
      "setup_sql": "CREATE TABLE members(id int PRIMARY KEY); INSERT INTO members VALUES (3),(10),(14); CREATE TABLE loans(id int PRIMARY KEY,member_id int REFERENCES members(id)); INSERT INTO loans VALUES (1,NULL),(5,10),(8,NULL);",
      "expected_rows": [
        [
          1
        ],
        [
          8
        ]
      ]
    },
    {
      "setup_sql": "CREATE TABLE members(id int PRIMARY KEY); CREATE TABLE loans(id int PRIMARY KEY,member_id int REFERENCES members(id));",
      "expected_rows": []
    }
  ],
  "negative_solutions": [
    "SELECT 2 AS id"
  ]
}
```

### recall-keys (recall)

List all primary-key IDs in members in increasing order, including all rows and no extra columns.

Select the primary-key column from members and order by id; do not hard-code the visible values.

Exact scoring contract / worked solution / fixtures:
```json
{
  "columns": [
    "id"
  ],
  "ordered": true,
  "starter_code": "SELECT ",
  "reference_solution": "SELECT id FROM members ORDER BY id",
  "public_dataset": {
    "setup_sql": "CREATE TABLE members(id int PRIMARY KEY); INSERT INTO members VALUES (2),(8); CREATE TABLE loans(id int PRIMARY KEY,member_id int REFERENCES members(id)); INSERT INTO loans VALUES (4,2),(7,NULL),(9,2);"
  },
  "datasets": [
    {
      "setup_sql": "CREATE TABLE members(id int PRIMARY KEY); INSERT INTO members VALUES (2),(8); CREATE TABLE loans(id int PRIMARY KEY,member_id int REFERENCES members(id)); INSERT INTO loans VALUES (4,2),(7,NULL),(9,2);",
      "expected_rows": [
        [
          2
        ],
        [
          8
        ]
      ]
    },
    {
      "setup_sql": "CREATE TABLE members(id int PRIMARY KEY); INSERT INTO members VALUES (3),(10),(14); CREATE TABLE loans(id int PRIMARY KEY,member_id int REFERENCES members(id)); INSERT INTO loans VALUES (1,NULL),(5,10),(8,NULL);",
      "expected_rows": [
        [
          3
        ],
        [
          10
        ],
        [
          14
        ]
      ]
    },
    {
      "setup_sql": "CREATE TABLE members(id int PRIMARY KEY); CREATE TABLE loans(id int PRIMARY KEY,member_id int REFERENCES members(id));",
      "expected_rows": []
    }
  ],
  "negative_solutions": [
    "SELECT 2 AS id"
  ]
}
```

### mock-primary (interview)

Which condition is guaranteed by a declared primary key?

Primary keys need not be consecutive or positive; uniqueness and non-nullness are required.

Exact scoring contract / worked solution / fixtures:
```json
{
  "choices": {
    "a": "Its value is always a consecutive positive integer.",
    "b": "Its value identifies each row uniquely and is not NULL."
  },
  "correct": [
    "b"
  ]
}
```

## Known uncertainties and reviewer decisions

- Proposed coverage is an author claim, not a completed human review. Check every learning outcome against teaching and independent evidence.
- Verify source relevance, original expression, factual accuracy, beginner sequencing and legitimate alternative answers.
- Verify transfer families require actual independent application rather than a superficial rewording. Revise/reject if inadequate; never approve by count.
- Confirm the restricted Python subset/PGlite contracts assess the intended competency. Reflection must stay unscored.
- No title-based historical mapping is authorized. Remaining Level 1–3 topics are not covered by this packet.

## Reviewer checklist (all unchecked)

- [ ] objective
- [ ] accurate explanation
- [ ] terminology
- [ ] worked example
- [ ] reasoning steps
- [ ] common mistakes
- [ ] progressive practice
- [ ] worked answers
- [ ] progressive hints
- [ ] revision summary
- [ ] provenance
- [ ] independent technical review
- [ ] semantic answers
- [ ] coverage
- [ ] statement judge agreement

## Authorized human actions

1. Read both exact candidates, all worked answers/fixtures, validation reports and references. Edit/revalidate if any check is unsatisfied.
2. Copy `review-checklist.template.json`; only personally completed checks may become true. Use the existing `scripts.content_checks.publish review` command with your actual name and `--i-am-the-human-reviewer`, separately for each candidate.
3. Explicitly review/confirm the Placement Foundations graph in Forge (confirmation does not approve content). Export its actual curriculum ID and graph digest for release targets. No graph or reviewer identity is guessed here.
4. Use `scripts.content_checks.publish package` for each reviewed candidate/target and combine entries into one canonical complete overlay. Run the existing publish CLI only after checking the exact package and destination DB. Preserve previous approved entries when constructing an overlay.
See `data/content-approvals/README.md` for exact CLI arguments and backup/restore safeguards. No review or publication command was run by this agent.
