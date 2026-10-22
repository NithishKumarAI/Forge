# Forge V1 Phase 1 implementation report

Date: 21 October 2026 (Asia/Calcutta). Baseline: local `main`, HEAD `f1ce096` (`phase 0 audit`), clean working tree before implementation. The existing inaccessible pytest directories were left untouched. No commit or push was made.

## 1. Implemented scope

Phase 1 adds numbered, checked SQLite migrations; consistent pre-upgrade backups and explicit restore-to-new-file tooling; immutable legacy lesson/exercise and Arena snapshots; exact curriculum-scoped mappings; scoped exercise synchronization and search; and safe path configuration. Startup no longer copies learner scores, replays evidence, or switches an existing curriculum selection.

Gemini, its configuration, provider code and grading policy remain in place. The mastery calculation, planner policy, interviews, confirmed curriculum JSON, and accepted educational content were not changed. No edition selector, numeric level navigation, dashboard redesign or new curriculum was added. The Two Sum statement was not modified.

## 2. Exact application/source files

Created:

- `apps/api/app/migrations/__init__.py`
- `apps/api/app/migrations/runner.py`
- `apps/api/app/migrations/v001_legacy_schema.py`
- `apps/api/app/migrations/v002_content_bindings.py`
- `apps/api/app/migrations/legacy_schema.json`
- `apps/api/app/migrations/content_schema.json`
- `apps/api/app/schemas/content_registry.py`
- `apps/api/app/services/content_paths.py`
- `apps/api/app/services/content_registry.py`
- `apps/api/app/services/database_backup.py`
- `apps/api/scripts/database_backup.py`
- `apps/api/tests/phase1_fixtures.py`
- `apps/api/tests/test_database_migrations.py`
- `apps/api/tests/test_content_bindings.py`
- `apps/api/tests/test_data_preservation.py`
- `apps/web/src/services/courseApi.test.ts`
- `data/content-bindings/legacy-curricula.json`
- `docs/forge-v1/PHASE1_IMPLEMENTATION_REPORT.md`

Modified:

- `.gitignore`, `README.md`, `apps/api/.env.example`
- `apps/api/app/config.py`, `apps/api/app/database.py`, `apps/api/app/main.py`
- `apps/api/app/models/entities.py`, `apps/api/app/models/__init__.py`
- `apps/api/app/routers/course.py`, `apps/api/app/routers/arena.py`, `apps/api/app/routers/adaptive.py`
- `apps/api/app/schemas/course.py`
- `apps/api/app/services/course.py`, `apps/api/app/services/arena.py`
- `apps/api/app/services/curriculum_migration.py`, `apps/api/app/services/practice.py`
- `apps/api/tests/conftest.py`, `apps/api/tests/test_arena_curriculum_v2.py`, `apps/api/tests/test_phase2_ai.py`
- `apps/web/src/pages/LearnPage.tsx`, `apps/web/src/services/api.ts`, `apps/web/src/types/course.ts`

Generated Vite/TypeScript/pytest artifacts are not application source. Verification databases and snapshots were confined to disposable locations. Normal snapshot/backup directories are ignored by Git.

## 3. Schema versions and new entities

- **Migration 1, `legacy_schema`:** frozen DDL for the 32 Phase 0 domain tables and indexes. Fresh installation creates that exact schema. An unversioned existing database must already have a compatible legacy schema; it is validated before migration, not dropped/recreated. Initialization guards both ordinary and unique indexes.
- **Migration 2, `content_bindings`:** five additional domain tables and integrity/immutability triggers. `SchemaMigration` is the bootstrap ledger, created transactionally before recording migration 1.

Six new entities:

- `SchemaMigration`: version, name, definition/DDL checksum, application timestamp.
- `ContentRevision`: unique stable key/revision, type, source path, snapshot path, SHA-256, provenance JSON, legacy/approval status, registration timestamp.
- `TopicContentBinding`: curriculum/topic/lesson-revision identity, deterministic order, coverage note, narrowly defined legacy-progress compatibility.
- `ArenaTopicBinding`: exact problem revision and curriculum-scoped topic, or an explicit unresolved reason.
- `CourseExerciseBinding`: stable lesson-revision/topic/exercise-key association to an exercise ID.
- `ContentSectionProgress`: reading state keyed by topic, lesson revision and section slug.

The latter two associations are necessary Phase 1 additions to the conceptual four-entity plan: old exercises lack immutable content identity, and old progress keys cannot distinguish duplicate section slugs across multiple lessons. No existing history table was rebuilt or repurposed.

The runner uses explicit `BEGIN IMMEDIATE`, checks contiguous migration history and definition checksums, rejects newer/partial/incompatible schemas, and rolls back schema DDL plus ledger writes together on failure. Checks include columns, nullability, keys, unique constraints, foreign keys, legacy CHECK expressions and required content triggers. Applied checksums cover each migration's Python definition and frozen JSON DDL; text reads normalize Git CRLF/LF. Runtime migration does not use current SQLModel `create_all()` to infer an upgrade.

New content/binding records cannot be updated or deleted through ordinary SQL. Ownership/type triggers reject cross-curriculum lesson/exercise associations and mismatched Arena revisions. Future changes need an explicit migration/new content identity, rather than editing an applied migration.

## 4. Backup and explicit restore

For a populated/file-backed existing schema needing migration, the runner first reserves writes, then invokes SQLite's consistent backup API through a separate read-only source connection. This includes committed WAL data without blindly copying the main file. It checks destination free space, bounded backup progress, integrity, SHA-256 and table counts. The companion JSON records the pre-upgrade schema version and counts. Backup failure prevents schema/ledger writes. Connections are explicitly closed, including failure paths, for Windows file safety.

Default backup root: `apps/api/data/db-backups`; override with `FORGE_DATABASE_BACKUP_PATH`. Fresh empty and in-memory test databases do not require a learner-file backup. Repeated startup on an unchanged migration version creates no redundant schema backup.

Restore is always explicit and creates a new file. It never stops processes, replaces an existing database or silently changes configuration. With Forge stopped normally, from `apps/api`:

```powershell
.\.venv\Scripts\python.exe -m scripts.database_backup --backup 'C:\My PC\git\Forge\apps\api\data\db-backups\<backup>.sqlite3' --destination 'C:\My PC\git\Forge\apps\api\data\forge-restored.db'
```

Keep the backup's companion `.json`. The command verifies hash, integrity and recorded schema/counts, and rejects existing destination files or sidecars. Inspect the new file, retain the matching immutable content snapshot store, and explicitly change `FORGE_DATABASE_URL` before restarting. A restored pre-upgrade database will be backed up and migrated again. No restore was performed against the actual learner database.

## 5. Content identity and snapshots

All **53 lesson bundles** and **110 Arena problems** are registered as `legacy_baseline`, never editorially approved. Lesson keys are `ai-engineer/v1/<track>/<topic>`; Arena keys are `arena/<original-problem-key>`. Declared content versions remain intact.

Canonical digest convention: SHA-256 over UTF-8 JSON with recursively sorted object keys, compact separators, Unicode retained, nonfinite floats rejected, and no trailing newline. Lesson payloads contain the original lesson object **and** complete static exercise array. Arena payloads contain the complete raw original problem, preserving adaptation/license fields that the existing public Pydantic model does not expose.

Snapshot path: `sha256/<first-two-digest-characters>/<digest>.json` under `apps/api/data/content-snapshots` (or the explicit configured override). Temporary bytes are flushed before atomic, non-replacing publication. Windows uses atomic rename, which refuses an existing target; POSIX uses an exclusive hard link. Each read verifies the exact path/digest, canonical bytes, declared content identity and structured payload. A changed existing key/version fails registration rather than silently overwriting a revision. Missing/corrupt snapshots fail visibly rather than loading mutable source files.

Legacy `content_hash` values are retained verbatim inside snapshots/provenance and existing metadata; newly computed bundle digests are separate. Source-file digests and source references are recorded. Registration is structural preservation, not validation of technical answers or licensing claims.

Relative registry paths reject traversal, absolute/drive paths, backslashes and ambiguous components. File access rejects symlinks/junctions along the path and verifies containment in its configured root. Explicit absolute configuration roots remain supported. Snapshot integrity is not a defense against an administrator rewriting both the database and files.

## 6. Explicit mapping coverage

`legacy-curricula.json` identifies each confirmed curriculum by exact name, revision, source type and a canonical hash of its actual track/topic/prerequisite graph, including seeder defaults. Custom curricula never inherit content from matching slugs. Unmapped topics are enumerated with reasons; missing, duplicate, ambiguous or changed bindings fail explicitly.

**Curriculum revision 1: 160 topics.**

- 47 topics bound to 47 lesson revisions: Python 18, DSA 18, SQL/CS 11.
- 113 topics explicitly unbound; no new graph nodes or invented teaching were created.
- Reviewed aliases include graph-basics/graphs, dynamic-programming-basics/dynamic-programming, legacy SQL topic names, relational relationships/normalization, and SQL/CS Big-O to the existing DSA Big-O lesson. Extra lesson depth does not alter the confirmed competency graph.
- 102 Arena problems bound; 8 remain explicitly unresolved because their declared Python strings/backtracking competencies lack corresponding confirmed topics in this revision.

**Curriculum revision 2: 97 topics.**

- 47 topics bound to 53 ordered lessons: Python 13 topics / 19 lessons, SQL 14 / 14, DSA 20 / 20.
- 50 topics explicitly unbound. These include `python/standard-library` and all topics outside the three static content tracks.
- Required aliases: foundations -> syntax-data-types, stack -> stacks, queue-deque -> queues.
- Explicit Python sequences: exceptions then files; modules/packages then environments; iterators, generators, decorators, typing; debugging then testing. Pythonic programming binds comprehensions; concurrency binds async/await.
- Coverage notes explicitly identify remaining CSV/context-manager, idiom/built-in, dataclass, logging/code-review, and general thread/process/GIL gaps. Binding a partial lesson is not a claim of full consolidated-topic coverage. Standard Library remains unavailable rather than assembled from unrelated fragments.
- All 110 Arena problems have exact bindings. All 17 diagnosed failures are resolved: six stacks mappings (two Python-bank/four DSA-bank) and eleven legacy SQL mappings (four subqueries, two CTE, five aggregation).

The 8 unresolved revision-1 Arena keys are: `python-anagram-check`, `python-bob`, `python-count-vowels`, `python-first-non-repeat`, `python-generate-subsets`, `python-is-palindrome`, `python-longest-common-prefix`, `python-pangram`. Their rationale is stored in the manifest and binding rows. Revision 2 has no unresolved Arena problems. Custom curricula without explicit bindings have no implicit topic assignment; manual Arena access remains available.

Arena evidence creation still uses the existing scoring/evidence policy. It now resolves the current curriculum's binding at submission time, so switching curricula cannot use a stale global mapping cache. Existing problem keys, attempts and historical evidence were not rewritten or duplicated.

## 7. Exercise, search and reading compatibility

Exercise identity is `(topic, immutable lesson revision, exercise key)`. An exact matching old static exercise can be linked without updating its ID or payload. Otherwise a new correctly scoped exercise is appended. Stale historical exercises and their sessions remain intact. New practice/review selection uses current static associations; cached/generated nonstatic behavior and old session access remain supported. Repeated synchronization is idempotent.

The legacy `CourseLesson` table's unique `(topic, content_version)` cannot represent multiple lessons with the same version. It is retained as primary-lesson compatibility metadata without rewriting old rows; ordered bindings are now authoritative. No concatenation of lesson sections occurs.

Existing Learn response fields remain `lesson` and `progress`; additive `lessons` metadata and optional `lesson_id` select an exact bound revision. Learn offers a small lesson selector only for topics with multiple lessons. Section reads, completion and viewing carry the revision ID, and selection changes reset section state. Existing legacy section-progress rows remain unchanged and are read only for the previously readable primary lesson. New bindings and secondary lessons do not inherit completion. New progress is stored separately; reading never changes mastery.

FTS5 uses a separate derived `course_content_fts_v2` index scoped by curriculum/topic/content key/revision/section. Search follows the selected or explicitly contextual curriculum, returns revision-specific lesson URLs, and logs/raises actionable errors if indexing/querying fails. The old derived index is retained, not used as a fallback. Gemini tutor/doubt behavior remains available and continues using the primary static lesson; secondary-lesson tutor state is not redesigned in Phase 1.

## 8. Before/after findings and learner-data safety

Fresh-install comparison against Phase 0:

- Readable active topics: 39 -> 47; stacks/queues aliases and reviewed Python bundles now resolve.
- Active topics missing static exercise association despite readable lessons: 24 -> 0.
- CourseLesson compatibility rows across both curricula: 49 -> 94 primary-topic rows.
- Static exercise rows across both curricula: 343 -> 700 (329 for revision 1, 371 for revision 2).
- Lesson bindings: 100; Arena bindings: 220, including explicit unresolved entries.
- Registered snapshot identities: 163 (53 lesson bundles, 110 problems).

A consistent read-only backup of the actual learner DB was restored into a disposable copy and upgraded/synchronized twice. All pre-existing domain row payloads/IDs were checked, with only ArenaProblem's derived mapped-topic cache allowed to change. Copy results:

- CourseLesson rows: 98 -> 143; old rows retained verbatim.
- Exercise rows: 679 -> 1036; 343 existing matching exercises adopted and 357 appended.
- Attempts remained 6, mastery evidence remained 6, Arena attempts remained 5.
- Active curriculum remained ID 2; unresolved active Arena bindings became 0.
- Repeated migration applied no further versions; repeated sync preserved historical rows and added no duplicate identities.

Independent before/after fingerprints confirmed **no changes to any of the actual learner DB's 32 domain tables** and **no changes to any of 217 accepted JSON files**. The actual learner database was never migrated in verification. Its next normal application startup will perform the backed-up upgrade; no existing Forge process was stopped or restarted.

## 9. Preservation and failure tests

Synthetic legacy fixtures include both confirmed graphs, nonzero learner states, completed and pending answers/details, mastery/Arena evidence, attempts/hints, valid versioned FSRS state and review events, completed plans, reading progress, chats, usage metadata, lineage, exercises/old metadata, transfers, interviews/responses/reports. Exact historical payload checks run across upgrade and two application startups for selections of revision 1, revision 2 and a custom curriculum.

Additional checks cover fresh initialization/startup, repeated migrations/sync, consistent legacy-copy backup/restore, WAL content, corrupted backups, low disk/write failure, interrupted migration rollback including DDL/ledger, modified migration checksums, unsupported newer versions, incompatible columns/CHECKs/triggers, immutable records, ownership, all 53 lessons, ordered multi-lessons, duplicate section slugs, invalid paths/digests, simulated link rejection, source mutation, custom slug collisions, missing coverage, revision-specific HTTP progress, scoped FTS and all 17 repaired Arena mappings.

The test fixture forbids real Gemini construction and isolates snapshot/backup paths. Existing AI tests now explicitly initialize their required static bindings; the legacy curriculum test helper explicitly activates the curriculum it wants instead of relying on an automatic switch.

## 10. Verification commands and results

From `C:\My PC\git\Forge\apps\api`, all commands used the existing virtual environment, `GEMINI_API_KEY=''` and `FORGE_DATABASE_URL='sqlite:///:memory:'`. HTTP tests ran outside the known Windows socket-restricted sandbox. Test databases and snapshot paths were disposable; real provider construction was forbidden.

```powershell
.\.venv\Scripts\python.exe -m pytest -q --basetemp='C:\My PC\git\Forge\scratch\phase1-baseline-20261021'
.\.venv\Scripts\python.exe -m pytest -q --basetemp='C:\My PC\git\Forge\scratch\phase1-final-20261021'
.\.venv\Scripts\python.exe -m scripts.course_builder.validate --track python
.\.venv\Scripts\python.exe -m scripts.course_builder.validate --track sql-postgresql
.\.venv\Scripts\python.exe -m scripts.course_builder.validate --track dsa
.\.venv\Scripts\python.exe -m scripts.problem_builder.validate
```

- Baseline full suite: **137 passed**, 1 dependency warning, 143.55 seconds.
- Final full suite: **173 passed**, 1 dependency deprecation warning, 199.21 seconds, exit 0. This includes all new migration, preservation, fresh-start, binding and configuration cases.
- Course validators: exit 0, Python 19, SQL/PostgreSQL 14, DSA 20 lessons.
- Full problem bank: exit 0, 110 problems including real SQL/PGlite reference checks.

From `C:\My PC\git\Forge\apps\web`:

```powershell
npm test
npm run typecheck
npm run build
npm run validate:sql-problems
```

- Frontend: **23 passed**, 5 files, exit 0.
- Typecheck: exit 0.
- Production build: exit 0, 3311 transformed modules, five copied Pyodide assets. Existing Pyodide Node-built-in externalization, PGlite eval and large-chunk warnings remain; Vite also reported plugin timings. No warning was suppressed.
- SQL: **30 passed, 0 failed, 60 datasets**, exit 0.
- `git diff --check`: exit 0; informational LF/CRLF notices only.

Development checks before the final run: initial focused selection had 37 passing/4 failing tests; three failures identified the unique-index bootstrap bug and one identified an expired-ORM-object test snapshot. Those were corrected; the focused migration/binding/preservation suite then passed 32 tests. A later broader run passed 171 tests (215.22 seconds); a fresh-start HTTP workflow test separately passed. The final run includes the additional fresh-start and CHECK-constraint cases. An early disposable smoke probe also exposed legacy difficulty/rubric schema differences, fixed without editing content. A sandbox hard-link restriction led to using Windows atomic non-replacing rename for snapshot publication. Failed probes are not counted as successful verification.

Not run: the process-stopping launcher verifier, live paid models, browser automation/WASM execution journeys, or Phase 2 content approval/answer review. Worker judging is unchanged and covered by existing deterministic tests and SQL validation. No backend static typechecker or frontend lint command is configured.

## 11. Remaining limits and implementation choices

- Only the exact Phase 0 schema has an unversioned bootstrap path. Unknown older/partial layouts fail explicitly and need a separately reviewed additive migration. No automatic drop/recreate repair exists.
- Schema backup and immutable content snapshots must both be retained for historical content availability. Restore never guesses a snapshot root or overwrites the current learner database. Backups are checked for consistency/integrity, not encrypted or remote.
- Canonical legacy imports are not editorial approvals. Existing answer/output, Two Sum, source/attribution and candidate-promotion validator gaps remain Phase 2 work. Known file hash mismatches remain preserved historical facts.
- Partial/unmapped curricula are explicit; no new subjects or teaching were generated. Custom curricula need deliberate bindings.
- Old unversioned section progress cannot prove which historical lesson bytes were read. Compatibility is limited to the old primary path; new revision-scoped progress prevents future ambiguity.
- The old metadata/search tables remain for preservation. New runtime resolution uses registry/bindings and the scoped derived index. Historic stale exercise rows remain readable through their original sessions, but are excluded from new static selection when not currently bound.
- Arena-to-mastery aggregation and client-result trust limitations are unchanged. Mapping repairs do not replay or manufacture old evidence.
- File containment/link checks and digests prevent accidental unsafe resolution/corruption; they are not a hostile administrator sandbox. Publication assumes ordinary trusted local filesystem operation.

## 12. Phase 2 readiness

The migration, preservation and explicit content-identity foundation is implemented. Phase 2 can build its exact-bundle validation, provenance/approval and immutable publication workflow on these tables/snapshots instead of rewriting learner storage. Its known blockers are content-review and publication-gate work identified in Phase 0, not missing Phase 1 infrastructure.

Phase 1 is complete with passing preservation, migration and synchronization checks. No Phase 2 implementation was performed. Gemini removal, scoring changes, curriculum/edition redesign and new subject content remain later work.
