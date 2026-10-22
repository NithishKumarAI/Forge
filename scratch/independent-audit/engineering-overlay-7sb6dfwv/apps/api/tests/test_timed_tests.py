import json
from datetime import datetime,timezone,timedelta
import pytest
from sqlmodel import select
from app import models as m
from app.services import timed_tests as t,assessment as a
from app.schemas.assessment import AssessmentSubmission
from tests.phase5_fixtures import published_scope


def current(session,key):return session.get(m.TimedTestSession,key)


def body(question,answer='a',source=''):
    return AssessmentSubmission(content_sha256=question['assessment']['content_sha256'],answer=answer,source=source)


def test_missing_pools_and_invalid_blueprints_create_nothing(session):
    with pytest.raises(ValueError,match='No approved'):t.start(session,'subject','python')
    with pytest.raises(ValueError):t.start(session,'level')
    with pytest.raises(ValueError):t.start(session,'subject','unknown')
    assert not session.exec(select(m.TimedTestSession)).all()
    assert not session.exec(select(m.AssessmentSelection)).all()


def test_subject_test_freezes_items_defers_feedback_and_has_no_mastery(session):
    published_scope(session,3)
    value=t.start(session,'subject','python');row=current(session,value['id'])
    assert len(value['questions'])==3 and value['blueprint']['question_count']==3
    assert not any(q['assessment']['result'] for q in value['questions'])
    with pytest.raises(ValueError):t.report(session,row)
    for index,q in enumerate(value['questions']):
        response=t.answer(session,row,q['position'],body(q,'a' if index!=1 else 'b'))
        assert response['report'] is None
        assert all(q['assessment']['result'] is None for q in response['questions'])
    report=t.complete(session,row)
    assert report['overall_score']==66.67 and len(report['questions'])==3
    assert all(q['explanation'] for q in report['questions'])
    assert t.complete(session,row)==report
    assert len(session.exec(select(m.Attempt)).all())==3
    assert not session.exec(select(m.MasteryEvidenceEvent)).all()
    assert not session.exec(select(m.ReviewEvent)).all()


def test_draft_resume_duplicate_submit_and_release_revocation(session):
    published_scope(session,3)
    value=t.start(session,'subject','python');row=current(session,value['id']);question=value['questions'][0]
    request=body(question)
    t.save_draft(session,row,0,request)
    deadline=row.deadline_at
    assert t.read(session,row)['questions'][0]['assessment']['draft']['answer']=='a'
    from app.services.content_publication import transition_release
    transition_release(session,'synthetic-phase5-test','revoked','TEST ONLY','Synthetic revocation during a frozen assessment')
    assert t.read(session,row)['questions'][0]['assessment']['content_sha256']==question['assessment']['content_sha256']
    t.answer(session,row,0,request);t.answer(session,row,0,body(question,'b'))
    assert len(session.exec(select(m.Attempt)).all())==1 and row.deadline_at==deadline
    with pytest.raises(ValueError,match='locked'):t.save_draft(session,row,0,request)


def test_mixed_negative_marking_and_level_subject_diversity(session):
    published_scope(session,3)
    value=t.start(session,'mixed');row=current(session,value['id'])
    for index,q in enumerate(value['questions']):t.answer(session,row,q['position'],body(q,'a' if index<2 else 'b'))
    report=t.complete(session,row)
    assert report['earned_points']==1 and report['overall_score']==16.67
    level=t.start(session,'level',level=1)
    subjects={json.loads(session.get(m.AssessmentSelection,q['assessment']['id']).snapshot_json)['subject'] for q in level['questions']}
    assert len(subjects)>=3


def test_expiry_on_resume_records_unanswered_without_fake_attempts(session):
    published_scope(session,3)
    start=datetime.now(timezone.utc)-timedelta(hours=1)
    value=t.start(session,'subject','python',now=start);row=current(session,value['id'])
    expired=t.read(session,row)
    assert expired['status']=='completed' and expired['report']['completion_reason']=='timeout'
    assert expired['report']['overall_score']==0 and all(q['unanswered'] for q in expired['report']['questions'])
    assert not session.exec(select(m.Attempt)).all()


def test_verification_crossing_deadline_rolls_back_grade_but_keeps_draft(session):
    published_scope(session,3)
    value=t.start(session,'subject','python');row=current(session,value['id']);deadline=a.utc(row.deadline_at)
    times=iter([deadline-timedelta(seconds=1),deadline-timedelta(seconds=1),deadline+timedelta(seconds=1)])
    result=t.answer(session,row,0,body(value['questions'][0]),clock=lambda:next(times))
    assert result['status']=='completed' and result['report']['overall_score']==0
    assert json.loads(session.get(m.TimedTestItem,(row.id,0)).draft_json)['answer']=='a'
    assert not session.exec(select(m.Attempt)).all()


def test_help_generic_submit_and_saved_report_shortcuts_are_blocked(session):
    published_scope(session,4)
    value=t.start(session,'subject','python');row=current(session,value['id'])
    selected=session.get(m.AssessmentSelection,value['questions'][0]['assessment']['id'])
    with pytest.raises(ValueError):a.help_guard(session)
    with pytest.raises(ValueError):a.hint(session,selected)
    with pytest.raises(ValueError):a.reveal(session,selected)
    with pytest.raises(ValueError,match='timed assessment answer'):a.submit(session,selected,body(value['questions'][0]))
    t.complete(session,row)
    t.start(session,'subject','quantitative-aptitude')
    with pytest.raises(ValueError):t.report(session,row)
    with pytest.raises(ValueError):t.read(session,row)
    with pytest.raises(ValueError):t.complete(session,row)


def test_abandon_is_persisted_and_does_not_create_scores_or_evidence(session):
    published_scope(session,3)
    value=t.start(session,'subject','python');row=current(session,value['id'])
    assert t.abandon(session,row)['status']=='abandoned'
    assert t.abandon(session,row)['status']=='abandoned'
    with pytest.raises(ValueError):t.complete(session,row)
    assert not session.exec(select(m.Attempt)).all()
    assert not session.exec(select(m.MasteryEvidenceEvent)).all()


def test_coding_blueprint_executes_python_sql_dsa_and_withholds_references(session):
    curriculum=published_scope(session,1)
    from tests.assessment_fixtures import item
    from tests.test_content_publication import approved_package
    from app.schemas.publication import Candidate
    from app.services.content_registry import digest,database_graph
    from app.services.content_publication import publish_release
    entries=[];sources={}
    for subject in ['python','sql-postgresql','dsa']:
        topic=session.exec(select(m.Topic).join(m.Track).where(m.Track.curriculum_id==curriculum.id,m.Track.slug==subject).order_by(m.Topic.order_index)).first()
        selected=item('test-code-'+subject,kind='sql' if subject=='sql-postgresql' else 'python',purposes=['interview'],subject=subject,topic=topic.slug)
        sources[subject]=selected.contract['reference_solution'];key=f'assessment/placement-foundations/{subject}/{topic.slug}'
        candidate=Candidate(content_key=key,revision='2',content_type='assessment_bundle',payload={'assessment':{'key':key,'version':'2','items':[selected.model_dump(mode='json')]}},provenance={'origin':'original','author':'TEST ONLY','sources':[]},coverage={'key':'test','version':'1','competencies':[{'id':'test','status':'covered','lesson_refs':['explanation/'+selected.key],'assessment_refs':['item/'+selected.key]}]})
        package=approved_package(session,candidate)
        package['entries'][0]['targets']=[{'source_type':'custom','curriculum_id':curriculum.id,'curriculum_name':curriculum.name,'curriculum_version':curriculum.version,'graph_sha256':digest(database_graph(session,curriculum)),'topic':subject+'/'+topic.slug}]
        entries.extend(package['entries'])
    publish_release(session,{'format_version':1,'release_id':'synthetic-coding','entries':entries})
    value=t.start(session,'coding');row=current(session,value['id'])
    assert 'reference_solution' not in json.dumps(value,default=str) and 'hidden_tests' not in json.dumps(value,default=str)
    for q in value['questions']:
        selected=session.get(m.AssessmentSelection,q['assessment']['id']);subject=json.loads(selected.snapshot_json)['subject']
        response=t.answer(session,row,q['position'],body(q,source=sources[subject]))
        assert response['report'] is None
    assert t.complete(session,row)['overall_score']==100
    assert not session.exec(select(m.MasteryEvidenceEvent)).all()
