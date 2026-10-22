# Human review packet: interview-communication-introductions

UNPUBLISHED. Agent-authored material. No human approval is present. The checked references are factual references; no publisher text or illustrations are redistributed.

Review the exact JSON and validation reports. If any candidate changes, validation/review digests must be regenerated; an old approval cannot cover new bytes.

## lesson

Candidate: `candidates\interview-communication-introductions.lesson.json`
Candidate SHA-256: `075fe08ae7e11ec1123eb0b1ced3322d39b2acd72bac053c2f9245f88da7894f`
Validation: `validation\interview-communication-introductions.lesson.validation.json`

Provenance and factual references:
```json
{
  "origin": "original",
  "author": "Forge coding agent \u2014 draft author, not a human reviewer",
  "sources": [
    {
      "source_id": "uk-interviews",
      "url": "https://nationalcareers.service.gov.uk/careers-advice/interview-advice",
      "usage": "factual_reference",
      "status": "resolved",
      "upstream_revision": null,
      "notice": "Original Forge prose and questions; no source text/images redistributed. Human factual/coverage review pending."
    }
  ]
}
```

### Goal and intuition

An introduction helps another person understand what you are doing now and why this conversation is relevant. It is not a competition to invent the strongest biography. Choose a small set of true details: current study or role, one concrete piece of work, what you did, and what you want to learn or contribute. Adapt length to the question and allow the other person to ask more.

### A worked example and why it works

Illustrative rehearsal, not a statement about the learner: 'I am studying computer science. In a small notes project I implemented search and wrote tests for empty results. That taught me to check edge cases. I am interested in an entry-level role where I can strengthen my Python and testing skills.' This gives a current context, a checkable action and a learning direction. It does not claim commercial customers or team leadership. A project description should distinguish your own contribution from the group's work.

### Guided practice, independent practice and revision

Guided: replace each detail in the example with a true detail of your own; remove any sentence you cannot explain with evidence. Independent: write a short introduction for a placement conversation, then a shorter version for a project discussion.

<details><summary>Self-review questions</summary>Can a listener identify your current context? Is there a specific action you personally took? Have you separated fact from aspiration? Could you explain the project if asked? Is there room for a follow-up? Several clear answers can be equally valid.</details>

Revision: be honest, use concrete actions, avoid unsupported labels, respect the requested length, and ask for clarification when needed. Forge stores this as reflection and supplies a rubric, not an automatic communication score or a prediction of hiring success.

## assessment

Candidate: `candidates\interview-communication-introductions.assessment.json`
Candidate SHA-256: `03ae44b362778c5ddddfccd95f558c944630e4e777e0546185f65ce480a9299a`
Validation: `validation\interview-communication-introductions.assessment.validation.json`

Provenance and factual references:
```json
{
  "origin": "original",
  "author": "Forge coding agent \u2014 draft author, not a human reviewer",
  "sources": [
    {
      "source_id": "uk-interviews",
      "url": "https://nationalcareers.service.gov.uk/careers-advice/interview-advice",
      "usage": "factual_reference",
      "status": "resolved",
      "upstream_revision": null,
      "notice": "Original Forge prose and questions; no source text/images redistributed. Human factual/coverage review pending."
    }
  ]
}
```

### guided-introduction (practice)

Write a concise, true introduction. Include current context, a concrete personal action and a learning direction.

Use the rubric to inspect your own explanation; no correctness score is assigned.

Exact scoring contract / worked solution / fixtures:
```json
{
  "example": "Illustrative structure: I am studying __. In __ I personally __. I learned __ and want to develop __.",
  "rubric": [
    "Use only true personal details.",
    "Explain your own action rather than only naming tools.",
    "Leave space for the interviewer to ask more."
  ]
}
```

### independent-project (practice)

Adapt your introduction for a project discussion. State one limitation or uncertainty honestly.

Use the rubric to inspect your own explanation; no correctness score is assigned.

Exact scoring contract / worked solution / fixtures:
```json
{
  "example": "I implemented the search screen and tested empty results. I have not yet measured performance on a large corpus.",
  "rubric": [
    "Separate your work from team work.",
    "State a limitation without inventing results."
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
