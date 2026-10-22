# Independent audit correction: python-exceptions-1.2.0

**NOT HUMAN REVIEWED. UNPUBLISHED. No reviewer identity or attestation has been invented.**

Candidate: `data/content-approvals/independent-audit/candidates/python-exceptions-1.2.0.json`
Validation: `data/content-approvals/independent-audit/validation/python-exceptions-1.2.0.json`
Exact candidate digest: `7ba3d83f4a8ca13851c5855c700592d5c70a6ab9bfc67712180895dac45bef00`

Focused factual correction only; inherited examples/exercises still need complete environment, pedagogy and semantic review. Not a completed course replacement.

## Validation limits

structural/context only; example setup/semantic review unresolved

A structural pass or contextual-example declaration is not factual, pedagogical or independent human approval. Complete missing setup/semantic review before approving.

## Sources

- The Python Tutorial — Errors and Exceptions: https://docs.python.org/3/tutorial/errors.html
- Python Standard Library — Built-in Exceptions: https://docs.python.org/3/library/exceptions.html

## Worked answers and review tasks

### exc-mcq-bare-except

Why is using a bare `except:` clause considered dangerous in production Python code?

Worked answer/explanation: A bare except: catches BaseException, which includes KeyboardInterrupt and SystemExit. This prevents developers from stopping the program with Ctrl+C and prevents container orchestrators from terminating the process cleanly.

Correct authored choice: 1 — It catches KeyboardInterrupt and SystemExit, preventing graceful shutdown or process termination

### exc-mcq-else-clause

Under what condition does the `else` block of a `try...except...else...finally` statement execute?

Worked answer/explanation: The else block in a try statement runs if and only if the code in the try block executed without raising any exception.

Correct authored choice: 1 — Only if the try block ran to completion without raising any exception

### exc-mcq-chaining

How do you re-raise a new exception while explicitly recording the original exception as its cause in Python 3?

Worked answer/explanation: The syntax `raise NewException(...) from original_exc` links the original exception as `__cause__`, providing an unbroken traceback for debugging.

Correct authored choice: 1 — raise NewException() from original_exc

### exc-short-predict-finally-override

Predict the printed output of this function and explain how the `finally` block interacts with return values:

```python
def compute() -> int:
    try:
        return 10
    finally:
        return 20

print(compute())
```

Worked answer/explanation: Output: `20`.
Explanation: The try block prepares to return 10, but the finally block executes unconditionally before the function exits. Because the finally block executes `return 20`, it overrides and discards the pending return value from the try block. Returning from inside a finally block is an anti-pattern because it masks returns and suppressed exceptions.

### exc-short-fix-swallowed-error

A database repository contains this method. When a query fails due to a connection drop, the function returns `None` and masks the failure, causing data corruption downstream. Diagnose the defect and write the corrected method.

```python
def get_user_profile(user_id: int):
    try:
        return db.query('SELECT * FROM users WHERE id = :id', id=user_id)
    except Exception as e:
        print(f'Error: {e}')
        return None
```

Worked answer/explanation: Defect: Catching broad `Exception` and returning `None` conflates 'user not found' with fatal database outages, swallowing stack traces and leading to silent corruption.
Corrected implementation:
```python
class DatabaseError(Exception):
    """Raised on database query failure."""

def get_user_profile(user_id: int):
    try:
        return db.query('SELECT * FROM users WHERE id = :id', id=user_id)
    except Exception as exc:
        # Preserve stack trace and propagate to error boundary
        raise DatabaseError(f'Failed fetching user {user_id}') from exc
```

### exc-short-implement-custom-hierarchy

Design an object-oriented domain exception hierarchy for an API client. Create a base `ApiClientError` and two specialized subclasses: `RateLimitError` (storing `retry_after_seconds: int`) and `NotFoundError` (storing `resource: str`). Show their class definitions.

Worked answer/explanation: ```python
class ApiClientError(Exception):
    """Base exception for API client operations."""

class RateLimitError(ApiClientError):
    def __init__(self, retry_after_seconds: int):
        super().__init__(f'Rate limit exceeded. Retry in {retry_after_seconds}s')
        self.retry_after_seconds = retry_after_seconds

class NotFoundError(ApiClientError):
    def __init__(self, resource: str):
        super().__init__(f'Requested resource not found: {resource}')
        self.resource = resource
```

### exc-short-explain-boundaries

In microservice architectures, where should error boundaries be placed? Explain the responsibilities of an error boundary when an unhandled exception reaches an API endpoint handler.

Worked answer/explanation: Error boundaries belong at system perimeters: HTTP middleware, event queue consumer loops, and scheduled job runners. When an unhandled exception bubbles up to the boundary, its responsibilities are:
1. Rollback open database transactions and release shared locks.
2. Log the full diagnostic stack trace securely using `logger.exception()` for debugging.
3. Record monitoring metrics/alerts (e.g. increment 500 error counter).
4. Return a sanitized, structured response (e.g. JSON `{'error': 'Internal server error', 'request_id': '...'}`) without leaking sensitive internal file paths or stack traces to end users.

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
