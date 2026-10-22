# Forge V1 Phase 3 implementation report

Date: 21 October 2026. Baseline: `main` at `da586d1` (`phase 2 done`). The local checkout was clean before implementation. Changes remain uncommitted; nothing was pushed.

## 1. Result and boundaries

Forge now represents a 157-topic Placement Foundations scope across nine subjects and Levels 1–3. Users can preview the scope, explicitly create an editable draft, review its exact graph, confirm it, and separately activate it. Product edition preference is independent of the active curriculum and historical curriculum revision numbers.

This phase adds an outline and navigation, not educational completeness. **All nine Placement Foundations subjects currently lack approved teaching content. All 157 newly outlined topics are planned/unpublished.** No legacy lesson was automatically mapped by title, reclassified as approved, or copied into the new curriculum. Existing Python/SQL/DSA teaching remains accessible through its historical curriculum bindings. No lessons, question banks, real content reviews, releases, or learner evidence were authored by this change. Forge V1 is not interview-ready because this outline exists.

The mandatory Phase 0/1/2 reports, architecture plan, curriculum scope, roadmap and teaching quality checklist were read against the actual implementation. The implementation uses migration 4 and the existing `ContentSectionProgress` table rather than older proposed names.

## 2. Exact file changes

New files:

- `data/editions.json`: validated product editions and nine subject definitions/icons/priorities.
- `data/placement-foundations-scope.json`: versioned, complete topic outline and coverage requirements.
- `apps/api/app/schemas/editions.py`: strict manifest, scope, review and response schemas.
- `apps/api/app/services/editions.py`: explicit draft/review/activation, scope integrity and registry-derived availability.
- `apps/api/app/routers/editions.py`: additive edition APIs.
- `apps/api/app/migrations/v004_editions.py` and `editions_schema.json`: frozen additive DDL and integrity triggers for two tables.
- `apps/api/tests/test_editions.py`: positive, negative, publication, migration and real startup coverage.
- `apps/web/src/types/editions.ts`: frontend edition/placement/availability contracts.
- `apps/web/src/components/EditionLearningPanel.tsx`: edition overview, future-edition information, draft creation and explicit review/activation controls.
- `apps/web/src/components/SubjectLevelNavigation.tsx` and `SubjectLevelNavigation.test.tsx`: reusable subject/level navigation and behavioral/rendered-output tests.
- `apps/web/src/services/editionApi.test.ts`: separate preview, preference, draft, review, confirmation and activation requests.
- This report.

Modified files:

- Backend `main.py`, `migrations/runner.py`, `models/entities.py`, `models/__init__.py`: register additive APIs/models/migration.
- Backend `schemas/publication.py`, `services/content_registry.py`, `services/content_publication.py`: narrow Phase 2 compatibility fixes described below.
- Backend `services/custom_curriculum.py`, `services/active_curriculum.py`: reuse manual draft machinery transactionally and enforce edition review on confirmation/activation.
- Backend `tests/test_database_migrations.py`, `tests/test_content_publication.py`: expect current migration 4; the synthetic publication helper now explicitly selects the default curriculum instead of assuming version 1 is globally unique.
- Frontend `services/api.ts`, `pages/CurriculumPage.tsx`, `pages/CurriculumBuilderPage.tsx`, `pages/TopicPage.tsx`: typed API integration, edition panel, scoped draft editing and truthful topic availability.

`App.tsx`, `LearnPage.tsx` and `types/api.ts` were inspected and need no change. Existing routes, lesson revision selection and historical API contracts are reused. No dependencies were added. Mastery, FSRS, planner, transfer eligibility, interview grading and Arena judges were not changed.

## 3. Edition and scope design

`placement-foundations` is Forge V1, status `preparing`, numeric levels `[1,2,3]`. `advanced-engineering` is Forge V2, status `future`, declared levels `[1,2,3,4,5]`. Strict manifest validation rejects incomplete subjects, duplicate editions, incorrect level ranges and premature advanced-edition availability. Both definitions share the same subject identities and application infrastructure.

`AppSetting.selected_product_edition` stores preference separately from `AppSetting.active_curriculum_id`. Previewing, choosing the product preference, creating a draft and confirming a draft never activate it. Historical `Curriculum.version == 2` is not Forge V2. The future edition endpoint returns no functioning subject catalogue, and its selection endpoint rejects selection. The UI provides a working future-information toggle rather than a dead learning route.

Every scope topic has a globally unique subject-prefixed key, a friendly description, numeric level, learning outcomes, resolved prerequisites, estimated minutes, priority, assessment-route classification, explicit coverage requirements and its intended stable content key. Availability is calculated at runtime from actual curriculum bindings; it is never inferred from a title or coverage keyword. The manifest remains below the existing 200-topic `CurriculumProposal` limit.

| Subject | Level 1 | Level 2 | Level 3 | Total |
| --- | ---: | ---: | ---: | ---: |
| Quantitative Aptitude | 6 | 7 | 5 | 18 |
| Logical Reasoning | 5 | 5 | 5 | 15 |
| Verbal Ability and English | 6 | 6 | 5 | 17 |
| Python Programming | 7 | 8 | 6 | 21 |
| SQL and PostgreSQL | 5 | 7 | 6 | 18 |
| Data Structures and Algorithms | 5 | 8 | 6 | 19 |
| System Design Fundamentals | 5 | 5 | 5 | 15 |
| AI, Generative AI, RAG and Agents | 5 | 7 | 7 | 19 |
| Interview Preparation and Communication | 5 | 5 | 5 | 15 |
| **Total** | **49** | **58** | **50** | **157** |

The outline covers the agreed arithmetic/rates/algebra/data/probability/geometry syllabus; patterns, arrangements and argument reasoning; grammar, comprehension and professional writing; Python programs, collections, modules, errors, testing and intermediate language concepts; SQL querying, joins, CTEs, windows, constraints and transactions; DSA search, collections, trees, graphs, backtracking and elementary DP; practical client/server, HTTP/API, database/cache/queue, reliability and authentication design; and interview explanation, projects, STAR examples, technical communication and reflection.

AI Level 1 covers AI/ML/DL, neural-network intuition, training/inference, generative models and limitations. Level 2 covers tokens/context, structured prompting, embeddings, chunking, vectors, RAG, citations and evaluation. Level 3 covers tools, agent workflows/planning/state/memory, human approval, reliability, architecture choices and failure analysis. Advanced specialization is deferred. Prerequisites are a small validated advisory graph, not blanket level gates. Python, SQL and DSA retain the highest foundational priorities; no planner policy was changed.

## 4. Migration 4 and data model

`EditionCurriculumBinding` binds one curriculum to edition identity, scope version, canonical scope SHA-256, the stored full scope, graph SHA-256, reviewer and review timestamp. Its unique `(edition_key, scope_sha256)` makes repeated creation idempotent, including after confirmation and restart. A changed scope/version creates a separately reviewable curriculum instead of altering a confirmed graph.

`TopicPlacement` stores topic/curriculum/edition/subject identity, integer numeric level and ordering. The topic primary key prevents ambiguous duplicate placements; `(curriculum_id, subject_key, order_index)` is unique. Foreign keys and triggers reject cross-curriculum owners, mismatched subject tracks, unknown subjects, fractional/out-of-range levels and V1 Levels 4–5. Binding identity cannot be reassigned. Edition prerequisites must reference topics in the same curriculum.

Confirmed edition metadata, tracks, topics and prerequisite rows are immutable at the database level. Confirmed curriculum structural identity/status is protected as well. Existing unbound historical curricula retain their prior behavior. Service-level `CurriculumProposal` validation rejects dangling/cyclic prerequisites before draft persistence and again before confirmation. `Topic.target_level` retains its original mastery-target meaning and is never repurposed as numeric content difficulty.

Migration 4 uses the existing atomic runner, ledger checksums, schema verification and backup mechanism. Migration 3-to-4 backup/restore and repeated migration are tested. **Migrations 1–3 and their three frozen DDL manifests are byte-for-byte unchanged.** No reading-progress table was added.

The real learner database was not migrated during verification. The normal application startup will apply pending migrations through the established backup/ledger workflow; tests used disposable databases and snapshots throughout.

## 5. Draft, review, confirmation and activation

1. `GET /api/editions` and `GET /api/editions/placement-foundations` read definitions and show a scope preview without creating rows.
2. `POST /api/editions/placement-foundations/select` saves only the edition preference.
3. `POST /api/editions/placement-foundations/draft` explicitly creates the deterministic `Forge Placement Foundations` custom draft, nine tracks, 157 topics and draft-only placement associations. Repeated requests return the same curriculum. Startup never creates it.
4. The existing draft editor supports names, descriptions, time, priority, topic ordering and prerequisites. The scope's subject/topic membership and numeric level assignments remain authoritative; additions/removals require a new scope version. Draft replacement deletes/rebuilds placements in the same transaction as topic replacement, and rolls back on failure. Drafts with learner activity cannot be replaced.
5. `GET /api/editions/curricula/{id}/review` exposes the current graph digest, complete stored scope, all subject-level groups, outcomes/prerequisites and actual availability. The UI review summary displays subject-level counts, approved/missing lesson counts, a reviewer identity field and two unchecked acknowledgments.
6. `POST /api/editions/curricula/{id}/confirm` requires the exact graph/scope hashes plus explicit scope review and missing-content acknowledgment. Stale review requests fail. Generic curriculum confirmation cannot bypass this requirement. Confirmation fixes the structure; it neither approves teaching nor selects the curriculum.
7. `POST /api/editions/curricula/{id}/activate` is a separate action available after reviewed confirmation. Generic activation also enforces the review guard. Old/custom curriculum selection still works.

No Gemini route participates in this flow. Existing optional custom AI generation remains available in its original workflow. Review names here record the local user's attestation, not an authenticated external editorial identity. Content publication still requires its independent Phase 2 content review.

## 6. Phase 2 compatibility fixes and availability

New lessons may use `forge/placement-foundations/<subject>/<topic>`. Subject membership and a safe topic slug must match the lesson payload, whose `curriculum_key` is `placement-foundations`. Legacy `ai-engineer/v1/...` identities remain unchanged. Revisions remain content-addressed and immutable. Future V2 may bind the same foundational content key/revision rather than rename it; actual V2 curriculum creation is deferred.

`ReleaseTarget` now has an explicit `source_type` (`default` or `custom`) and optional exact `curriculum_id`. Omitted source type still means `default`. Existing release entries remain their original raw package dictionaries, so absent new fields are not silently inserted into archived hash inputs. Default archives retain their original resolution behavior.

Custom publication requires an explicit curriculum ID, exact name/version/source type, confirmed status, exact graph digest and an explicitly reviewed Placement Foundations binding. Arbitrary confirmed custom copies, drafts, missing IDs and graph mismatches are rejected. The existing hash-bound candidate validation, provenance, human content review and immutable snapshot gates remain required. Successful publication in tests uses synthetic review fixtures only; nothing real was approved or published.

Availability uses exact curriculum/topic bindings and the selected release:

- **Approved:** an effective selected reviewed release supplies that lesson revision to that topic.
- **Legacy:** a compatible legacy binding exists without effective release approval.
- **Planned:** no compatible published/bound lesson exists.
- Static course exercise IDs and mapped Arena bindings determine practice availability. Selected release overrides are respected; lesson and practice availability are distinct.
- Reading progress aggregates the compatible revisions using the existing Phase 1 `ContentSectionProgress` calculations and legacy read overlay. No progress writes occur during catalogue reads.

No new topic is automatically matched to a legacy topic by string similarity. Historical lesson selectors, revision-scoped reading progress, Arena attempts, pending AI evaluations and practice history remain intact. The corrected Two Sum 1.0.1 candidate remains unreviewed and unpublished.

## 7. UI and compatibility

The curriculum page adds a Forge V1 overview and nine icon cards above the existing active-curriculum selector and manual tracks. Subject and numeric-level choices are reflected in URL search parameters. Level 2 shows only that subject's Level 2 topics. All confirmed topics remain manually openable regardless of level or prerequisites.

Cards show concise descriptions, estimated study time, honest lesson/practice badges, advisory prerequisite names, compatible reading progress, expandable outcomes/coverage and actual available lesson/practice links. Drafts remain scope previews. Topic pages display level independently of mastery and suppress empty scoped lesson/practice links; their existing mastery/history presentation remains. The draft editor routes scoped confirmation back to the edition review screen. Responsive grids, labeled navigation, pressed/expanded states, native buttons/details/progress and focus styling support keyboard and smaller-screen use.

Existing topic routes and legacy/custom manual navigation remain in place. `LearnPage` and its revision selector were preserved. No Arena worker, tutor grounding, interview help restriction or grading policy changed.

## 8. Data preservation evidence

Before changes, a read-only SQLite transaction recorded complete sorted-row fingerprints and counts for all **32 actual learner tables**, and SHA-256 for **224 historical files** covering accepted lesson/exercise JSON, the entire problem-bank JSON history and frozen migration 1–3 modules/DDL. The final read-only comparison matched every file and every table's complete row fingerprint/count. The actual active curriculum remains **2**, and the two historical curricula remain unchanged. This comparison did not write to or migrate the learner database.

Isolated integration tests additionally cover old revision 1, historical revision 2 and a custom curriculum through repeated startup/upgrades; legacy rows, evidence, progress, pending evaluations and selection remain preserved. A new test runs two real application lifespans around the same scoped draft, asserting one binding, 157 placements, unchanged active selection and no mastery evidence. Browsing/preview tests assert unchanged reading/mastery state.

Pre-existing inaccessible `apps/api/data/pytest-arena-temp` and `pytest-full-temp` directories were left untouched. Only this task's explicitly named disposable scratch directories are cleaned up after verification.

## 9. Executed verification

Backend commands run from `apps/api` with `GEMINI_API_KEY=''`, `FORGE_DATABASE_URL='sqlite:///:memory:'`, existing `.venv`, unique disposable pytest paths, isolated snapshot/backup paths and the existing fake-provider enforcement. Windows local test sockets and isolated validator workers required execution outside the restricted sandbox; this did not grant access to paid providers or target the learner database.

- Pre-change focused publication/migration/curriculum baseline: **45 passed**, 41.82 seconds.
- Full backend `python -m pytest -q`: **214 passed**, 355.87 seconds, exit 0. One existing Starlette/AnyIO deprecation warning. The subsequently added restart test and final guards are covered by the final focused run below.
- Edition suite including real repeated startup: **16 passed**, 26.00 seconds, exit 0.
- Final focused edition/migration/curriculum checks: **35 passed**, 25.50 seconds, exit 0, including the restart test and final manifest/duplicate-placement guards.
- Existing course validators: Python **19**, SQL/PostgreSQL **14**, DSA **20**, all exit 0. These structural checks are not editorial approval or execution of every legacy prose example.
- Full Arena `python -m scripts.problem_builder.validate`: **111 revisions passed**, exit 0, including isolated Python references and exact SQL bundles in PGlite. Two Sum remains unapproved.
- Frontend `npm test`: **30 passed**, seven files, final run 8.95 seconds, exit 0. Includes six subject/level component tests and the separate edition API action test.
- `npm run typecheck`: exit 0; production build also runs `tsc -b`.
- `npm run build`: exit 0, 3312 transformed modules. Existing Pyodide Node built-in externalization, PGlite eval and large chunk warnings remain.
- `npm run validate:sql-problems`: **30 passed, 0 failed, 60 datasets**, exit 0.
- `git diff --check`: exit 0; Git may display informational LF/CRLF normalization notices.

Development failures were investigated rather than counted as passing: the first focused run had 32 passes/two fixture failures (an overly specific rejection-message expectation and a helper assuming version 1 was unique across curriculum names). Both were corrected. The first production build detected a Windows character-encoding error in the edited Topic page; its original UTF-8 source was restored and the narrow UI changes reapplied, then the final tests/build passed.

No live browser end-to-end session, screen-size screenshots, assistive-technology audit or browser worker journey was performed. Frontend navigation verification uses server-rendered HTML and controlled callbacks plus API request tests, not a DOM/browser simulation. HTTP/startup/publication workflows were exercised through FastAPI TestClient and real isolated databases. The launcher verifier was deliberately not run because it can terminate existing processes.

## 10. Limitations and Phase 4 prerequisites

All nine subjects need separately authored or explicitly mapped, independently reviewed and published educational content. Quantitative Aptitude, Logical Reasoning, Verbal/English, System Design, AI/RAG/Agents and Interview/Communication have no approved new course here; Python, SQL and DSA also have no approved Placement Foundations bindings despite their separate legacy content. Reading an outline or opening a topic creates no competence claim.

Before Phase 4, the user must review the scope, explicitly confirm the chosen graph and choose activation when appropriate. Authors must register permitted public references with attribution, resolve legacy coverage/provenance gaps, create accurate lessons and assessment fixtures, execute deterministic examples, obtain independent human content review and publish against the exact confirmed graph through Phase 2. No title-based reuse shortcut is authorized. Two Sum's corrected revision still needs its independent human review/publication.

Draft topic membership and numeric level classifications are versioned scope decisions; changing those requires a new scope/version. Editable draft names, ordering, descriptions and prerequisites do not rewrite the stored scope. Edition browsing currently queries the local registry per topic; this is suitable for the small catalogue and can be batched if measured growth warrants it. Browser accessibility and responsive interaction should be checked in a real browser before release.

Future work must define multi-subject deterministic objective evidence/rubrics and any planner expansion in its own approved phase, retain Python/SQL/DSA priority and free manual access, and preserve the existing mastery caps and delayed-recall requirements. No Level 4/5 authoring, timed company mocks, entitlement infrastructure or Phase 4 implementation is included.
