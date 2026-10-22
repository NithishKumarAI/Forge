"""Close the local audit evidence without mutating learner data or approving content."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sqlite3
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / 'docs/forge-v1/audit-evidence'


def read(name):
    return json.loads((EVIDENCE / (name + '.json')).read_text(encoding='utf-8'))


def write(name, value):
    (EVIDENCE / (name + '.json')).write_text(json.dumps(value, indent=2) + '\n', encoding='utf-8')


def main():
    before = read('before')
    changed = [name for name, digest in before['files'].items()
               if not (ROOT / name).is_file() or hashlib.sha256((ROOT / name).read_bytes()).hexdigest() != digest]
    connection = sqlite3.connect((ROOT / 'apps/api/data/forge.db').as_uri() + '?mode=ro', uri=True)
    try:
        connection.execute('BEGIN')
        after = {}
        for name in before['db']:
            rows = connection.execute('SELECT * FROM "' + name.replace('"', '""') + '"').fetchall()
            # Same sorted full-row repr fingerprint used in before.json; no raw rows are exported.
            after[name] = {'count': len(rows), 'sha256': hashlib.sha256(json.dumps(sorted(map(repr, rows))).encode()).hexdigest()}
        tables = {row[0] for row in connection.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")}
    finally:
        connection.close()
    changed_tables = [name for name, value in before['db'].items() if value != after[name]]
    new_tables = sorted(tables - set(before['db']))
    human_attestations = []

    def scan(value, path):
        if isinstance(value, dict):
            if value.get('human_attestation') is True:
                human_attestations.append(path)
            for child in value.values():
                scan(child, path)
        elif isinstance(value, list):
            for child in value:
                scan(child, path)

    for path in (ROOT / 'data/content-approvals').rglob('*.json'):
        scan(json.loads(path.read_text(encoding='utf-8')), path.relative_to(ROOT).as_posix())
    assert not changed and not changed_tables and not new_tables and not human_attestations
    head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    assert head == before['head']
    preservation = {
        'verified_at_utc': datetime.now(timezone.utc).isoformat(), 'read_only_database_transaction': True,
        'protected_files_checked': len(before['files']), 'protected_file_mismatches': changed,
        'complete_tables_checked': len(after), 'table_mismatches': changed_tables, 'new_tables': new_tables,
        'after_table_fingerprints': after, 'human_attestation_true_count': len(human_attestations),
        'head_unchanged': True, 'no_raw_learner_rows_exported': True,
        'scratch_policy': 'All disposable audit scratch retained locally and excluded from synchronization; pre-existing Phase4 scratch preserved.',
    }
    write('preservation', preservation)

    sys.path.insert(0, str(ROOT / 'apps/api'))
    from app.schemas.publication import Candidate
    from app.services.content_registry import digest
    queue = json.loads((ROOT / 'data/content-approvals/independent-audit/review-queue.json').read_text(encoding='utf-8'))
    assert queue['approved'] is False and queue['publication_performed'] is False
    for row in queue['candidates']:
        candidate = Candidate.model_validate_json((ROOT / row['candidate']).read_text(encoding='utf-8'))
        expected = digest(candidate.model_dump(mode='json'))
        report = json.loads((ROOT / row['validation']).read_text(encoding='utf-8'))
        copy = read('candidate-validation/independent-audit-' + row['name'])
        packet = (ROOT / 'data/content-approvals/independent-audit/review' / (row['name'] + '.md')).read_text(encoding='utf-8')
        assert expected == row['candidate_sha256'] == report['candidate_sha256'] == copy['candidate_sha256']
        assert expected in packet and report['approved'] is False
    checklist = json.loads((ROOT / 'data/content-approvals/independent-audit/review-checklist.template.json').read_text())
    assert all(value is False for value in checklist.values())

    exits = {}
    for path in EVIDENCE.glob('*.exit'):
        exits[path.stem] = int(path.read_text(encoding='utf-8-sig').strip())
    assert exits['security-red'] != 0 and exits['contracts-red'] != 0
    assert all(value == 0 for key, value in exits.items() if key not in {'security-red', 'contracts-red'})
    browser = read('browser-report')
    extra = read('independent-browser')
    expiry = read('timed-expiry-state')
    assert browser['passed'] == 17 and browser['failed'] == 0
    assert not browser['external_requests'] and not browser['page_errors']
    assert extra['blocked_real_course_journeys'] == 9 and extra['completed_real_course_journeys'] == 0
    assert not extra['external_requests'] and not extra['page_errors']
    assert expiry['status'] == 'passed_actual_elapsed_time' and expiry['restart_preserved_deadline_and_draft']
    summary = {
        'decision': 'A. NOT READY — major engineering or educational blockers',
        'sole_platform_answer': 'No', 'head': head, 'branch': before['branch'],
        'exit_codes': exits, 'backend_release': {'passed': 278, 'warnings': 1, 'seconds': 603.54, 'skipped': 0},
        'frontend': {'passed': 49, 'files': 12, 'seconds': 12.91, 'typecheck_exit': exits['typecheck'], 'build_exit': exits['build']},
        'fresh_python_regressions_passed': 20, 'fresh_node_packages_installed': 220,
        'fresh_node_lifecycle_scripts_enabled': False, 'fresh_node_build_exit': exits['fresh-node-build'],
        'lesson_structural_validation': {'python': 19, 'sql': 14, 'dsa': 20},
        'problem_validator_files': 111, 'sql_bank': {'problems': 30, 'datasets': 60, 'failures': 0},
        'portable_candidates_validated': 24, 'new_correction_digests_and_packets_matched': len(queue['candidates']),
        'human_reviews_or_publications_created': 0,
        'launcher': read('launcher'), 'engine_browser_journeys': {'passed': 17, 'failed': 0},
        'extra_browser_checks': extra['checks'], 'real_course_journeys': {'completed': 0, 'blocked_by_content': 9},
        'actual_elapsed_expiry_with_restart': {'status': expiry['status'], 'seconds_allowed': 900, 'score': expiry['report']['overall_score']},
        'census': read('content-census')['totals'],
        'python_examples': {'attempted': 189, 'matched_stdout': 166, 'context_or_execution_errors': 23},
        'sql_examples': {'attempted': 69, 'executed': 37, 'missing_setup': 32, **read('sql-output-comparisons')['counts']},
        'contract_probes': {'constant_mutants_rejected': 80, 'input_mutation_constraint_bypasses': 4},
        'placement_coverage': read('learning-coverage')['counts'],
        'preservation': {key: preservation[key] for key in ['protected_files_checked', 'protected_file_mismatches', 'complete_tables_checked', 'table_mismatches', 'new_tables', 'head_unchanged']},
        'no_commit_or_push': True, 'offline_scope': 'Browser deny policy plus Python process guard; not a machine-wide firewall or OS sandbox.',
    }
    write('summary', summary)

    sync = read('synchronization')
    original = {row['path']: row for row in sync['files']}
    tracked = set(subprocess.check_output(['git', 'ls-files', '-z'], cwd=ROOT).decode().split('\0'))
    changes = subprocess.check_output(['git', 'diff', '--name-only', '-z', 'HEAD'], cwd=ROOT).decode().split('\0')
    changes += subprocess.check_output(['git', 'ls-files', '--others', '--exclude-standard', '-z', '--', 'apps', 'scripts', 'data', 'docs', 'README.md', 'ARCHITECTURE.md'], cwd=ROOT).decode().split('\0')
    overlay = read('engineering-overlay')['explicit_overlay_paths']
    final = []
    for name in sorted(set(changes) - {''}):
        if name.startswith(('apps/api/.venv/', 'apps/web/node_modules/', 'apps/api/data/', 'scratch/')):
            continue
        if name in original:
            recommendation = original[name]['recommendation']
        elif name.startswith('docs/forge-v1/audit-evidence/'):
            recommendation = 'LOCAL EVIDENCE: inspect and redact private paths/learner-derived metadata before sharing; exclude from engineering commit'
        elif name in overlay:
            recommendation = 'ENGINEERING SYNC: explicit engineering overlay verified; review before inclusion'
        elif name.startswith('data/content-approvals/') or name == 'scripts/prepare_audit_candidates.py' or name.startswith('scripts/audit-') or name in {'scripts/verify_timed_expiry.py'}:
            recommendation = 'KEEP LOCAL: unreviewed content or candidate-dependent harness; exclude from engineering commit'
        else:
            recommendation = 'REVIEW DOCUMENTATION/TOOL: inspect before sharing; not automatically a release requirement'
        path = ROOT / name
        final.append({'path': name, 'status': 'modified' if name in tracked else 'untracked', 'tracked_at_head': name in tracked,
                      'local_sha256': hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else None, 'recommendation': recommendation})
    sync['final_files'] = final
    sync['tested_engineering_only_paths'] = overlay
    sync['manifest_note'] = 'files is the initial inventory; final_files is the closing inventory. Manifests/reports are self-referential and their own raw hashes can change while refreshing the report.'
    write('synchronization', sync)
    report = ROOT / 'docs/forge-v1/PHASE5_SYNCHRONIZATION_REPORT.md'
    text = report.read_text(encoding='utf-8')
    marker = '\n## Final audit additions\n'
    text = text.split(marker)[0]
    text += marker + '\nThe initial inventory above is preserved. The closing inventory below refreshes every changed or untracked source/report path; exact raw digests are in synchronization.json final_files. Self-referential manifest/report hashes require a final packaging refresh. No staging, commit or push occurred. The explicit engineering-only overlay passed without candidate content, secrets or learner data. Audit scratch and evidence remain local.\n\n'
    text += '\n'.join('- `' + row['path'] + '` — ' + row['status'] + '. ' + row['recommendation'] + '.' for row in final) + '\n'
    report.write_text(text, encoding='utf-8')
    print(json.dumps({'protected_files_unchanged': len(before['files']), 'complete_tables_unchanged': len(after), 'new_tables': len(new_tables), 'candidate_digest_checks': len(queue['candidates']), 'exit_markers_checked': len(exits), 'final_inventory_paths': len(final)}))


if __name__ == '__main__':
    main()
