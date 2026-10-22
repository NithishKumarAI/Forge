# Human review packet: quantitative-aptitude-number-operations

UNPUBLISHED. Agent-authored material. No human approval is present. The checked references are factual references; no publisher text or illustrations are redistributed.

Review the exact JSON and validation reports. If any candidate changes, validation/review digests must be regenerated; an old approval cannot cover new bytes.

## lesson

Candidate: `candidates\quantitative-aptitude-number-operations.lesson.json`
Candidate SHA-256: `335ed5e6a12e4b9151ef2ddab942ddeaa216f50ff5153fd15b22e075e6e24117`
Validation: `validation\quantitative-aptitude-number-operations.lesson.validation.json`

Provenance and factual references:
```json
{
  "origin": "original",
  "author": "Forge coding agent \u2014 draft author, not a human reviewer",
  "sources": [
    {
      "source_id": "openstax-arithmetic",
      "url": "https://openstax.org/books/prealgebra-2e/pages/2-1-use-the-language-of-algebra",
      "usage": "factual_reference",
      "status": "resolved",
      "upstream_revision": null,
      "notice": "Original Forge prose and questions; no source text/images redistributed. Human factual/coverage review pending."
    }
  ]
}
```

### Goal and intuition

An expression is an instruction with a shared reading order. A bill for a fixed delivery charge plus several identical items should multiply the item cost first; otherwise the delivery charge would be multiplied too. Brackets make a group explicit. Work inside groups first, then powers, multiplication/division from left to right, then addition/subtraction from left to right. Multiplication does not outrank division; they share a level.

### A worked example and why it works

A stationery order has a ₹4 delivery charge and three ₹2 pencils. The total is 4 + 3 × 2. First the pencils cost 6; then add delivery: 4 + 6 = ₹10. By contrast, (4 + 3) × 2 = 14: the brackets change the instruction. For signed values, a temperature of −3°C rising by 5°C becomes 2°C. Estimate before calculating: the order must cost more than the ₹6 pencils, so a result below ₹6 cannot fit this story.

### Guided practice, independent practice and revision

Guided: evaluate 9 − 2 × 3. Mark multiplication first: 2 × 3 = 6, then 9 − 6 = 3. Independent: a ₹5 booking fee plus four ₹3 tickets costs how much? Stop before opening the solution.

<details><summary>Step-by-step solution</summary>Four tickets cost 4 × 3 = 12 rupees; add the single fee, 5 + 12 = 17 rupees. The fee is charged once, not per ticket.</details>

Check your work: identify the quantities, write their units, group where needed, calculate in the shared order, and compare with an estimate. Never round an intermediate exact integer merely because an answer looks awkward.

## assessment

Candidate: `candidates\quantitative-aptitude-number-operations.assessment.json`
Candidate SHA-256: `307fbeb174cbb9c426c9a59c6cd4f4bee06ef0947221c83678ed6f26cf147bf7`
Validation: `validation\quantitative-aptitude-number-operations.assessment.validation.json`

Provenance and factual references:
```json
{
  "origin": "original",
  "author": "Forge coding agent \u2014 draft author, not a human reviewer",
  "sources": [
    {
      "source_id": "openstax-arithmetic",
      "url": "https://openstax.org/books/prealgebra-2e/pages/2-1-use-the-language-of-algebra",
      "usage": "factual_reference",
      "status": "resolved",
      "upstream_revision": null,
      "notice": "Original Forge prose and questions; no source text/images redistributed. Human factual/coverage review pending."
    }
  ]
}
```

### guided-order (practice)

Evaluate 9 - 2 * 3 using conventional arithmetic order. Enter a number, with no unit.

Multiply 2 by 3 to get 6; subtract 6 from 9 to get 3.

Exact scoring contract / worked solution / fixtures:
```json
{
  "answer": "3",
  "tolerance": "0",
  "unit": "",
  "rounding": "none",
  "boundary": "inclusive",
  "representation": "decimal",
  "exact_derivation": {
    "op": "subtract",
    "args": [
      "9",
      {
        "op": "multiply",
        "args": [
          "2",
          "3"
        ]
      }
    ]
  }
}
```

### independent-group (practice)

Evaluate (7 + 5) / 3 exactly. Enter a number, with no unit.

The bracket gives 12; dividing 12 by 3 gives 4.

Exact scoring contract / worked solution / fixtures:
```json
{
  "answer": "4",
  "tolerance": "0",
  "unit": "",
  "rounding": "none",
  "boundary": "inclusive",
  "representation": "decimal",
  "exact_derivation": {
    "op": "divide",
    "args": [
      {
        "op": "add",
        "args": [
          "7",
          "5"
        ]
      },
      "3"
    ]
  }
}
```

### transfer-balance (transfer)

A prepaid account holds 23 credits. Two bookings each deduct 6 credits; a single refund adds 4 credits. No other changes occur. What balance remains? Enter the number of credits, without a unit.

Two deductions total 12. The balance is 23 - 12 + 4 = 15 credits.

Exact scoring contract / worked solution / fixtures:
```json
{
  "answer": "15",
  "tolerance": "0",
  "unit": "",
  "rounding": "none",
  "boundary": "inclusive",
  "representation": "decimal",
  "exact_derivation": {
    "op": "add",
    "args": [
      {
        "op": "subtract",
        "args": [
          "23",
          {
            "op": "multiply",
            "args": [
              "2",
              "6"
            ]
          }
        ]
      },
      "4"
    ]
  }
}
```

### recall-signed (recall)

A value starts at -4 and increases by 9. What is its final value? Enter a number.

Move nine units right from -4: -4 + 9 = 5.

Exact scoring contract / worked solution / fixtures:
```json
{
  "answer": "5",
  "tolerance": "0",
  "unit": "",
  "rounding": "none",
  "boundary": "inclusive",
  "representation": "decimal",
  "exact_derivation": {
    "op": "add",
    "args": [
      "-4",
      "9"
    ]
  }
}
```

### mock-order (interview)

Evaluate 18 / 3 * 2. Multiplication and division have equal precedence. Enter a number.

Work left to right: 18 / 3 = 6, then 6 * 2 = 12.

Exact scoring contract / worked solution / fixtures:
```json
{
  "answer": "12",
  "tolerance": "0",
  "unit": "",
  "rounding": "none",
  "boundary": "inclusive",
  "representation": "decimal",
  "exact_derivation": {
    "op": "multiply",
    "args": [
      {
        "op": "divide",
        "args": [
          "18",
          "3"
        ]
      },
      "2"
    ]
  }
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
