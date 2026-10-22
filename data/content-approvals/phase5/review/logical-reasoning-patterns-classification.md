# Human review packet: logical-reasoning-patterns-classification

UNPUBLISHED. Agent-authored material. No human approval is present. The checked references are factual references; no publisher text or illustrations are redistributed.

Review the exact JSON and validation reports. If any candidate changes, validation/review digests must be regenerated; an old approval cannot cover new bytes.

## lesson

Candidate: `candidates\logical-reasoning-patterns-classification.lesson.json`
Candidate SHA-256: `99dac25fa920a0f75704892467f25baab2e6b55989d2512742c21d8f30cfc31f`
Validation: `validation\logical-reasoning-patterns-classification.lesson.validation.json`

Provenance and factual references:
```json
{
  "origin": "original",
  "author": "Forge coding agent \u2014 draft author, not a human reviewer",
  "sources": [
    {
      "source_id": "openstax-logic",
      "url": "https://openstax.org/books/college-algebra-2e/pages/9-1-sequences-and-their-notations",
      "usage": "factual_reference",
      "status": "resolved",
      "upstream_revision": null,
      "notice": "Original Forge prose and questions; no source text/images redistributed. Human factual/coverage review pending."
    }
  ]
}
```

### Goal and intuition

A pattern question is reliable only when its rule is stated or its assumptions are explicit. A few numbers alone do not determine one inevitable continuation. Separate observing a pattern from applying an agreed rule. A classification is similar: say which property is being tested before deciding which objects belong.

### A worked example and why it works

Suppose the first term is 2 and each following term is exactly 3 greater. The positions and values are 1→2, 2→5, 3→8, 4→11, 5→14. To reach position five, make four additions, not five. This rule is explicit, so its fifth term is uniquely 14. For classification, define the group as whole numbers divisible by 2. Among 6, 9 and 12, only 6 and 12 belong: dividing them by 2 leaves no remainder. That definition says nothing about colour or size.

### Guided practice, independent practice and revision

Guided: start at 4 and add 2 at every step. The first four values are 4, 6, 8, 10. Independent: the first term is 10 and every next term is 2 smaller. Find the fourth term.

<details><summary>Trace and answer</summary>Position 1 is 10; position 2 is 8; position 3 is 6; position 4 is 4. There are three transitions. No guessing rule is needed.</details>

Revision: write the starting state, state the transition, label positions, enumerate a short trace, and check every supplied value. If no rule is supplied, ask which alternatives are allowed rather than presenting a guess as a mathematical certainty.

## assessment

Candidate: `candidates\logical-reasoning-patterns-classification.assessment.json`
Candidate SHA-256: `997cc199d4c5fc02a576bb948713ff91e8014404174dae60373cf88689fc62ec`
Validation: `validation\logical-reasoning-patterns-classification.assessment.validation.json`

Provenance and factual references:
```json
{
  "origin": "original",
  "author": "Forge coding agent \u2014 draft author, not a human reviewer",
  "sources": [
    {
      "source_id": "openstax-logic",
      "url": "https://openstax.org/books/college-algebra-2e/pages/9-1-sequences-and-their-notations",
      "usage": "factual_reference",
      "status": "resolved",
      "upstream_revision": null,
      "notice": "Original Forge prose and questions; no source text/images redistributed. Human factual/coverage review pending."
    }
  ]
}
```

### guided-sequence (practice)

The first term is 2. Every following term adds exactly 3. What is term 5? Enter a number.

Enumerate 2, 5, 8, 11, 14; four transitions reach term five.

Exact scoring contract / worked solution / fixtures:
```json
{
  "answer": "14",
  "tolerance": "0",
  "unit": "",
  "rounding": "none",
  "boundary": "inclusive",
  "representation": "decimal",
  "sequence_proof": {
    "start": 2,
    "step": 3,
    "position": 5
  }
}
```

### independent-descending (practice)

Term 1 is 10. Each following term subtracts exactly 2. What is term 4?

The trace is 10, 8, 6, 4.

Exact scoring contract / worked solution / fixtures:
```json
{
  "answer": "4",
  "tolerance": "0",
  "unit": "",
  "rounding": "none",
  "boundary": "inclusive",
  "representation": "decimal",
  "sequence_proof": {
    "start": 10,
    "step": -2,
    "position": 4
  }
}
```

### transfer-positions (transfer)

A marker starts at coordinate -3 at observation 1. Between consecutive observations it moves exactly 4 units right. What coordinate is observed at observation 6?

Five moves add 20 to -3, giving 17. Observation 1 involves no move.

Exact scoring contract / worked solution / fixtures:
```json
{
  "answer": "17",
  "tolerance": "0",
  "unit": "",
  "rounding": "none",
  "boundary": "inclusive",
  "representation": "decimal",
  "sequence_proof": {
    "start": -3,
    "step": 4,
    "position": 6
  }
}
```

### recall-transition (recall)

Term 1 is 7. Add exactly 5 for each next term. What is term 3?

7, 12, 17 requires two transitions.

Exact scoring contract / worked solution / fixtures:
```json
{
  "answer": "17",
  "tolerance": "0",
  "unit": "",
  "rounding": "none",
  "boundary": "inclusive",
  "representation": "decimal",
  "sequence_proof": {
    "start": 7,
    "step": 5,
    "position": 3
  }
}
```

### mock-classify (interview)

The classification rule is 'whole numbers divisible by 2'. Which pair both belongs?

Both 6 and 12 have zero remainder on division by 2; 9 does not.

Exact scoring contract / worked solution / fixtures:
```json
{
  "choices": {
    "a": "6 and 9",
    "b": "6 and 12"
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
