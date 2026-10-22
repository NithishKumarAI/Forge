# Independent audit correction: python-type-hints-1.2.0

**NOT HUMAN REVIEWED. UNPUBLISHED. No reviewer identity or attestation has been invented.**

Candidate: `data/content-approvals/independent-audit/candidates/python-type-hints-1.2.0.json`
Validation: `data/content-approvals/independent-audit/validation/python-type-hints-1.2.0.json`
Exact candidate digest: `970b4bfefc1d0ac82619cc78df26e3b8512be91eda48261de665b79dbd1fd33b`

Focused factual correction only; inherited examples/exercises still need complete environment, pedagogy and semantic review. Not a completed course replacement.

## Validation limits

structural/context only; example setup/semantic review unresolved

A structural pass or contextual-example declaration is not factual, pedagogical or independent human approval. Complete missing setup/semantic review before approving.

## Sources

- Python Standard Library — typing Support for type hints: https://docs.python.org/3/library/typing.html
- PEP 585 — Type Hinting Generics In Standard Collections: https://peps.python.org/pep-0585/

## Worked answers and review tasks

### th-mcq-builtin-generics

In modern Python (3.9+), what is the idiomatic way to type hint a function parameter as a dictionary mapping strings to lists of integers?

Worked answer/explanation: PEP 585 enabled standard built-in collections `dict` and `list` to act as generic type hints directly using square brackets: `dict[str, list[int]]`.

Correct authored choice: 0 — dict[str, list[int]]

### th-mcq-runtime-behavior

What happens at runtime if you execute `val: int = 'hello world'` in standard CPython without third-party libraries?

Worked answer/explanation: Type annotations in Python are pure metadata stored in `__annotations__`. CPython does not enforce them at runtime; assigning a string to `val: int` succeeds without error.

Correct authored choice: 1 — CPython successfully assigns the string to val without any error

### th-mcq-any-vs-object

What is the key difference between `typing.Any` and `object` in static type checking?

Worked answer/explanation: `Any` acts as a dynamic escape hatch that allows any attribute access or call without checking. `object` is the safe root of the hierarchy; static checkers forbid calling arbitrary methods on it without narrowing via `isinstance()`.

Correct authored choice: 1 — `Any` turns off type checking allowing any operation, while `object` requires narrowing before accessing attributes

### th-short-predict-callable

Write the complete type annotation for the parameter `validator` in this function signature:

```python
def validate_payload(data: dict[str, str], validator: ???) -> bool:
    return validator(data['email'], len(data['password']))
```

Worked answer/explanation: The type annotation is `Callable[[str, int], bool]`. Full signature:
```python
from collections.abc import Callable
def validate_payload(data: dict[str, str], validator: Callable[[str, int], bool]) -> bool:
    return validator(data['email'], len(data['password']))
```

### th-short-fix-none-dereference

A static checker flags an error on line 4: `Item "None" of "User | None" has no attribute "email"`. Diagnose why the checker flags this and write the corrected code.

```python
def notify_user(user_id: int, user_repo: dict[int, User]) -> None:
    user: User | None = user_repo.get(user_id)
    send_email(user.email, 'Welcome!')
```

Worked answer/explanation: Defect: `user_repo.get()` returns `None` if the ID is missing. Directly accessing `user.email` risks `AttributeError: 'NoneType' object has no attribute 'email'`. The static checker enforces checking for None.
Corrected implementation:
```python
def notify_user(user_id: int, user_repo: dict[int, User]) -> None:
    user: User | None = user_repo.get(user_id)
    if user is None:
        raise ValueError(f'User {user_id} not found')
    send_email(user.email, 'Welcome!')
```

### th-short-implement-protocol

Implement a `Serializable` Protocol using `typing.Protocol` requiring a method `to_dict() -> dict[str, str]`. Then write a function `dump_json(obj: Serializable) -> str` that calls it.

Worked answer/explanation: ```python
import json
from typing import Protocol

class Serializable(Protocol):
    def to_dict(self) -> dict[str, str]:
        ...

def dump_json(obj: Serializable) -> str:
    return json.dumps(obj.to_dict())
```
This enables any class implementing `.to_dict()` to be accepted by `dump_json` without nominal inheritance.

### th-short-explain-runtime-limits

Explain to an interviewer why static typing alone cannot replace runtime validation (like Pydantic or Marshmallow) at web API boundaries.

Worked answer/explanation: Static type checking (via mypy/pyright) operates purely at build/lint time on Python source code, verifying developer logic assumptions. In contrast, external HTTP requests arrive over the network as raw JSON or strings at runtime from untrusted clients. Because Python does not execute static checks on incoming network payloads, runtime parsing and validation libraries (like Pydantic) are mandatory to inspect types, validate constraints, and reject malformed data before internal business logic runs.

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
