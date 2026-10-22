# Independent audit evidence

This directory contains fresh executions from 22 October 2026. It is local evidence, not approved course content. Logs, screenshots and fingerprints can contain local paths or learner-derived metadata; inspect and redact before sharing. No raw learner rows were exported. Synthetic browser approvals never establish real course coverage.

`summary.json` records the final decision, counts and all 24 exit markers. The two intentionally failing red runs are `security-red` and `contracts-red`; the other 22 markers are zero. Structural validator logs without a separate exit marker are listed below. `backend-final.log` is an intermediate run; **backend-release.log is the final result: 278 passed, one upstream warning, 603.54 seconds**.

## Executed evidence map

- `before.json`, `preservation.json`: protected-file digests and all 38 complete real-database table fingerprints, measured through read-only connections. All 229 protected files and all 38 tables match; no new table.
- `synchronization.json`, `engineering-overlay.json`: exact public commit, initial/closing inventories, exclusions and explicit engineering-only overlay. The HEAD archive lacks the Phase5 routes; the overlay starts and satisfies the checked API contracts without candidate material or learner data.
- `backend-baseline.log`: original 271 tests; `security-red.log` and `contracts-red.log`: reproduced defects; `security-green.log`: 16 focused regressions; `backend-release.log`: complete repaired suite.
- `frontend.log`, `typecheck.log`, `build.log`: 49 tests across 12 files, successful typecheck and production build.
- `lessons-python.log`, `lessons-sql.log`, `lessons-dsa.log`: 19/14/20 structural lesson checks. `problem-bank.log`: 111 files, including the unpublished corrected Two Sum. `sql-bank.log`: 30 problems, 60 isolated datasets, zero failures.
- `python-dependencies.log`, `node-dependencies.log`: current dependency integrity; `python-install.log`, `node-install.log`: fresh disposable installs; `fresh-python-tests.log`: 20 focused regressions; `fresh-node-build.log`: copied actual frontend builds with the fresh lockfile install. Node lifecycle scripts were disabled; Python transitive requirements are not fully pinned.
- `launcher.json`, `launcher.log`: 18 isolated Windows lifecycle/identity checks. Normal Forge runtime and data were not accessed.
- `browser-report.json`, `browser.log`: 17 Chromium application journeys on synthetic fixtures, no external requests or page errors. Expected missing-pool conflict responses remain visible in console diagnostics.
- `independent-browser.json`: legacy upgrade, nine real-course journeys blocked by missing approved content, computed mobile focus check, and every authored Python/SQL example attempted in browser workers. The fourth check records all example attempts; it does not declare their failures passed.
- `browser-upgrade-backup.json`: upgrade to schema6 plus verified backup/restore of a synthetic schema0 sentinel.
- `timed-expiry-state.json`, `timed-expiry-start.log`, `timed-expiry-finish.log`: actual 900-second expiry and browser reporting across process restart. One submitted answer counted, one draft did not; 33.33%, two unanswered, timeout.
- `content-census.json`: every legacy lesson, exercise, example and historical coding bank file with exact keys. 53 lessons, 371 unique exercise records, 258 examples, 110 historical problems.
- `contract-probes.json`: 80 rejected constant mutants, four accepted mutation-contract bypasses, tuple/list Two Sum mismatch. Not a comprehensive adversarial proof of judge correctness.
- `sql-output-comparisons.json`: exact table comparisons separated from setup, nondeterminism and driver display issues. `sql-factual-probes.json`, `python-factual-probes.json`: deterministic counterexamples.
- `source-register.json`: explicit primary reference URLs registered before research. `legacy-provenance.json`: independent provenance scan, not rights clearance.
- `candidate-validation/`, `all-candidates.log`: independent validation of all 24 current portable candidates, including five new unapproved audit corrections. Exact digest/packet consistency is checked again by the finalizer.
- `learning-coverage.json`: every one of the 157 authoritative scope IDs, prerequisites, competencies, separate availability/review/publication states and ordered review queue.
- `runtime-scan.json`: supported runtime provider-import scan and redacted frontend secret-pattern scan. Not a general secret, dependency-advisory or sandbox certification.

## Reproduction commands

Run from the stated directory. All testing used scratch databases, snapshots, backups and runtime directories. Do not substitute the real learner database or normal runtime. Re-running the finalizer compares against this audit's fixed baseline and will correctly refuse if the user has subsequently changed protected files or learner data.

From `apps/api`:

```powershell
$env:FORGE_DATABASE_URL='sqlite://'
.venv/Scripts/python.exe -m pytest -q --basetemp='C:\My PC\git\Forge\scratch\independent-audit\pytest-release'
.venv/Scripts/python.exe -m scripts.course_builder.validate --track python
.venv/Scripts/python.exe -m scripts.course_builder.validate --track sql-postgresql
.venv/Scripts/python.exe -m scripts.course_builder.validate --track dsa
.venv/Scripts/python.exe -m scripts.problem_builder.validate
.venv/Scripts/python.exe -m scripts.content_checks.provenance --output ../../docs/forge-v1/audit-evidence/legacy-provenance.json
.venv/Scripts/python.exe -m pip check
```

Use a new empty basetemp when repeating pytest. The disposable fresh Python install used `python -m venv` and `pip install -r apps/api/requirements.txt`, then the security/contracts/database/migration6 test subset (20 cases). Its environment remains under `scratch/independent-audit/dependency-venv`.

From `apps/web`:

```powershell
npm test -- --run
npm run typecheck
npm run build
npm run validate:sql-problems
npm ls --depth=0
```

The fresh Node install copied package.json/package-lock.json into `scratch/independent-audit/node-install`, executed `npm ci --ignore-scripts --no-audit --no-fund`, copied actual frontend sources/configuration, and ran the build there. It did not replace existing dependencies.

From repository root, with the API virtual-environment Python:

```powershell
$py = 'apps/api/.venv/Scripts/python.exe'
$out = 'docs/forge-v1/audit-evidence'
$pw = 'C:\Users\nithi\.cache\codex-runtimes\codex-primary-runtime\dependencies\node\node_modules\playwright'
& $py scripts/audit_content.py --output $out
& $py scripts/audit_contract_probes.py
node scripts/audit_sql_facts.cjs
& $py scripts/audit_coverage.py
& $py scripts/audit_sync_smoke.py
& $py scripts/verify_launcher.py --report "$out/launcher.json"
& $py scripts/verify_independent.py --playwright-module $pw --output $out
& $py scripts/finalize_independent_audit.py
```

The browser orchestrator creates fresh scratch fixtures and uses dedicated loopback ports24000–24049. It invokes `verify-browser.cjs` and `audit-browser.cjs`; their configuration is synthetic only. Its Python network/provider guard and browser external-request denial establish the documented offline scope, not machine-wide isolation.

The separate real elapsed expiry used the orchestrator's explicitly marked synthetic `content` fixture:

```powershell
& $py scripts/verify_timed_expiry.py start --state "$out/timed-expiry-state.json" --fixture-root 'scratch/independent-browser-pqkbx68f/content' --playwright-module $pw
# Finish only after the recorded real UTC deadline; the harness refuses an early claim.
& $py scripts/verify_timed_expiry.py finish --state "$out/timed-expiry-state.json" --playwright-module $pw
```

Candidate generation/validation commands and exact report paths are in each `data/content-approvals/independent-audit/review/*.md` packet. The existing publication CLI's `validate` action was used for fresh reports; **review, package, publish and restore were not used on the real learner database**. Reports and checklist templates do not constitute human approval.

All audit scratch remains local, including fresh installs and synthetic databases. Neither pre-existing scratch nor local changes were cleaned. No commit or push occurred.
