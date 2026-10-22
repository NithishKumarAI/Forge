# Human review packet: verbal-english-sentence-structure

UNPUBLISHED. Agent-authored material. No human approval is present. The checked references are factual references; no publisher text or illustrations are redistributed.

Review the exact JSON and validation reports. If any candidate changes, validation/review digests must be regenerated; an old approval cannot cover new bytes.

## lesson

Candidate: `candidates\verbal-english-sentence-structure.lesson.json`
Candidate SHA-256: `8c2a00dd9c9c19ab3197e549ec790ea8bf483bb5d960948c9e7d6a71995cb69c`
Validation: `validation\verbal-english-sentence-structure.lesson.validation.json`

Provenance and factual references:
```json
{
  "origin": "original",
  "author": "Forge coding agent \u2014 draft author, not a human reviewer",
  "sources": [
    {
      "source_id": "purdue-sentences",
      "url": "https://owl.purdue.edu/owl/general_writing/academic_writing/sentence_variety/sentence_types.html",
      "usage": "factual_reference",
      "status": "resolved",
      "upstream_revision": null,
      "notice": "Original Forge prose and questions; no source text/images redistributed. Human factual/coverage review pending."
    }
  ]
}
```

### Goal and intuition

A sentence lets a reader connect something being discussed with what happens or is true about it. In a plain statement, look for the subject and its verb before extra detail. A clause contains a subject–verb relationship. An independent clause can stand as a complete statement; a dependent clause relies on surrounding text. These are useful checks for standard edited English, not a judgment about a person's accent or worth.

### A worked example and why it works

In 'Mira checks the report', Mira is the subject, checks is the verb, and the report receives the action. 'Because Mira checks the report' still has a subject and verb, but because makes the thought dependent: the reader expects what follows. 'Because Mira checks the report, errors are found early' connects that reason with an independent clause. Descriptive words can lengthen a sentence without adding another clause. In 'The very small robot moves slowly', the subject is the robot and the verb is moves.

### Guided practice, independent practice and revision

Guided: in 'The trainees test the app', ask who performs the action (the trainees), then what action occurs (test). Independent: identify the subject and verb in 'A careful reviewer notices mistakes'.

<details><summary>Explanation</summary>The subject is a careful reviewer, with reviewer as its head noun. Notices is the verb. Mistakes is the object, not the subject.</details>

Revision: find the verb, identify its subject, distinguish the object, and ask whether the clause stands alone. Real writing allows several valid formulations. The objective items below ask about specified sentences; open rewrites should be reviewed as reflection, not rejected by matching one model sentence.

## assessment

Candidate: `candidates\verbal-english-sentence-structure.assessment.json`
Candidate SHA-256: `6e1fd90671386c37c12b03f938d772905a9fb7de0be46ff1b2cdb274a3d8f02c`
Validation: `validation\verbal-english-sentence-structure.assessment.validation.json`

Provenance and factual references:
```json
{
  "origin": "original",
  "author": "Forge coding agent \u2014 draft author, not a human reviewer",
  "sources": [
    {
      "source_id": "purdue-sentences",
      "url": "https://owl.purdue.edu/owl/general_writing/academic_writing/sentence_variety/sentence_types.html",
      "usage": "factual_reference",
      "status": "resolved",
      "upstream_revision": null,
      "notice": "Original Forge prose and questions; no source text/images redistributed. Human factual/coverage review pending."
    }
  ]
}
```

### guided-subject (practice)

In the statement 'The courier carries a parcel', which phrase is the subject?

The courier performs the action carries; a parcel receives it.

Exact scoring contract / worked solution / fixtures:
```json
{
  "choices": {
    "a": "a parcel",
    "b": "The courier"
  },
  "correct": [
    "b"
  ]
}
```

### independent-verb (practice)

In 'Our team reviews changes', which word is the verb?

Reviews describes the action; changes is its object here.

Exact scoring contract / worked solution / fixtures:
```json
{
  "choices": {
    "a": "reviews",
    "b": "changes"
  },
  "correct": [
    "a"
  ]
}
```

### transfer-clause (transfer)

Which option is an independent clause in standard edited English?

The first is a complete statement. Although makes the second clause dependent.

Exact scoring contract / worked solution / fixtures:
```json
{
  "choices": {
    "a": "Although the service restarted",
    "b": "The service restarted."
  },
  "correct": [
    "b"
  ]
}
```

### recall-dependent (recall)

In 'Because the build failed, we checked the logs', which clause is dependent?

Because marks the reason as dependent on the main statement.

Exact scoring contract / worked solution / fixtures:
```json
{
  "choices": {
    "a": "Because the build failed",
    "b": "we checked the logs"
  },
  "correct": [
    "a"
  ]
}
```

### mock-head (interview)

In 'The quiet student near the window asks a question', who asks?

The subject is the student phrase; near the window only describes its location.

Exact scoring contract / worked solution / fixtures:
```json
{
  "choices": {
    "a": "the window",
    "b": "The quiet student near the window"
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
