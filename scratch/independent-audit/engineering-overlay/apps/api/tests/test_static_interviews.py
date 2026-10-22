import json
from datetime import timedelta
import pytest
from sqlmodel import select
from app import models as m
from app.schemas.assessment import AssessmentSubmission
from app.services import assessment as a,interview as i
from app.services.content_publication import publish_release
from tests.assessment_fixtures import item,publish,topic

def test_no_approved_objective_pool_creates_no_session(session):
    with pytest.raises(ValueError,match='No approved interview questions'):i.start_interview(session,'objective')
    assert not session.exec(select(m.InterviewSession)).all()
    assert not session.exec(select(m.AssessmentSelection)).all()

def test_reflection_all_prompts_save_resume_complete_no_mastery(session):
    row=i.start_interview(session,'reflection')
    assert len(i.questions(session,row))==7
    i.transition(session,row,'save');assert row.status=='saved'
    i.transition(session,row,'resume');assert row.status=='active'
    for question in i.questions(session,row):
        selected=i.selection(session,question)
        response=i.answer(session,row,question.id,AssessmentSubmission(content_sha256=selected.content_sha256,answer='My honest explanation and a limitation.'))
        assert all(q['assessment']['result'] is None for q in response['questions'])
    report=i.complete_interview(session,row)
    assert report['overall_score'] is None and all(q['score'] is None for q in report['questions'])
    assert not session.exec(select(m.MasteryEvidenceEvent)).all()
    assert i.complete_interview(session,row)==report
    assert len(session.exec(select(m.InterviewReport)).all())==1


@pytest.mark.parametrize('expired',[False,True])
def test_objective_snapshot_weights_feedback_and_legacy_report(session,expired):
    from app.services.curriculum import seed_default_curriculum
    from app.services.active_curriculum import activate_curriculum
    from app.config import settings
    curriculum=seed_default_curriculum(session,settings.curriculum_v2_path);activate_curriculum(session,curriculum)
    entries=[]
    for index,(subject,slug) in enumerate([('python','foundations'),('sql-postgresql','query-basics'),('dsa','arrays')]):
        t=session.exec(select(m.Topic).join(m.Track).where(m.Track.curriculum_id==curriculum.id,m.Track.slug==subject,m.Topic.slug==slug)).one()
        # helper selects default v1 by design; replace the exact target with revision 2 before publication.
        from app.schemas.publication import Candidate
        from app.services.content_registry import digest,database_graph
        from tests.test_content_publication import approved_package
        selected=item('question-'+str(index),purposes=['interview'],subject=subject,topic=slug)
        candidate=Candidate(content_key=f'assessment/placement-foundations/{subject}/{slug}',revision='1',content_type='assessment_bundle',
            payload={'assessment':{'key':f'assessment/placement-foundations/{subject}/{slug}','version':'1','items':[selected.model_dump(mode='json')]}},
            provenance={'origin':'original','author':'TEST ONLY author','sources':[]},coverage={'key':'test','version':'1','competencies':[{'id':'test','status':'covered','lesson_refs':['explanation/'+selected.key],'assessment_refs':['item/'+selected.key]}]})
        package=approved_package(session,candidate,'unused')
        package['entries'][0]['targets']=[{'curriculum_name':curriculum.name,'curriculum_version':2,'graph_sha256':digest(database_graph(session,curriculum)),'topic':subject+'/'+slug}]
        entries.extend(package['entries'])
    publish_release(session,{'format_version':1,'release_id':'objective-test','entries':entries})
    row=i.start_interview(session,'objective');metadata=json.loads(row.metadata_json)
    assert metadata['blueprint']['allowed_seconds']==1800
    assert sum(metadata['weights'])==pytest.approx(1)
    assert all(p['sha256'] and p['revision']=='1' for p in metadata['blueprint']['items'])
    with pytest.raises(ValueError):i.report_for(session,row.id)
    with pytest.raises(ValueError):a.help_guard(session)
    if expired:
        selected=i.selection(session,i.questions(session,row)[0])
        with pytest.raises(ValueError,match='time limit'):
            a.submit(session,selected,AssessmentSubmission(content_sha256=selected.content_sha256,answer='a'),now=a.utc(row.started_at)+timedelta(minutes=31))
        report=i.complete_interview(session,row,now=a.utc(row.started_at)+timedelta(minutes=31))
        assert report['overall_score']==0 and report['time_limit_elapsed']
        assert all(q['unanswered'] for q in report['questions'])
        assert not session.exec(select(m.Attempt)).all() and not session.exec(select(m.MasteryEvidenceEvent)).all()
        return
    for index,question in enumerate(i.questions(session,row)):
        selected=i.selection(session,question)
        with pytest.raises(ValueError):a.reveal(session,selected)
        i.answer(session,row,question.id,AssessmentSubmission(content_sha256=selected.content_sha256,answer='a' if index!=1 else 'b'))
        assert a.public(session,selected)['result'] is None
    report=i.complete_interview(session,row)
    assert report['overall_score']==70
    assert len(report['questions'])==3 and all(q['explanation'] for q in report['questions'])
    assert not session.exec(select(m.MasteryEvidenceEvent)).all()
    legacy=m.InterviewSession(curriculum_id=curriculum.id,mode='unknown-old-mode',status='completed',overall_score=62,metadata_json='{"model":"historical"}')
    session.add(legacy);session.flush();session.add(m.InterviewReport(session_id=legacy.id,report_json='{"overall_score":62,"old":"kept verbatim"}'));session.commit()
    assert i.report_for(session,legacy.id)=={'overall_score':62,'old':'kept verbatim'}
    assert i.interview_read(session,legacy)['read_only']
    with pytest.raises(ValueError):i.transition(session,legacy,'resume')
