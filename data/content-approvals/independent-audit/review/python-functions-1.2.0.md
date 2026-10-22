# Independent audit correction: python-functions-1.2.0

**NOT HUMAN REVIEWED. UNPUBLISHED. No reviewer identity or attestation has been invented.**

Candidate: `data/content-approvals/independent-audit/candidates/python-functions-1.2.0.json`
Validation: `data/content-approvals/independent-audit/validation/python-functions-1.2.0.json`
Exact candidate digest: `62288077de0124769174e6b37af48a2d9eb191499fcae8c5813d30b7faea83f5`

Full replacement of generic Functions prompts and worked answers; no scored transfer pool is claimed.

## Validation limits

all six standalone Python examples executed with exact stdout

A structural pass or contextual-example declaration is not factual, pedagogical or independent human approval. Complete missing setup/semantic review before approving.

## Sources

- Defining Functions: https://docs.python.org/3/tutorial/controlflow.html#defining-functions

## Worked answers and review tasks

### functions-return-none

What does result contain after def announce(): print("hi") followed by result = announce()?

Worked answer/explanation: The call prints hi but has no return statement, so result is None.

Correct authored choice: 1 — None

### functions-keyword-binding

For def cost(price, quantity=1): return price * quantity, what is cost(quantity=3, price=4)?

Worked answer/explanation: Keyword names bind price=4 and quantity=3, so multiplication returns 12.

Correct authored choice: 1 — 12

### functions-default-list

For def add(x, items=[]): items.append(x); return items, what does print(add(1)); print(add(2)) display?

Worked answer/explanation: The same default list is reused. The first print happens before the second mutation, so it prints [1], then [1, 2].

Correct authored choice: 1 — [1] then [1, 2]

### functions-trace-scope

Trace: x=10; def double(x): return x*2. Explain double(3) and the outer x afterwards.

Worked answer/explanation: double(3) returns 6. Its local parameter x refers to 3. The outer x remains 10 because the call does not assign to the outer name.

### functions-fix-return

Fix def square(n): print(n*n) so callers can use square(4)+1. State the final value.

Worked answer/explanation: Use def square(n): return n*n. square(4) returns 16, so square(4)+1 is 17. Printing alone returns None, which cannot be added to 1.

### functions-normalize-contract

Implement normalized_scores using the full nonnegative finite-list contract in the worked section. Include empty, zero, negative and no-mutation tests.

Worked answer/explanation: def normalized_scores(scores):
    if any(value < 0 for value in scores):
        raise ValueError("scores must be nonnegative")
    if not scores:
        return []
    maximum = max(scores)
    if maximum == 0:
        return [0 for value in scores]
    return [value / maximum for value in scores]
values = [2, 4]
print(normalized_scores(values))
print(values)
print(normalized_scores([]))
print(normalized_scores([0, 0]))
Expected printed output:
[0.5, 1.0]
[2, 4]
[]
[0, 0]
A call with [-1] must raise ValueError. Finite numbers are an explicit precondition.

### functions-explain-sharing

Explain why items=[] is unsafe when an omitted argument should create a fresh list. Give the repair.

Worked answer/explanation: The default list is constructed once when def executes, then reused. Use items=None and inside the body if items is None: items=[] before appending. Two omitted-argument calls then receive independent lists.

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
