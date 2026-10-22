# Human review packet: ai-fundamentals-ai-ml-dl

UNPUBLISHED. Agent-authored material. No human approval is present. The checked references are factual references; no publisher text or illustrations are redistributed.

Review the exact JSON and validation reports. If any candidate changes, validation/review digests must be regenerated; an old approval cannot cover new bytes.

## lesson

Candidate: `candidates\ai-fundamentals-ai-ml-dl.lesson.json`
Candidate SHA-256: `0dd1db4e014fe140bb3630dc6c7a2c0b7a172fbb955b99478d62c9c01fba6e5c`
Validation: `validation\ai-fundamentals-ai-ml-dl.lesson.validation.json`

Provenance and factual references:
```json
{
  "origin": "original",
  "author": "Forge coding agent \u2014 draft author, not a human reviewer",
  "sources": [
    {
      "source_id": "google-ml-intro",
      "url": "https://developers.google.com/machine-learning/intro-to-ml/what-is-ml",
      "usage": "factual_reference",
      "status": "resolved",
      "upstream_revision": null,
      "notice": "Original Forge prose and questions; no source text/images redistributed. Human factual/coverage review pending."
    }
  ]
}
```

### Goal and intuition

AI is a broad label for computer systems performing tasks associated with intelligent behaviour. Machine learning is an approach in which behaviour is fitted from data rather than every rule being hand-written. Deep learning is a family of machine-learning methods using neural networks with multiple learned layers. These are overlapping categories, not three separate products. A system can use ordinary rules without learning from examples.

### A worked example and why it works

Imagine sorting incoming messages. A fixed rule that flags a message when its subject contains a specified word uses no training data. A model fitted to labeled examples of spam and normal messages is machine learning. A multi-layer neural-network classifier is both deep learning and machine learning. Training adjusts learned parameters; inference applies the trained model to a new input. A correct-looking output alone does not establish how the system was built, and a learned model can still make mistakes.

### Guided practice, independent practice and revision

Guided: a hand-written multiplication function does not become machine learning because it runs on a computer. Independent: a classifier is trained on past labeled messages using a multi-layer neural network. Which categories include it?

<details><summary>Explanation</summary>It is deep learning, which is within machine learning, used for an AI task. The evidence is the stated training method, not a brand name. This tells us nothing by itself about accuracy, fairness or reliability.</details>

Revision: distinguish task, learning method, training and inference; ask what data and evaluation support a claim. These offline scenarios do not require an API key or live model. Product-specific model features change; this lesson deliberately avoids claims about current model prices or capabilities.

## assessment

Candidate: `candidates\ai-fundamentals-ai-ml-dl.assessment.json`
Candidate SHA-256: `3106c95cf8fa2500acf41f01f470e6ccd27ae7e16463360238ee9a9af13c44cc`
Validation: `validation\ai-fundamentals-ai-ml-dl.assessment.validation.json`

Provenance and factual references:
```json
{
  "origin": "original",
  "author": "Forge coding agent \u2014 draft author, not a human reviewer",
  "sources": [
    {
      "source_id": "google-ml-intro",
      "url": "https://developers.google.com/machine-learning/intro-to-ml/what-is-ml",
      "usage": "factual_reference",
      "status": "resolved",
      "upstream_revision": null,
      "notice": "Original Forge prose and questions; no source text/images redistributed. Human factual/coverage review pending."
    }
  ]
}
```

### guided-learning (practice)

A message filter's parameters are fitted from labeled examples. Which description follows from that information?

The stated fitting process learns from data; a specific network architecture has not been specified.

Exact scoring contract / worked solution / fixtures:
```json
{
  "choices": {
    "a": "It must use a hand-written rule for every message.",
    "b": "It uses machine learning."
  },
  "correct": [
    "b"
  ]
}
```

### independent-inference (practice)

A trained classifier is applied to one new message without updating parameters. What stage is this?

The saved parameters are being used rather than fitted.

Exact scoring contract / worked solution / fixtures:
```json
{
  "choices": {
    "a": "Inference",
    "b": "Training"
  },
  "correct": [
    "a"
  ]
}
```

### transfer-evidence (transfer)

A team reports that its classifier uses a neural network with several learned layers trained on examples. Which relationship is justified?

Deep learning is a family of machine-learning methods; the stated architecture supplies the evidence.

Exact scoring contract / worked solution / fixtures:
```json
{
  "choices": {
    "a": "It is a deep-learning system and also a machine-learning system.",
    "b": "Deep learning is unrelated to machine learning."
  },
  "correct": [
    "a"
  ]
}
```

### recall-fixed-rule (recall)

A program always flags a message if the literal word URGENT appears, using only that hand-written rule. What is justified?

The description gives no training or learning process.

Exact scoring contract / worked solution / fixtures:
```json
{
  "choices": {
    "a": "This description does not establish machine learning.",
    "b": "Any program reading text must be machine learning."
  },
  "correct": [
    "a"
  ]
}
```

### mock-limits (interview)

A model answered one example correctly. What follows?

One example cannot establish performance across unseen inputs.

Exact scoring contract / worked solution / fixtures:
```json
{
  "choices": {
    "a": "That one output matched; broader reliability still needs evaluation.",
    "b": "Every future output is guaranteed correct."
  },
  "correct": [
    "a"
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
