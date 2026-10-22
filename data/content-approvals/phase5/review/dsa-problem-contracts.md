# Human review packet: dsa-problem-contracts

UNPUBLISHED. Agent-authored material. No human approval is present. The checked references are factual references; no publisher text or illustrations are redistributed.

Review the exact JSON and validation reports. If any candidate changes, validation/review digests must be regenerated; an old approval cannot cover new bytes.

## lesson

Candidate: `candidates\dsa-problem-contracts.lesson.json`
Candidate SHA-256: `430fbb6ee59f5780bc4cca84d17f938f91eb54348126bf699314215ceb885e48`
Validation: `validation\dsa-problem-contracts.lesson.validation.json`

Provenance and factual references:
```json
{
  "origin": "original",
  "author": "Forge coding agent \u2014 draft author, not a human reviewer",
  "sources": [
    {
      "source_id": "mit-algorithms",
      "url": "https://ocw.mit.edu/courses/6-006-introduction-to-algorithms-spring-2020/pages/lecture-notes/",
      "usage": "factual_reference",
      "status": "resolved",
      "upstream_revision": null,
      "notice": "Original Forge prose and questions; no source text/images redistributed. Human factual/coverage review pending."
    }
  ]
}
```

### Goal and intuition

Before choosing an algorithm, agree on what counts as a correct answer. A contract states inputs, outputs, bounds and awkward cases. A trace then follows one small input through the proposed steps. This prevents solving the wrong task quickly. No prior sorting or graph knowledge is needed: our first examples use integer arithmetic and a fully provided function wrapper.

### A worked example and why it works

Define the distance between integer positions a and b as a nonnegative integer. For positions 3 and 8, subtracting gives -5; taking its absolute value gives 5. Reversing the positions still gives 5. Equal positions give 0. In Python, abs(x) returns the magnitude of x, so `return abs(a - b)` matches the contract. Simply returning a - b fails when a is smaller. The work and extra storage are constant for the bounded integers used here; passing these cases is not a proof about arbitrary huge-integer cost.

### Guided practice, independent practice and revision

Guided: trace a=9, b=4: difference 5, magnitude 5, return integer 5. Independent: state the contract for remaining capacity when used may exceed capacity.

<details><summary>Contract and checked examples</summary>Inputs are two nonnegative integers. Return max(0, capacity - used), never a negative capacity. For capacity 8 and used 3 return 5; for used 11 return 0. Python max(0, difference) chooses the larger value. The exact signature and bounds must be written before submission.</details>

Revision: read the return type, list valid input ranges, trace normal/equal/boundary cases, and construct a counterexample to a tempting wrong method. Hidden tests supplement a clear contract; they cannot rescue an ambiguous statement. Do not print or return a string when an integer is requested.

## assessment

Candidate: `candidates\dsa-problem-contracts.assessment.json`
Candidate SHA-256: `5244d52c09bb4409c8bf366cae0c2124262057aeba1b7539e8b7469b765f9f65`
Validation: `validation\dsa-problem-contracts.assessment.validation.json`

Provenance and factual references:
```json
{
  "origin": "original",
  "author": "Forge coding agent \u2014 draft author, not a human reviewer",
  "sources": [
    {
      "source_id": "mit-algorithms",
      "url": "https://ocw.mit.edu/courses/6-006-introduction-to-algorithms-spring-2020/pages/lecture-notes/",
      "usage": "factual_reference",
      "status": "resolved",
      "upstream_revision": null,
      "notice": "Original Forge prose and questions; no source text/images redistributed. Human factual/coverage review pending."
    }
  ]
}
```

### guided-distance (practice)

Return the nonnegative integer distance between positions a and b, each between -1000 and 1000. Keep solve(a, b). Equal positions have distance 0.

Subtract the positions and take the absolute value.

Exact scoring contract / worked solution / fixtures:
```json
{
  "mode": "function",
  "function_name": "solve",
  "parameters": [
    "a",
    "b"
  ],
  "starter_code": "def solve(a, b):\n    # Replace pass with your return expression.\n    pass",
  "reference_solution": "def solve(a, b):\n    return abs(a - b)",
  "tests": [
    {
      "name": "case-0",
      "args": [
        3,
        8
      ],
      "expected": 5
    },
    {
      "name": "case-1",
      "args": [
        8,
        3
      ],
      "expected": 5
    },
    {
      "name": "case-2",
      "args": [
        4,
        4
      ],
      "expected": 0
    },
    {
      "name": "case-3",
      "args": [
        -3,
        2
      ],
      "expected": 5
    }
  ],
  "sample_tests": [
    {
      "name": "public",
      "args": [
        3,
        8
      ],
      "expected": 5
    }
  ],
  "negative_solutions": [
    "def solve(a, b):\n    return 0"
  ]
}
```

### independent-inclusive (practice)

For integers start <= end between -100 and 100, return how many integer positions are in the inclusive interval [start, end]. Keep solve(start, end).

The difference counts gaps; add one to count both endpoints.

Exact scoring contract / worked solution / fixtures:
```json
{
  "mode": "function",
  "function_name": "solve",
  "parameters": [
    "start",
    "end"
  ],
  "starter_code": "def solve(start, end):\n    # Replace pass with your return expression.\n    pass",
  "reference_solution": "def solve(start, end):\n    return end - start + 1",
  "tests": [
    {
      "name": "case-0",
      "args": [
        2,
        4
      ],
      "expected": 3
    },
    {
      "name": "case-1",
      "args": [
        0,
        0
      ],
      "expected": 1
    },
    {
      "name": "case-2",
      "args": [
        -2,
        1
      ],
      "expected": 4
    }
  ],
  "sample_tests": [
    {
      "name": "public",
      "args": [
        2,
        4
      ],
      "expected": 3
    }
  ],
  "negative_solutions": [
    "def solve(start, end):\n    return 0"
  ]
}
```

### transfer-ring (transfer)

Twelve positions labeled 0 through 11 form a ring. One step moves to either adjacent position, with 0 adjacent to 11. Return the fewest steps from a to b, where both inputs are integer labels. Keep solve(a, b).

Compare the direct distance with the complementary path around the twelve-position ring.

Exact scoring contract / worked solution / fixtures:
```json
{
  "mode": "function",
  "function_name": "solve",
  "parameters": [
    "a",
    "b"
  ],
  "starter_code": "def solve(a, b):\n    pass",
  "reference_solution": "def solve(a, b):\n    return min(abs(a-b), 12-abs(a-b))",
  "tests": [
    {
      "name": "case-0",
      "args": [
        1,
        11
      ],
      "expected": 2
    },
    {
      "name": "case-1",
      "args": [
        0,
        11
      ],
      "expected": 1
    },
    {
      "name": "case-2",
      "args": [
        0,
        6
      ],
      "expected": 6
    },
    {
      "name": "case-3",
      "args": [
        4,
        4
      ],
      "expected": 0
    },
    {
      "name": "case-4",
      "args": [
        10,
        2
      ],
      "expected": 4
    }
  ],
  "sample_tests": [
    {
      "name": "public",
      "args": [
        1,
        11
      ],
      "expected": 2
    }
  ],
  "negative_solutions": [
    "def solve(a, b):\n    return abs(a-b)",
    "def solve(a, b):\n    return 0"
  ]
}
```

### recall-distance (recall)

Return the nonnegative integer distance between integer positions a and b in [-1000,1000].

Absolute difference handles either order and equal positions.

Exact scoring contract / worked solution / fixtures:
```json
{
  "mode": "function",
  "function_name": "solve",
  "parameters": [
    "a",
    "b"
  ],
  "starter_code": "def solve(a, b):\n    # Replace pass with your return expression.\n    pass",
  "reference_solution": "def solve(a, b):\n    return abs(a-b)",
  "tests": [
    {
      "name": "case-0",
      "args": [
        -4,
        -1
      ],
      "expected": 3
    },
    {
      "name": "case-1",
      "args": [
        7,
        2
      ],
      "expected": 5
    },
    {
      "name": "case-2",
      "args": [
        0,
        0
      ],
      "expected": 0
    }
  ],
  "sample_tests": [
    {
      "name": "public",
      "args": [
        -4,
        -1
      ],
      "expected": 3
    }
  ],
  "negative_solutions": [
    "def solve(a, b):\n    return 0"
  ]
}
```

### mock-contract (interview)

A function promises a list of two integers. Which result satisfies that return-type contract?

The first is a list; the second is a tuple even though its elements match.

Exact scoring contract / worked solution / fixtures:
```json
{
  "choices": {
    "a": "(2, 5)",
    "b": "[2, 5]"
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
