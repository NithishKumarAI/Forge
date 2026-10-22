# Human review packet: python-values-expressions

UNPUBLISHED. Agent-authored material. No human approval is present. The checked references are factual references; no publisher text or illustrations are redistributed.

Review the exact JSON and validation reports. If any candidate changes, validation/review digests must be regenerated; an old approval cannot cover new bytes.

## lesson

Candidate: `candidates\python-values-expressions.lesson.json`
Candidate SHA-256: `ccebb5c1622db89e642ae328e4d4fc9245adb25c28b2245d939e17ecd3763d0d`
Validation: `validation\python-values-expressions.lesson.validation.json`

Provenance and factual references:
```json
{
  "origin": "original",
  "author": "Forge coding agent \u2014 draft author, not a human reviewer",
  "sources": [
    {
      "source_id": "python-tutorial",
      "url": "https://docs.python.org/3.12/tutorial/introduction.html",
      "usage": "factual_reference",
      "status": "resolved",
      "upstream_revision": null,
      "notice": "Original Forge prose and questions; no source text/images redistributed. Human factual/coverage review pending."
    }
  ]
}
```

### Goal and intuition

Python keeps values such as whole numbers and text. An expression computes a value; assignment gives that value a name. Quotes matter: 6 is an integer, while '6' is text. A name is a label, not a box that permanently remembers an earlier calculation. This lesson uses integers, strings and basic arithmetic only; external packages, files and network access are outside Forge's restricted Submit worker.

### A worked example and why it works

Trace `count = 3`, then `total = count * 4`, then `count = 5`. Total remains 12: assignment evaluated the expression when count was 3. It is not a live spreadsheet formula. Python uses * for multiplication; brackets group operations. The expression `2 + 3 * 4` is 14. The expression `'2' + '3'` joins text into '23', rather than adding numbers. Division / produces a floating-point value; // is floor division. Keep these operations distinct.

### Guided practice, independent practice and revision

Guided: after `price = 7` and `cost = price + 2`, cost is 9. Independent: compute a total with a fixed fee of 3 plus two times an integer value. For value 4, the result is 11.

<details><summary>Code and explanation</summary>`def solve(value):` names the small function the judge calls; its indented `return 3 + 2 * value` sends the answer back. Return the number, not its printed representation. For value 0, the fee remains 3. The provided function wrapper is only a test interface; complete function design is taught later.</details>

Revision: note types, trace one assignment at a time, use grouping intentionally, preserve the provided function parameters, and test zero and negative inputs when allowed. Run checks public samples; Submit checks additional fixtures.

## assessment

Candidate: `candidates\python-values-expressions.assessment.json`
Candidate SHA-256: `7b48a06e48baa41ff87a0505cd42021da5f495def74ce45026c1d5935c623199`
Validation: `validation\python-values-expressions.assessment.validation.json`

Provenance and factual references:
```json
{
  "origin": "original",
  "author": "Forge coding agent \u2014 draft author, not a human reviewer",
  "sources": [
    {
      "source_id": "python-tutorial",
      "url": "https://docs.python.org/3.12/tutorial/introduction.html",
      "usage": "factual_reference",
      "status": "resolved",
      "upstream_revision": null,
      "notice": "Original Forge prose and questions; no source text/images redistributed. Human factual/coverage review pending."
    }
  ]
}
```

### guided-fee (practice)

Return the integer 3 + 2 * value for any integer value from -1000 to 1000. Keep solve(value); do not print the answer.

Multiply value by 2 before adding the fixed fee of 3.

Exact scoring contract / worked solution / fixtures:
```json
{
  "mode": "function",
  "function_name": "solve",
  "parameters": [
    "value"
  ],
  "starter_code": "def solve(value):\n    # Replace pass with your return expression.\n    pass",
  "reference_solution": "def solve(value):\n    return 3 + 2 * value",
  "tests": [
    {
      "name": "case-0",
      "args": [
        4
      ],
      "expected": 11
    },
    {
      "name": "case-1",
      "args": [
        0
      ],
      "expected": 3
    },
    {
      "name": "case-2",
      "args": [
        -2
      ],
      "expected": -1
    }
  ],
  "sample_tests": [
    {
      "name": "public",
      "args": [
        4
      ],
      "expected": 11
    }
  ],
  "negative_solutions": [
    "def solve(value):\n    return 0"
  ]
}
```

### independent-square (practice)

Return value * value + 1 for an integer value between -100 and 100. Keep the provided solve(value) signature.

The product is computed first. A negative multiplied by itself is nonnegative.

Exact scoring contract / worked solution / fixtures:
```json
{
  "mode": "function",
  "function_name": "solve",
  "parameters": [
    "value"
  ],
  "starter_code": "def solve(value):\n    # Replace pass with your return expression.\n    pass",
  "reference_solution": "def solve(value):\n    return value * value + 1",
  "tests": [
    {
      "name": "case-0",
      "args": [
        3
      ],
      "expected": 10
    },
    {
      "name": "case-1",
      "args": [
        0
      ],
      "expected": 1
    },
    {
      "name": "case-2",
      "args": [
        -4
      ],
      "expected": 17
    }
  ],
  "sample_tests": [
    {
      "name": "public",
      "args": [
        3
      ],
      "expected": 10
    }
  ],
  "negative_solutions": [
    "def solve(value):\n    return 0"
  ]
}
```

### transfer-conversion (transfer)

A sensor reports an integer value in whole minutes, between 0 and 1000. A test event occurs 15 seconds after that many minutes. Return its time in seconds from the origin.

Each minute contributes 60 seconds; add the one-time 15-second offset after conversion.

Exact scoring contract / worked solution / fixtures:
```json
{
  "mode": "function",
  "function_name": "solve",
  "parameters": [
    "value"
  ],
  "starter_code": "def solve(value):\n    # Replace pass with your return expression.\n    pass",
  "reference_solution": "def solve(value):\n    return value * 60 + 15",
  "tests": [
    {
      "name": "case-0",
      "args": [
        2
      ],
      "expected": 135
    },
    {
      "name": "case-1",
      "args": [
        0
      ],
      "expected": 15
    },
    {
      "name": "case-2",
      "args": [
        9
      ],
      "expected": 555
    }
  ],
  "sample_tests": [
    {
      "name": "public",
      "args": [
        2
      ],
      "expected": 135
    }
  ],
  "negative_solutions": [
    "def solve(value):\n    return 0"
  ]
}
```

### recall-evaluation (recall)

Return 10 - 2 * value for an integer between -100 and 100, without converting to text.

Multiplication is performed before subtraction.

Exact scoring contract / worked solution / fixtures:
```json
{
  "mode": "function",
  "function_name": "solve",
  "parameters": [
    "value"
  ],
  "starter_code": "def solve(value):\n    # Replace pass with your return expression.\n    pass",
  "reference_solution": "def solve(value):\n    return 10 - 2 * value",
  "tests": [
    {
      "name": "case-0",
      "args": [
        3
      ],
      "expected": 4
    },
    {
      "name": "case-1",
      "args": [
        0
      ],
      "expected": 10
    },
    {
      "name": "case-2",
      "args": [
        -2
      ],
      "expected": 14
    }
  ],
  "sample_tests": [
    {
      "name": "public",
      "args": [
        3
      ],
      "expected": 4
    }
  ],
  "negative_solutions": [
    "def solve(value):\n    return 0"
  ]
}
```

### mock-types (interview)

What value and type does Python produce for the expression '4' + '5'?

Both operands are strings, so + concatenates them.

Exact scoring contract / worked solution / fixtures:
```json
{
  "choices": {
    "a": "The integer 9",
    "b": "The string '45'"
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
