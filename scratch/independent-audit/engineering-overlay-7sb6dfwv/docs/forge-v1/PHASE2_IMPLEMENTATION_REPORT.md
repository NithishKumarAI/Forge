# Forge V1 Phase 2 implementation report

Date: 21 October 2026. Local checkout: `C:\My PC\git\Forge`, branch `main`, HEAD `8055eb8` (`phase 1 done`). The working tree was clean before implementation. Git's warnings about the two pre-existing inaccessible pytest directories were retained; those directories were not touched. No commit, push, reset, learner-data deletion, application shutdown or paid model call was performed.

## 1. Implemented boundary

Phase 2 implements exact-bundle validation, conservative provenance gates, digest-bound human review, append-only approval/release storage, atomic release selection, revision-safe Arena compatibility, source-fetch restrictions and a reusable teaching review contract. It does not implement Phase 3, activate a new curriculum, remove Gemini, change mastery, replay evidence, redesign planning/interviews or generate the nine-subject curriculum.

The corrected Two Sum revision is **validated and awaiting independent human review**. No human approval, approved release or new live content selection was fabricated. Existing content retains its legacy status and availability. Publication is deliberately blocked until the human-operated workflow in [data/content-approvals/README.md](../../data/content-approvals/README.md) is completed.

## 2. Exact source/artifact files

Created:

- `apps/api/app/migrations/{v003_content_publication.py,publication_schema.json}`
- `apps/api/app/schemas/publication.py`
- `apps/api/app/services/{content_policy.py,content_publication.py}`
- `apps/api/scripts/content_checks/{__init__,bundle,coverage,examples,problems,provenance,publish,python_worker}.py`
- `apps/api/tests/test_content_publication.py`
- `apps/web/scripts/validate-content-sql.mjs`
- `content/problem-bank/revisions/dsa/dsa-two-sum-indices/1.0.1.json`
- `data/content-approvals/README.md`
- `data/content-approvals/arena-provenance.json`
- `data/content-approvals/candidates/two-sum-1.0.1.json`
- `data/content-approvals/review-checklist.template.json`
- `data/content-approvals/two-sum-1.0.1.validation.json`
- `data/content-approvals/two-sum-targets.json`
- `docs/forge-v1/{TEACHING_QUALITY_CHECKLIST.md,PHASE2_IMPLEMENTATION_REPORT.md}`

Modified:

- `LICENSES/exercism-mit.txt`, `THIRD_PARTY_CONTENT.md`
- `apps/api/app/main.py`, `app/migrations/runner.py`
- `apps/api/app/models/{entities.py,__init__.py}`
- `apps/api/app/routers/arena.py`, `app/schemas/arena.py`
- `apps/api/app/services/{arena,content_registry,course}.py`
- `apps/api/scripts/course_builder/{build,fetch,promote,sources,validate}.py`
- `apps/api/scripts/problem_builder/{promote,validate}.py`
- `apps/api/tests/test_database_migrations.py` (expected current schema advances from 2 to 3; preservation/failure assertions remain)
- `apps/web/src/pages/ArenaPage.tsx`, `src/services/api.ts`, `src/types/arena.ts` (carry exact revision ID on submission)

Verification caches, build outputs, temporary databases and test snapshots are not source deliverables. Disposable Phase 2 scratch directories are cleaned after checks. No existing accepted JSON file or migration 1/2 frozen definition was edited.

## 3. Statuses and exact identity

The following statuses are distinct:

- **Structurally valid:** schemas, keys, versions, complete lesson/exercise bundle, source consistency, references, prerequisites, hashes and fixture links pass. This is not a correctness or teaching approval.
- **Executable and test-validated:** supported examples/reference implementations match typed outputs or stdout, including exceptions and fixtures. Contextual fragments are explicitly `requires_review`, never counted as executed.
- **Editorially reviewed:** an independent named human records the technical, semantic-answer, coverage, provenance and beginner-clarity checklist against the exact candidate/report digests.
- **Approved for release:** every required coverage record is covered, all gates pass, and an approved human review identifies the exact digests. The portable package contains candidate, validation, review and confirmed-graph target records.
- **Published:** one successful database transaction registers the complete release overlay and appends its publication event. An approved package file alone is not publication.

The canonical digest convention remains Phase 1's UTF-8 JSON, sorted keys, compact separators, Unicode retained, no NaN/infinity and no trailing newline. Candidate SHA-256 is computed from the validated Candidate schema with explicit defaults and includes payload, provenance, coverage, example contracts, negative solutions and dependency declarations. Payload SHA-256 identifies the exact lesson-plus-exercises or complete raw problem snapshot that runtime reads. The validation report has its own policy version (`forge-content-checks/1`) and digest. Review records bind both candidate and report digests. Target graph hashes and the review are also inside the immutable release package digest.

New lesson hashes use canonical raw lesson JSON excluding `content_hash` and `generated_at`; the enclosing bundle digest includes both fields and exercises. Legacy unexplained hashes are preserved, not reinterpreted as valid new hashes.

## 4. Migration 3 and append-only records

Migration 3, `content_publication`, uses the existing migration runner, verified backup path and transactional ledger. Migrations 1 and 2, their frozen DDL and checksums are unchanged. The runner validates the new frozen schema and required trigger presence and rejects an unrecorded partial publication schema.

Six additive tables:

- `ContentValidationReport`: immutable report digest, candidate/payload digests, policy version, complete candidate and report JSON, registration time.
- `ContentReviewRecord`: immutable review digest, exact validation-report FK, reviewer identity, timestamp, outcome and complete checklist/notes JSON. Rejected reviews can also be recorded.
- `ApprovedContentRelease`: stable release identity, package digest, full reproducible archive and publication time.
- `ContentReleaseEntry`: release/curriculum/topic/content-revision association, deterministic order and exact validation/review FKs. A lesson can target multiple topics in the same curriculum.
- `ContentReleaseEvent`: append-only publication, activation, supersession or revocation with actor/reason/time. Latest explicit event selects the complete overlay.
- `ArenaAttemptContent`: exact immutable content revision for new attempts/Give Up records. No historical attempt is rewritten or assigned an inferred new revision.

UPDATE/DELETE triggers protect all six tables. Insert triggers require exact payload validation plus an approved linked review, enforce curriculum ownership, validate release transitions and enforce Arena attempt/problem identity. Existing immutable content/binding triggers remain intact. `ContentRevision.approval_status` is never changed in place: new registered rows retain `candidate`; effective publication status comes from release records. Legacy baselines retain `legacy_baseline`.

## 5. Validation architecture

`scripts.content_checks.bundle` validates one complete portable `Candidate`. It never reads accepted exercises to validate different candidate exercises and supports first-time content without an accepted sibling. The legacy course validator additionally accepts an explicit exercise path; the optional builder supplies its candidate path only after both candidates exist. Both old replacement promoters now require a reviewed package and explicit session, delegating to the common pipeline. Automatic `--promote` is disabled before any provider call.

Coverage is a versioned competency specification with exact section/exercise/test/dataset references. It reports covered, partially covered, missing and requires review. Dangling references, duplicate identities, unresolved prerequisites and cycles block publication. Literal keywords cannot establish covered competencies. An explicit human coverage review covers the exact embedded specification.

MCQs require valid indices, distinct options, explicit assumptions, answer text matching the selected option and an explanation. These are structural consistency checks; the human must establish that the answer/explanation is actually correct. Short-answer references and rubrics are required; no keyword-overlap grading or model assertion produces approval. New course coding types without a supported independent contract fail closed; broader course assessment types remain Phase 4 work.

The pure backend provenance/coverage policy is shared with development checks. Backend import verifies structures, policy/digests, coverage/provenance consistency, human review completeness, independence and target graph identity. The development CLI reruns executable checks before accepting review and before publication/restore. Runtime startup verifies stored release packages and exact snapshots; it never executes educational code or fetches sources.

### Python

Teaching code executes only in a child interpreter (`-I -S`) with an empty disposable working directory and an environment containing no API/database settings or user secrets. The restricted subset provides explicit safe built-ins and selected math/collection/etc. exports through namespaces, not real module objects or their ambient `sys/os` references. AST checks reject unsafe names/imports/introspection; an audit hook denies file, network and process operations. Windows job limits bound process memory to 256 MiB and process count to one; POSIX uses resource limits. Instruction, output, source/input size and wall-clock limits fail closed. A Python `input()` example without explicit stdin raises EOFError rather than being falsely counted as self-contained execution. Unsupported contextual examples need manual review; there is no unrestricted fallback in the backend.

Typed comparison distinguishes list/tuple and bool/int, recursively checks values, handles dictionary ordering correctly, checks exception behavior and compares documented stdout under declared normalization rules. The development worker is a restricted teaching interpreter, not a general-purpose hostile-code hosting service. Learner execution remains in the existing browser workers.

### SQL

The stdin-driven Node helper creates fresh PGlite databases for every fixture/dataset and has a bounded process timeout/heap. It compares column identities, duplicate-preserving rows, NULLs and explicit order; alternate datasets are executed when supplied. Arena checks reuse the existing `validateSqlProblem` implementation, preserving its table/alternate-data/result checks while feeding exact candidate objects instead of looking up an accepted key. SELECT/CTE Arena policy remains. SQL lesson examples can provide independent setup fixtures; external-context fragments are explicitly manual. No SQL reaches Forge SQLite.

## 6. Publication, history and recovery

The lifecycle is draft -> candidate -> validated -> human reviewed -> approved portable package -> published release. `inspect`, `validate`, `review`, `package`, `publish`, `restore` and `transition` commands expose each operation explicitly; exact commands and the unchecked review template are in the workflow README. The review command requires a human attestation, independent reviewer, timezone-aware timestamp, all checklist items and notes. No real human review command was run during this implementation.

Artifact writes use atomic non-replacing publication. Changing registered provenance under the same key/revision is rejected even when payload bytes are identical; use a new content revision. Startup also compares the stored provenance with the reviewed archive. Existing artifact/release identities cannot acquire different bytes. The complete canonical approved archive is input to publication; DB release, bindings/exercises, event and FTS rebuild commit together. Failed publication rolls back visibility and history. Complete archives and orphan content-addressed files are inert until explicit import; startup never watches an approval directory and therefore cannot activate a failed candidate. Repeating the same publication adds no records and cannot undo revocation.

New lesson associations append at free legacy binding indices to satisfy existing ownership/progress triggers. The selected release defines their effective topic order (including API order metadata); old associations are retained. Current exercises and FTS follow selected bindings. Lesson choices and Arena DTOs expose stored provenance and snapshot digests, preserving source/notice metadata through API transformations. Explicit lesson IDs retain access to old revisions with their own progress. Revocation/supersession appends an event and falls back to legacy compatibility content; activation of a previous complete release is an explicit rollback. Release overlays are complete sets: include previous approved entries that should remain selected; unmentioned topics retain legacy compatibility.

Fresh installation reconstructs snapshots from tracked legacy source files and an explicitly imported approved archive. The restore CLI initializes through numbered migrations, registers the existing default content and verifies/recreates the approved snapshot bytes from the archive. An empty restore uses the same existing revision-2 default as normal first startup; populated installations keep their selection. Archives include the complete source payload, provenance, coverage, validation and review and do not depend on an ignored snapshot store being copied from the developer machine. Keep those archives with backups. A corrupt existing snapshot fails visibly; explicit recovery uses a verified archive/new destination rather than overwriting historical bytes silently.

## 7. Two Sum correction and compatibility

Original `content/problem-bank/dsa/dsa-two-sum-indices.json`, revision 1.0.0, remains byte-for-byte unchanged, including its known tuple/list contradiction. The corrected independent revision is `content/problem-bank/revisions/dsa/dsa-two-sum-indices/1.0.1.json`; its candidate and deterministic report are tracked under `data/content-approvals`.

The authoritative structured contract renders the displayed statement/examples. Starter and reference signatures must match exact parameter/return annotations. Constraints, visible example links, typed hidden results and numeric/list bounds are checked. The corrected contract returns `[i, j]` with distinct `i < j`, smallest `j` then smallest `i`, and returns `[]` when no pair exists. Inputs are not mutated. Hints/explanation describe checking complements before inserting the current value and retaining earliest indices. Complexity states expected O(n) time/O(n) space.

Ten cases cover normal pairs, middle pairs, duplicate values, repeated values/tie-breaking, negatives, zeros, empty/single/no-pair input and integer boundaries. Two deliberately wrong implementations (tuple output and reused index) are rejected. Contradictory displayed output, starter parameter, constraints and hidden result are negative tests. The full problem validator includes both historical and new revisions; revision 1.0.1 is executable/test-validated, **not human-approved or published**.

Release-aware selection does not update `ArenaProblem.version` or old `ArenaTopicBinding` rows. Selected releases resolve the new revision/topic through `ContentReleaseEntry`; old revisions remain available through `load_problem(..., revision_id=...)` and the revision-specific read API. New attempts carry an exact content-revision link; stale submissions and new-release submissions missing an exact revision ID are rejected before appending anything. Solving an old revision does not unlock the new revision's explanation. Existing key-based first-solve/mastery policy is unchanged; no historical evidence is replayed.

## 8. Provenance and licenses

`arena-provenance.json` records every one of the 110 existing problems: original raw metadata, canonical snapshot digest, classification, conflicts, status and publication blocker. Nine declare Exercism adaptation while also declaring `source_type=original`: anagram-check, bob, collatz, flatten-list, leap-year, pangram, raindrops, two-fer and word-count (all `python-` keys). Their metadata is preserved through model serialization, snapshots and public attribution; the DTO truthfully identifies adaptation and retains the original declared type separately.

The attribution list now matches those nine. The former Celsius attribution claim is retained as an explicit unresolved document/JSON discrepancy. Upstream candidate links are labeled unverified; no per-item commit, author or permission date was invented. The public [Python repository license](https://github.com/exercism/python/blob/main/LICENSE) and [problem-specifications license](https://github.com/exercism/problem-specifications/blob/main/LICENSE) were checked for repository-level notices. The historical local notice remains verbatim, with an appended reconciliation explaining its limits. This does not certify any item's complete notice chain.

Nine adaptations plus the Celsius discrepancy require provenance resolution. Other 100 historical items have unreviewed originality claims. All 110 remain blocked from automatic new approval. New Arena publication is original-only; resolving an adapted item's license does not turn it into an original challenge. New lesson redistribution uses the explicit approved-license policy with pinned upstream identity, notice and permission evidence. Factual-reference use is separate from permission to redistribute. Unknown/contradictory provenance blocks new publication without deleting legacy content/history.

## 9. Source fetching

Development-only fetching enforces enabled/non-reference-only policy, HTTPS, registered host/path scopes, normal port/no credentials, unambiguous URL paths and optional exact URL allowlists. Each redirect and final logical destination is revalidated, with at most five redirects. All resolved addresses must be public; the production transport pins the checked IP while preserving original TLS SNI/Host, avoiding a second uncontrolled DNS destination. Injected clients must be MockTransport clients. Robots policy is required, fetched safely when absent, and checked for each destination; unavailable/disallowed policy fails closed.

Streaming response size is capped at 2 MiB; requests time out. Cache records bind source identity/scope, original/final URL, redirect chain, retained bytes, encoding and SHA-256 and are verified before reuse. Old unverified cache records are not reused by the new cache identity. Live authoring requires one explicit topic and at most eight registered URLs. No runtime fetching, large dataset download, paid provider call or external HTTP request in automated fetch tests was added. DNS, redirects, cache failures and robots restrictions use mocks.

## 10. Verification

Before changes: **173 backend tests passed**, one Starlette/AnyIO deprecation warning, 202.94 seconds. The first two unbounded baseline attempts were stopped after no-progress output; the bounded rerun completed on unchanged source. A separate bounded health test passed. Windows HTTP/child-process tests ran outside the restricted sandbox, still with Gemini disabled, fake-provider enforcement and disposable storage.

All backend commands ran from `apps/api` with `GEMINI_API_KEY=''`, `FORGE_DATABASE_URL='sqlite:///:memory:'`, existing `.venv`, isolated snapshot/backup paths and unique safe pytest directories. Required commands:

```powershell
.\.venv\Scripts\python.exe -m pytest -q --basetemp='C:\My PC\git\Forge\scratch\phase2-release-verification'
.\.venv\Scripts\python.exe -m scripts.course_builder.validate --track python
.\.venv\Scripts\python.exe -m scripts.course_builder.validate --track sql-postgresql
.\.venv\Scripts\python.exe -m scripts.course_builder.validate --track dsa
.\.venv\Scripts\python.exe -m scripts.problem_builder.validate
```

- Full backend suite: **199 passed**, one dependency deprecation warning, **344.42 seconds**, exit 0. After final additive API provenance, release-order and required-revision guards, **50 focused publication/binding/preservation tests passed**, one dependency warning, **117.43 seconds**, exit 0. These focused checks cover the last contract changes after the full-suite process started.

- Final worker capability/EOF/stdin checks: **2 passed**, **1.46 seconds**, exit 0. Final immutable-provenance/idempotency/fresh-restore checks: **3 passed**, **7.12 seconds**, exit 0.
- Existing lesson validators: Python **19**, SQL/PostgreSQL **14**, DSA **20**, all exit 0. These legacy structural/keyword checks are not editorial approvals and do not claim execution of all 258 legacy examples.
- Full problem validator: **111 revisions** (110 historical plus corrected Two Sum), exit 0; exact Python references/typed fixtures and exact SQL objects in real PGlite pass.
- Corrected candidate validator: 10 fixtures and 2 negative solutions pass; report records `approved=false`, `editorial_status=awaiting_human_review`.
- Frontend `npm test`: **23 passed**, 5 files, exit 0.
- `npm run typecheck`: exit 0.
- `npm run build`: exit 0, 3311 transformed modules and five copied Pyodide assets. Existing Pyodide Node-built-in externalization, PGlite eval and >500 kB chunk warnings remain.
- `npm run validate:sql-problems`: **30 passed, 0 failed, 60 datasets**, exit 0.
- `git diff --check`: exit 0, informational LF/CRLF notices only.

Development failures were corrected rather than hidden: first focused run had 43 passed/1 failed (a Windows default-codepage test read fixed to UTF-8); the next focused preservation/publication/judge/migration run passed 68 tests (116.93 seconds). A broader later suite passed 198 tests (360.98 seconds), and the standalone publication suite passed 26 tests (38.66 seconds), including full CLI restoration into a fresh database. An intermediate full run had 193 passed/2 failed because the restricted worker omitted safe `bin`; this was corrected without changing content or weakening the sandbox. The first full problem-validator run exposed the same omission. A sandbox-only candidate probe also encountered denied temporary-directory cleanup; isolated execution succeeded outside that environment. No failed/interrupted run is counted as a pass.

Not run: process-stopping launcher verifier, interactive browser journeys, live model calls, human editorial review or new-content publication into the real learner DB. No configured backend typechecker or frontend lint command exists. This phase does not claim complete offline/browser-WASM verification or blanket content correctness.

## 11. Data preservation evidence

Before/after read-only fingerprints match for **all 32 actual learner tables** and **all 221 historical content/migration files** (217 accepted JSON files plus four frozen migration 1/2 definition/DDL files). Changed tables: **0**. Changed historical files: **0**. The aggregate table fingerprint is identical: `dc239e25515cb6879dc96bf4b88bef1fb71f4767a581434bf23b021a295afb6d`.

Actual stored counts stayed at 6 attempts, 6 mastery evidence events, 5 Arena attempts, 2 curricula, 257 topics and 679 exercises. This comparison checks complete row-payload digests, not just totals.

Synthetic tests retain complete learner row payloads/IDs across migration and repeated startups with revision-1, revision-2 and custom selections. The publication tests preserve original Arena problem/binding identities, scored historical attempt payloads and evidence, keep old/new snapshots concurrently readable, enforce immutability and rollback and prove repeated publication adds no duplicate records. Fresh archive import reconstructs snapshots from a separate store; no developer snapshot copy is required.

The actual learner DB was only read in a consistent read-only transaction for fingerprints. It was not migrated or used as a mutable fixture. Next normal application startup will use the existing backup-first runner to apply any pending numbered migrations. Existing confirmed curriculum files and graphs are unchanged.

## 12. Human review and unverified content

Pending human work:

1. Independently review Two Sum 1.0.1's contract, hints, explanation, complexity, fixtures, coverage and originality. Complete the false-by-default checklist and record a named human review before packaging/publishing.
2. Establish pinned per-item upstream provenance/notices for the nine adaptations; resolve the Celsius discrepancy. Keep them legacy or author new original replacements under separately reviewed identities.
3. Review existing lesson semantics, MCQs, short-answer rubrics, contextual examples and teaching clarity before approving new releases. The 53 historical lessons, 159 MCQs, 212 short answers and 258 examples have not acquired blanket editorial/execution approval.
4. Approve versioned competency specifications for future content. Existing keyword coverage files remain legacy checks; only exact-reference specifications and explicit review can authorize new publication.

The reusable teaching contract covers all nine intended subjects without generating new curriculum content. Unsupported course coding types, arbitrary Python modules, contextual SQL and unstructured problem prose fail closed or require explicit manual review. Human identity is a local attestation, not a cryptographic signature. Future policy changes must version validation/review requirements deliberately and preserve historical release readability.

## 13. Phase 3 prerequisites and stop

The Phase 2 engineering infrastructure is complete with passing verification and no real learner-data migration during testing. Human review remains a content-release blocker, not a reason to invent approval. Phase 3 must remain a separate explicit task: prepare reviewed edition/level metadata and a new nine-subject curriculum draft; preserve both confirmed historical graphs, manual access and history; obtain explicit curriculum confirmation/activation; map only approved content and show missing coverage truthfully. It must not treat curriculum revision 2 as a product edition, infer numeric levels from mastery, copy scores or begin later assessment/Gemini/planner redesign work.

No Phase 3 implementation, commit or push was performed.
