# Independent audit correction: sql-indexes-1.2.0

**NOT HUMAN REVIEWED. UNPUBLISHED. No reviewer identity or attestation has been invented.**

Candidate: `data/content-approvals/independent-audit/candidates/sql-indexes-1.2.0.json`
Validation: `data/content-approvals/independent-audit/validation/sql-indexes-1.2.0.json`
Exact candidate digest: `3f7c82613d987093d51124a1668bdb2c0d3df3e50589e09d03d21d0b733ebbf0`

Corrects missing seed rows, relname/indexrelname confusion and universal planner/write/heap-fetch claims. Four exact PGlite examples; EXPLAIN plan intentionally requires contextual human review.

## Validation limits

Four exact SQL fixtures executed; one environment-dependent EXPLAIN example remains contextual, not a machine execution certification.

A structural pass or contextual-example declaration is not factual, pedagogical or independent human approval. Complete missing setup/semantic review before approving.

## Sources

- PostgreSQL Documentation — Indexes (B-tree, Multicolumn, EXPLAIN): https://www.postgresql.org/docs/current/indexes.html
- PostgreSQL Indexes Tutorial: https://www.postgresql.org/docs/current/tutorial.html

## Worked answers and review tasks

### index-catalog-name

Which pg_stat_user_indexes column identifies the index name?

Worked answer/explanation: indexrelname names the index; relname names its table.

Correct authored choice: 1 — indexrelname

### index-only-visibility

Does an Index Only Scan always guarantee zero heap fetches?

Worked answer/explanation: Visibility checks may still require heap access when pages are not all-visible.

Correct authored choice: 1 — No

### index-physical-writes

Does adding ten indexes imply exactly eleven physical writes for each insert?

Worked answer/explanation: Logical index maintenance, buffers and WAL do not imply a fixed physical write count.

Correct authored choice: 1 — No

### index-composite-query

For (customer_id,order_date), describe the query pattern that directly uses the leading key and explain the limitation.

Worked answer/explanation: Equality on customer_id followed by a range on order_date matches the ordering. Queries omitting the leading key are not universally impossible; inspect plan and cost for the engine version and data.

### index-fix-catalog

Fix a query that filters relname = 'idx_orders_cust_date' to find that index.

Worked answer/explanation: SELECT indexrelname AS index_name FROM pg_stat_user_indexes WHERE indexrelname = 'idx_orders_cust_date'; relname is the table name.

### index-fixture-rows

A sample creates an empty table and then promises a selected row. What must its fixture add?

Worked answer/explanation: Insert the exact row before querying, or change the expected result to empty. Declare schema, inserted data, query and ordering together; never invent a row in the answer.

### index-explain-report

What should a worked EXPLAIN example promise instead of a fixed cost or runtime?

Worked answer/explanation: Provide complete setup and ask the reader to inspect plan nodes, actual rows and visibility/heap behavior. State engine version and data. Timings and selected plans are observations, not universal expected constants.

## Human checklist

- [ ] objective
- [ ] accurate_explanation
- [ ] terminology
- [ ] worked_example
- [ ] reasoning_steps
- [ ] common_mistakes
- [ ] progressive_practice
- [ ] worked_answers
- [ ] progressive_hints
- [ ] revision_summary
- [ ] provenance
- [ ] independent_technical_review
- [ ] semantic_answers
- [ ] coverage
- [ ] statement_judge_agreement

## Publication boundary

Review the complete candidate, sources, coverage, executable fixtures and all worked answers. Copy the all-false checklist and mark only personally completed checks. Use the existing content_checks.publish review command with your actual identity and explicit human attestation. Package only for an exact confirmed graph/topic after review; preserve existing overlay entries. No review/package/publish operation is performed here.

Changes to candidate bytes require fresh validation and a fresh review. Focused factual patches still inherit broader lesson and exercise issues; do not approve them as complete teaching merely because the corrected paragraph is accurate.
