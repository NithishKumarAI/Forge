# Independent audit correction: python-control-flow-1.2.0

**NOT HUMAN REVIEWED. UNPUBLISHED. No reviewer identity or attestation has been invented.**

Candidate: `data/content-approvals/independent-audit/candidates/python-control-flow-1.2.0.json`
Validation: `data/content-approvals/independent-audit/validation/python-control-flow-1.2.0.json`
Exact candidate digest: `987fdd2c145fd1c319ecc87dfceb3d2233592a4d2a294905a2d599f14113d427`

Focused factual correction only; inherited examples/exercises still need complete environment, pedagogy and semantic review. Not a completed course replacement.

## Validation limits

structural/context only; example setup/semantic review unresolved

A structural pass or contextual-example declaration is not factual, pedagogical or independent human approval. Complete missing setup/semantic review before approving.

## Sources

- The Python Tutorial — More Control Flow Tools: https://docs.python.org/3/tutorial/controlflow.html
- Python Language Reference — Compound statements: https://docs.python.org/3/reference/compound_stmts.html

## Worked answers and review tasks

### cf-mcq-truthiness

Which of the following expressions evaluates to True in Python?

Worked answer/explanation: Any non-empty string evaluates to True, including the text 'False'. Empty collections, 0.0, and None are falsy.

Correct authored choice: 2 — bool('False')

### cf-mcq-loop-else

When does the else block of a for loop execute in Python?

Worked answer/explanation: In Python, a loop else block runs only if the loop finishes normally without being terminated by a break statement.

Correct authored choice: 2 — Only if the loop completes all iterations without hitting break

### cf-mcq-short-circuit

What is the evaluated result of the expression `[] or 0 or 'backend' or True`?

Worked answer/explanation: The or operator evaluates left-to-right, discarding falsy operands [] and 0, and returns the first truthy value 'backend' without converting to bool.

Correct authored choice: 1 — 'backend'

### cf-short-predict-trace

Predict the final printed output of this code snippet and trace the values of `x` and `total` through each iteration:

```python
x = 1
total = 0
while x < 10:
    if x % 3 == 0:
        x += 2
        continue
    total += x
    if total > 10:
        break
    x += 2
print(f'{x}:{total}')
```

Worked answer/explanation: Iteration 1: x=1, total becomes 1, x increments to 3. Iteration 2: x=3 (3%3==0), x increments to 5, continue skips addition. Iteration 3: x=5, total becomes 6, x increments to 7. Iteration 4: x=7, total becomes 13 (>10), break fires immediately before x changes. Final output: 7:16.

### cf-short-fix-boundary

A payment service calculates shipping fees using the function below. When an order has `discount_amount = 0`, it incorrectly applies the default discount of 10. Diagnose the root cause and provide the minimal corrected implementation.

```python
def apply_discount(subtotal: float, discount_amount: float | None = None) -> float:
    if not discount_amount:
        discount_amount = 10.0
    return max(0.0, subtotal - discount_amount)
```

Worked answer/explanation: The defect occurs because `not 0` evaluates to True, causing valid 0-dollar discounts to be overwritten by the 10.0 default. Fix: replace `if not discount_amount:` with `if discount_amount is None:`. This explicitly checks whether an argument was provided, preserving 0 as a valid numeric discount.

### cf-short-implement-guard

Refactor the deeply nested function below to use early guard clauses instead of nested if-else blocks. Explain why guard clauses improve code maintainability.

```python
def process_transaction(user, balance, amount):
    if user is not None:
        if user.is_active:
            if balance >= amount:
                return 'approved'
            else:
                return 'insufficient_funds'
        else:
            return 'inactive_user'
    else:
        return 'missing_user'
```

Worked answer/explanation: Refactored implementation:
```python
def process_transaction(user, balance, amount):
    if user is None:
        return 'missing_user'
    if not user.is_active:
        return 'inactive_user'
    if balance < amount:
        return 'insufficient_funds'
    return 'approved'
```
Guard clauses validate failure preconditions up front and return immediately, keeping the primary execution path unnested and making preconditions inspectable.

### cf-short-explain-mutation-trap

Explain why mutating a list while iterating over it with a for loop leads to skipped elements or bugs in Python. Write a small code example showing the bug and the idiomatic resolution.

Worked answer/explanation: Python's for loop maintains an internal index offset into the list. If an item at index 0 is removed, the item formerly at index 1 shifts to index 0. On the next iteration, the loop advances its pointer to index 1, completely skipping the newly shifted element. Example bug: `items = [1, 2, 3]; for x in items: items.remove(x)`. Resolution: either iterate over a shallow copy `for x in items[:]:` or use a list comprehension: `items = [x for x in items if keep(x)]`.

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
