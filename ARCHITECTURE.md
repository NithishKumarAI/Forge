# Forge architecture

Forge is one React/TypeScript frontend, one FastAPI backend and one SQLite learner database. The current runtime has no model provider, SDK import, generated learning content or model grading. Product edition identity and numeric content levels remain separate from curriculum revision and learner mastery.

## Runtime flow

```text
React / Vite
  -> FastAPI -> immutable local content registry + curriculum bindings
             -> SQLite attempts, historical records, evidence and FSRS state
  -> public Run: Pyodide or fresh PGlite browser worker (no scored evidence)
  -> Submit: exact frozen selection + source/answer
             -> Decimal/choice policy or bounded local worker verification
             -> atomic attempt + provenance + unique evidence credit + projection/FSRS
```

Python submission verification executes only in a child interpreter (`-I -S`) with a restricted AST/built-in/module subset, empty disposable working directory, no inherited secrets, memory/process/instruction/output limits and a parent timeout. Unsupported code fails closed without evidence. SQL submission verification executes in a bounded Node child process with fresh isolated PGlite fixtures, read-only query transactions, exact columns, duplicate/NULL/order comparisons and alternate datasets. No learner Python runs on the UI main thread; no learner SQL touches Forge SQLite. Browser Run still uses the existing Pyodide/PGlite worker implementations.

The repository and local operating-system administrator remain trust boundaries. Backend verification does not establish secure remote proctoring. The restricted Python interpreter is not a general-purpose hostile-code hosting service. Missing Node/runtime assets or unsupported capabilities produce an explicit unverified result, not a trusted client-score fallback.

## Static content and publication

Phase 1 content-addressed snapshots and exact curriculum-topic bindings remain authoritative. Phase 2 validates complete portable candidates, provenance/coverage and exact execution contracts, then requires independent human review before a release can be imported. Phase 3 custom edition targets require explicit reviewed confirmation and exact immutable graph digests. Omitted publication source type retains its historical default meaning.

`assessment_bundle` extends the existing pipeline; it does not introduce a second publication store. Its immutable items declare stable identities, equivalence families, subject/topic/level, practice/transfer/recall/interview purposes, reviewed independent-variant classification, public samples, full scoring contracts and authored feedback. Coding references and negative implementations must pass the development validator. An assessment target must match the confirmed subject/topic placement. Existing release archives keep their original hash inputs and gates.

Runtime pools derive only from the effective reviewed release. Legacy static course practice is available only through historical curricula and is explicitly unverified; it is not promoted into the new scored pools. Generated legacy exercises remain historical records. Transfer excludes exposed/revealed families; coding subjects require coding variants. Selection/exposure is persisted for resume. Missing pools never trigger generation.

## Phase 5 plans, tests and schema version 6

Migration 6 adds StudyPlanRevision/Entry and TimedTestSession/Item. Frozen migrations 1–5 are unchanged. Plan revisions snapshot exact approved activities by selected IANA local date and timezone. Settings changes require explicit regeneration; terminal items survive across revisions. Due FSRS work, Python/SQL/DSA minima, weaknesses, prerequisites and subject rotation drive allocation. Insufficient approved content leaves free minutes, never invented tasks. Manual subject/topic access remains unrestricted.

Timed tests use shared immutable AssessmentSelection snapshots with purpose `timed`, static versioned blueprints, fixed weights and server deadlines. Drafts survive refresh; submitted answers lock. Finishing after a deadline rolls back a transient evaluation and completes with previously committed responses. Answer grading is binary full-contract correctness; only the mixed blueprint deducts 0.25 for submitted incorrect answers. Unanswered items score zero. Reports are immutable and revealed only after completion. Timed work creates no mastery evidence, review ratings or global mistake updates. Scored interview/timed contexts share help and solution embargo guards.

The Windows owner process prebinds loopback before starting the app and publishes its native creation identity, executable, exact command hash and unique runtime owner. Open/close use a per-runtime mutex and verify a held process handle before stopping it. Verification uses explicit disposable databases and runtime directories. The optional `FORGE_VERIFY_NO_NETWORK=1` guard denies external Python DNS/TCP and provider imports inside verification processes; it is not a machine-wide firewall. Browser verification separately rejects external requests. Monaco, fonts and worker assets resolve locally after installation/build.

## Attempts and evidence

Migrations 1–4 and their frozen DDL/checksums are unchanged. Additive migration 5 introduces:

- `AssessmentSelection`: exact curriculum/topic/session, content revision/SHA, item/family, immutable contract snapshot, purpose, assistance/hints/reveal, completion/result, attempt/Arena/interview linkage and scoring/judge versions.
- `EvidenceCredit`: a unique topic/family/purpose credit linked to the exact selection and original evidence event, plus a global Arena-family claim across curriculum switches. Recall credits include the FSRS due cycle so a later weak recall remains meaningful.
- `EvidencePolicyRecord`: the previous learner projection and original evidence IDs at the first new qualifying event, explicitly labeled `legacy/unversioned` alongside the new policy version.
- `AssessmentHelpEvent`: append-only help/solution-reveal audit, including permitted reveals after completion.

These are additive detail/association tables over existing `LearningSession`, `Attempt`, `ArenaAttempt`, `MasteryEvidenceEvent`, `ReviewState` and interview records. Completed selection snapshots, exposure history, credit, help events and policy records are immutable. Ownership/content triggers reject mismatched associations. The existing backup-first atomic migration runner validates schema/trigger presence, refuses modified applied definitions and rolls back failed DDL/ledger writes.

New evidence uses `forge-evidence/2`; worker verification uses `forge-worker/1`. A qualifying approved independent Arena solve retains `event_type="arena"`, has an exact Arena-attempt/selection/credit linkage and enters the practice projection once. Ambiguous historical Arena rows remain unchanged and excluded from new credit. Replay comparisons run read-only on synthetic/copied data; startup and normal browsing never backfill/recalculate historical attempts or copy mastery.

Practice remains capped at 79; clean transfer at 89; 90+ requires qualified recall at least 24 elapsed hours later. Weak delayed recall may lower mastery. MCQ-only work cannot unlock coding transfer. Reflection, reading, chat and study minutes create no mastery evidence. Objective score-to-FSRS ratings remain fixed code and FSRS card JSON stays versioned. Attempt/evidence/projection/review completion commits as one transaction; the HTTP submit path serializes writes and retry uses the saved selection identity.

## Static guidance and interview safety

FTS5 search stays curriculum/revision scoped. Guidance returns exact authored excerpts and lesson/section links rather than invented text. Existing Learn revision selectors and revision-scoped `ContentSectionProgress` remain unchanged in meaning. Legacy conversations/usage/generation metadata are preserved; model-era sessions have no invented continuation.

Backend guards block static help, lesson/search reads, hints, solution reveals and saved answer reports during an active scored interview. Permitted help during unfinished transfer or recall records assistance; revealing the item ends its clean-credit eligibility. Recall excludes recently helped/revealed variants for 24 hours. Public DTOs omit answer keys, hidden fixtures and references. Developer reference-validation endpoints are retired from learner routes.

Objective interviews use fixed competency/weight blueprints and snapshot exact selected item identities/revisions/hashes before the session starts. The 30-minute deadline survives save/resume. Results and authored explanations stay hidden until the entire interview completes. Communication/project rehearsal uses prewritten prompts/rubrics/examples and stores reflection without technical mastery or a scored denominator. Its shared selection may have no topic and creates no artificial topic attempt. Historical interview sessions/questions/responses/reports are retained verbatim and unknown historical modes remain readable.

## Boundaries and next phase

No application runtime module imports `scripts.authoring` or a provider. Optional provider tooling lives outside `app` with its own requirements; inactive legacy code/test text is never imported. Normal requirements contain no Google model SDK or key configuration. Installed SDK absence and outbound-model-call prevention are tested separately from content availability.

All nine Placement Foundations subjects still need independently reviewed educational content/pools. Infrastructure tests use isolated synthetic approvals, never production review records. The existing advisory planner is preserved; the redesigned 5/6/8-hour planner, subject/mixed timed-test system, full content release and final browser/network-denial/Windows packaging verification belong to the final combined phase. Build/unit tests do not certify the installed product as fully offline.
