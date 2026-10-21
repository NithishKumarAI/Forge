# Approved assessment pools

Runtime pools derive only from the effective Phase 2 reviewed release and its exact curriculum/topic bindings. No synthetic approved items ship in this folder.

Publish `assessment_bundle` candidates through `scripts.content_checks.bundle` and the existing independent human review/release process. A bundle has a stable `assessment/placement-foundations/<subject>/<topic>` identity and immutable version. Items declare `family` (shared across equivalent/reworded variants), `purposes`, `independent_variant`, level, prompt, authored explanation/hints and the validated scoring contract. The reviewed family/purpose classification is an editorial responsibility; changing it changes the candidate digest.

Coding bundles require complete reference fixtures and negative implementations. The validator executes their exact submitted contracts. Never mark a model/agent as an independent human reviewer. Historical legacy practice is not automatically eligible for these pools.
