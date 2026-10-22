# Human review packet: system-design-requirements

UNPUBLISHED. Agent-authored material. No human approval is present. The checked references are factual references; no publisher text or illustrations are redistributed.

Review the exact JSON and validation reports. If any candidate changes, validation/review digests must be regenerated; an old approval cannot cover new bytes.

## lesson

Candidate: `candidates\system-design-requirements.lesson.json`
Candidate SHA-256: `f16b8d96283677e13bb4fbe24dcd2a339f8504b9e348600ff0b31f65307bfcba`
Validation: `validation\system-design-requirements.lesson.validation.json`

Provenance and factual references:
```json
{
  "origin": "original",
  "author": "Forge coding agent \u2014 draft author, not a human reviewer",
  "sources": [
    {
      "source_id": "nasa-requirements",
      "url": "https://www.nasa.gov/reference/systems-engineering-handbook/",
      "usage": "factual_reference",
      "status": "resolved",
      "upstream_revision": null,
      "notice": "Original Forge prose and questions; no source text/images redistributed. Human factual/coverage review pending."
    }
  ]
}
```

### Goal and intuition

Start with the job a small system must do, not a collection of fashionable components. A functional requirement describes a user-visible action. A constraint limits the solution, such as using one school computer. A quality requirement describes a property that can be checked, such as an agreed response-time target under a stated workload. Put the boundary around what this version owns.

### A worked example and why it works

A small club needs a shared equipment notebook. Members can view items and a volunteer can mark an item borrowed or returned. The first version serves 20 members on a local network; payments and public sign-up are out of scope. A simple browser → local service → database path is enough to discuss initially. Before choosing a cache or queue, ask whether a measured problem needs one. If two people request one item at the same moment, the borrowing rule needs an explicit consistency decision; drawing more boxes does not decide it.

### Guided practice, independent practice and revision

Guided: 'Members can see which items are available' is functional. 'Works on the existing local computer' is a constraint. Independent: define a minimal attendance notebook, list two actions, one limit and one failure case.

<details><summary>Illustrative review, not the only correct design</summary>Record attendance and view a day's list; serve one classroom on the local network; retain a saved record after a restart. Decide whether repeat marks update a record or are rejected. Other coherent boundaries can be valid.</details>

Revision: name the users, state actions, record limits, make success observable, identify failures and exclude tempting extras. Open designs use a rubric; Forge does not automatically judge arbitrary architecture prose.

## assessment

Candidate: `candidates\system-design-requirements.assessment.json`
Candidate SHA-256: `568c108ac0dd89e81d91702caef818f52d47ab7d0126db54f6ff006f36d842dc`
Validation: `validation\system-design-requirements.assessment.validation.json`

Provenance and factual references:
```json
{
  "origin": "original",
  "author": "Forge coding agent \u2014 draft author, not a human reviewer",
  "sources": [
    {
      "source_id": "nasa-requirements",
      "url": "https://www.nasa.gov/reference/systems-engineering-handbook/",
      "usage": "factual_reference",
      "status": "resolved",
      "upstream_revision": null,
      "notice": "Original Forge prose and questions; no source text/images redistributed. Human factual/coverage review pending."
    }
  ]
}
```

### guided-boundary (practice)

Describe the equipment notebook's users, two functional actions, one constraint and one explicit exclusion.

Use the rubric to inspect your own explanation; no correctness score is assigned.

Exact scoring contract / worked solution / fixtures:
```json
{
  "example": "Members view availability; a volunteer records loans. One local computer is used; payments are excluded.",
  "rubric": [
    "Separate user actions from technology choices.",
    "State a boundary and a limitation."
  ]
}
```

### independent-attendance (practice)

Write a small attendance notebook specification. State a failure case and how success would be checked.

Use the rubric to inspect your own explanation; no correctness score is assigned.

Exact scoring contract / worked solution / fixtures:
```json
{
  "example": "Save one record per learner per date; reject accidental duplicates; verify records survive restart.",
  "rubric": [
    "Several coherent answers are possible.",
    "Include an observable check and a failure boundary."
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
