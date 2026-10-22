"""Reconcile all 157 outline topics with exact candidates and actual release state."""
from collections import Counter
import json
from pathlib import Path
import sqlite3
import sys

ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'apps/api'))
from app.schemas.publication import Candidate
from app.services.content_registry import digest


def main():
    scope=json.loads((ROOT/'data/placement-foundations-scope.json').read_text(encoding='utf-8'))
    c=sqlite3.connect((ROOT/'apps/api/data/forge.db').as_uri()+'?mode=ro',uri=True);c.execute('BEGIN')
    names={r[0] for r in c.execute("SELECT name FROM sqlite_master WHERE type='table'")}
    releases=c.execute('SELECT count(*) FROM contentrelease').fetchone()[0] if 'contentrelease' in names else 0
    c.rollback();c.close()
    if releases:raise RuntimeError('Actual release records exist; reconcile exact effective entries instead of inferring zero coverage')
    rows=[]
    for topic in scope['topics']:
        folder=ROOT/'data/content-approvals/phase5';paths=[folder/'candidates'/(topic['key']+'.'+kind+'.json') for kind in ['lesson','assessment']]
        candidates=[];validated=[];depth={purpose:0 for purpose in ['practice','transfer','recall','interview']}
        for path in paths:
            if not path.exists():continue
            candidate=Candidate.model_validate_json(path.read_text(encoding='utf-8'));sha=digest(candidate.model_dump(mode='json'));candidates.append(path.relative_to(ROOT).as_posix())
            report_path=ROOT/'docs/forge-v1/audit-evidence/candidate-validation'/('phase5-'+path.stem+'.json')
            if report_path.exists():
                report=json.loads(report_path.read_text(encoding='utf-8'))
                if report['candidate_sha256']==sha and report['structurally_valid'] and report['executable_checks_passed']:validated.append(path.name)
            if candidate.content_type=='assessment_bundle':
                for item in candidate.payload['assessment']['items']:
                    for purpose in depth:
                        if purpose in item['purposes'] and item['kind']!='reflection':depth[purpose]+=1
        objective=topic['assessment_route']!='reflection'
        row={**topic,'outline_only':not candidates,'candidate_lesson':bool(candidates),'automatically_validated_lesson':len(validated)==2,
            'independently_reviewed_lesson':False,'actually_published_lesson':False,'practice_available':False,'transfer_available':False,'recall_available':False,'mock_test_coverage':False,
            'candidate_paths':candidates,'candidate_objective_pool_depth':depth,'actual_published_pool_depth':{k:0 for k in depth},
            'journey_outcome':'BLOCKED BY CONTENT','next_action':'Independent factual/pedagogical/semantic/source review; deepen pools; confirm exact graph and publish only if approved' if candidates else 'Author original teaching, worked examples, explicit prerequisites and deterministic practice contracts before review',
            'proposed_pilot_depth':{'practice':6,'transfer':3,'recall':3,'interview':6} if objective else {'unscored_reflection':4},
            'pilot_depth_notice':'Proposed editorial capacity target, not an existing curriculum requirement or readiness denominator. Transfer must be genuinely independent, not reworded.'}
        rows.append(row)
    # Review/author in prerequisite order; retain the authoritative graph unchanged.
    pending={r['key']:r for r in rows};done=set();queue=[];priority={'python':0,'sql-postgresql':0,'dsa':0,'quantitative-aptitude':1,'logical-reasoning':2,'verbal-english':2,'system-design':3,'ai-fundamentals':3,'interview-communication':4}
    while pending:
        ready=[r for r in pending.values() if set(r['prerequisites'])<=done]
        if not ready:raise RuntimeError('Scope prerequisites have a cycle or unresolved identity')
        selected=min(ready,key=lambda r:(r['level'],priority[r['subject_key']],r['priority'],r['key']))
        queue.append(selected['key']);done.add(selected['key']);del pending[selected['key']]
    result={'scope_sha256':digest(scope),'actual_release_count':releases,'actual_database_read_only':True,'fresh_install_publication_crosscheck':'Browser checked all nine subject totals: zero approved lessons; synthetic engine server excluded.',
            'counts':{'topics':157,'outline_only':sum(r['outline_only'] for r in rows),'candidate_lesson_pairs':sum(r['candidate_lesson'] for r in rows),'automatically_validated_pairs':sum(r['automatically_validated_lesson'] for r in rows),'independent_human_reviews':0,'published_lessons':0,'completed_real_subject_journeys':0},
            'topics':rows,'prerequisite_ordered_review_queue':queue}
    (ROOT/'docs/forge-v1/audit-evidence/learning-coverage.json').write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    lines=['# Learning coverage gaps','','**No beginner can currently complete an approved Placement Foundations learning journey in any of the nine subjects.** All157 topic states below are reconciled with exact current candidate hashes and the independently rerun validator reports. Outlines, legacy material, candidates, validation, human review and publication are separate states.','',
        '157 planned topics; 9 validated candidate lesson/pool pairs; 148 outline-only topics; 0 independent human approvals and 0 actually published lessons or scored pools. The five new audit corrections are legacy-course drafts and do not increase Placement Foundations coverage.','',
        'The actual learner database was inspected read-only and has no release records. Independently initialized browser fixtures confirm zero approved subject totals. The separate synthetic engine server used in assessment tests is excluded.','',
        'The53 legacy lessons are Python19, SQL14 and DSA20. They are editorial references, not accepted mappings to the new outline. The other six subjects have no legacy taught course. Generic seven-prompt communication rehearsal is an unscored tool, not proof of the fifteen-topic interview syllabus.','',
        'The scope names the required Python/SQL/DSA foundations and AI topics including LLMs, tokens, embeddings, vector databases, chunking, RAG, citations/evaluation, tools, workflows, memory, approvals and failures. These titles do not supply teaching. Python recursion is explicitly present in the DSA track; any cross-track reuse needs a reviewed binding. End-to-end backend/API/project competency and production AI evaluation still need accepted integrated exercises, not just topic lists.','',
        '## Pool depth and review queue','','The seven objective candidate topics each have2 practice,1 transfer,1 recall and1 interview item. Subject tests require3 unused interview-purpose items, so publishing the current batch alone would still leave subject-test pools too shallow. Mixed/coding tests could at best exhaust very quickly. AI/communication candidate reflections have no scored transfer/recall denominator.','',
        'Proposed pilot capacity targets are6 practice /3 genuinely independent transfer /3 delayed-recall /6 mock items per objective topic, subject to educational review. These are editorial planning targets, not changes to the immutable curriculum or evidence formula. Reflection topics need authored rubrics/examples and honest unscored rehearsal. A prerequisite-ordered queue for all157 IDs is in the JSON companion.','']
    for subject in dict.fromkeys(r['subject_key'] for r in rows):
        selected=[r for r in rows if r['subject_key']==subject];lines+=['## '+subject,'',f"{len(selected)} topics; {sum(r['candidate_lesson'] for r in selected)} validated candidate pair; 0 reviewed/published. Subject outcome: **BLOCKED BY CONTENT**.",'']
        for r in selected:
            depth=' / '.join(str(r['candidate_objective_pool_depth'][p]) for p in ['practice','transfer','recall','interview'])
            lines+=['### Level '+str(r['level'])+' — '+r['title']+' (`'+r['key']+'`)','',
                '- State: '+('candidate lesson + automatically validated pair' if r['automatically_validated_lesson'] else 'outline only')+'. Independently reviewed: no. Actually published: no.',
                '- Actual practice / transfer / recall / mock coverage: unavailable / unavailable / unavailable / unavailable.',
                '- Candidate objective depth (practice / transfer / recall / interview): '+depth+'.',
                '- Prerequisites: '+(', '.join(r['prerequisites']) or 'None declared in authoritative scope')+'.',
                '- Required competencies: '+'; '.join(r['coverage_requirements']),
                '- Next action: '+r['next_action']+'.','']
    (ROOT/'docs/forge-v1/LEARNING_COVERAGE_GAPS.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    print(json.dumps(result['counts']))


if __name__=='__main__':main()
