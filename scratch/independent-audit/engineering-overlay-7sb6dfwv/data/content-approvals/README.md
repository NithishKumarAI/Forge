# Content publication workflow

No human review or published release is included in Phase 2. The corrected Two Sum 1.0.1 candidate is structurally and execution validated, awaiting independent human review. Legacy material remains available with its existing baseline status.

Run these commands from `C:\My PC\git\Forge\apps\api` using the existing `.venv`. No command calls an LLM. Paths below refer to repository artifacts; replace the reviewer name/notes and explicitly select the destination database yourself.

```powershell
.\.venv\Scripts\python.exe -m scripts.content_checks.publish inspect --candidate '../../data/content-approvals/candidates/two-sum-1.0.1.json'
.\.venv\Scripts\python.exe -m scripts.content_checks.publish validate --candidate '../../data/content-approvals/candidates/two-sum-1.0.1.json' --output '../../data/content-approvals/two-sum-1.0.1.validation.json'
```

Read the full candidate and [teaching checklist](../../docs/forge-v1/TEACHING_QUALITY_CHECKLIST.md), compare the historical and corrected revisions, and inspect every normal/edge/negative test. Copy `review-checklist.template.json` to `two-sum.review-checklist.json`. Only after personally completing each check, set the corresponding value true. Do not submit this command on behalf of a human or fabricate a reviewer identity.

```powershell
.\.venv\Scripts\python.exe -m scripts.content_checks.publish review --candidate '../../data/content-approvals/candidates/two-sum-1.0.1.json' --validation '../../data/content-approvals/two-sum-1.0.1.validation.json' --checklist '../../data/content-approvals/two-sum.review-checklist.json' --reviewer 'YOUR NAME' --notes 'Describe the independent technical, clarity, coverage and provenance checks you performed.' --outcome approved --i-am-the-human-reviewer --output '../../data/content-approvals/two-sum.human-review.json'
.\.venv\Scripts\python.exe -m scripts.content_checks.publish package --candidate '../../data/content-approvals/candidates/two-sum-1.0.1.json' --validation '../../data/content-approvals/two-sum-1.0.1.validation.json' --review '../../data/content-approvals/two-sum.human-review.json' --targets '../../data/content-approvals/two-sum-targets.json' --release-id two-sum-1.0.1 --output '../../data/content-approvals/two-sum-1.0.1.release.json'
.\.venv\Scripts\python.exe -m scripts.content_checks.publish publish --package '../../data/content-approvals/two-sum-1.0.1.release.json' --database 'C:\PATH\TO\YOUR\Forge\forge.db'
```

Use `--outcome rejected` to retain a rejection. An approved package must contain the canonical JSON bytes written by `package`; reformatting is rejected by publication. All checks are rerun before publication. Changed content/coverage/provenance requires a fresh validation and review. Artifact paths cannot be overwritten with different bytes. Use a new version/path when correcting an artifact.

The single `package` command builds one candidate entry; a complete multi-entry package uses the same validated `ReleasePackage` schema. Entries explicitly identify confirmed curriculum graphs, topics and lesson order. A release is a complete overlay: include all previously approved entries you intend to keep selected. Unmentioned topics use the legacy compatibility baseline. Activation selects the whole release atomically; the curriculum selection itself never changes.

Keep candidate, validation, human-review, target and canonical release artifacts in the repository so a fresh installation can reproduce the approved bytes. A fresh database can be reconstructed explicitly with:

```powershell
.\.venv\Scripts\python.exe -m scripts.content_checks.publish restore --package '../../data/content-approvals/two-sum-1.0.1.release.json' --database 'C:\PATH\TO\NEW\forge.db'
```

Restore uses migrations and idempotent default curriculum/content registration, then imports the verified archive. A genuinely empty restore receives the same existing revision-2 default as a normal fresh installation; it creates no new curriculum edition. Existing settings and history are preserved. If restoring into a preinitialized Forge database, retain that database's current curriculum selection. Archives are deliberately not automatically watched at startup: a failed publication's complete archive or orphan snapshot cannot activate itself on restart.

Revocation/rollback is explicit:

```powershell
.\.venv\Scripts\python.exe -m scripts.content_checks.publish transition --database 'C:\PATH\TO\YOUR\Forge\forge.db' --release-id two-sum-1.0.1 --status revoked --actor 'YOUR NAME' --reason 'Explain why this release is being withdrawn.'
```

Use `activated` to select a previous complete release, or `superseded` to retire the selected overlay. The service is `transition_release(session, release_id, status, actor, reason)` in `app.services.content_publication`. It appends an event and rebuilds the derived index transactionally. Revocation falls back to the legacy compatibility bank; explicit activation of a previous complete release restores that overlay. Repeating publication never undoes a revocation. All old content and release records remain inspectable.

`arena-provenance.json` inventories all 110 historical problems. Nine declare Exercism adaptation while saying `source_type=original`; their raw conflicting metadata remains preserved. The Celsius problem has a separate historical-document/JSON conflict. These ten need provenance reconciliation before any new publication. The other 100 have unreviewed originality claims. Repository-level MIT pages do not establish any item's pinned upstream version or satisfy an independent technical review.

The trust boundary is the local reviewer and repository. Review records are auditable attestations, not cryptographic proof of a person's identity. Backend imports verify digests and structured approval contracts; the human-operated CLI additionally reruns executable checks. Runtime never executes candidate code or fetches a source URL.

New lesson `content_hash` uses the canonical SHA-256 of the raw lesson object excluding `content_hash` and `generated_at`; the bundle digest separately includes those fields and the complete exercise array. Legacy hash values remain historical facts. Every example has either an exact fixture or an explicit contextual/manual-review reason. Course coding items without a supported independent judge contract fail closed; use an original Arena revision until Phase 4 adds the broader assessment engine. Coverage references and prerequisites must resolve to existing registry keys or other entries in the same release, with no prerequisite cycle.
