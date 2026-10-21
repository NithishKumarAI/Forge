import json
from datetime import datetime,timezone
from sqlmodel import select
from app import models as m
from app.schemas.arena import ArenaAttemptRequest
from app.services.mastery import practice_metrics,recalculate_topic,projection_comparison
from app.services.arena import sync_problem_bank,record_attempt,problem_revision
from app.services.content_publication import publish_release
from tests.test_content_publication import approved_package,TWO_SUM
from tests.assessment_fixtures import topic

def test_historical_arena_is_preserved_and_ambiguous_credit_not_guessed(session):
    t=topic(session);sync_problem_bank(session)
    old=m.ArenaAttempt(problem_key='python-normalize-name',track='python',submitted_source='historical code',score=100,passed=True)
    event=m.MasteryEvidenceEvent(topic_id=t.id,event_type='arena',score=100,evidence_weight=1,metadata_json='{"ambiguous_old":true}')
    session.add_all([old,event]);session.commit();session.refresh(old);session.refresh(event);before=(old.model_dump(),event.model_dump())
    assert practice_metrics(session,t.id)['score'] is None
    assert recalculate_topic(session,t.id)['mastery_score']==0
    assert projection_comparison(session,t.id)=={'old_policy':'legacy/unversioned','new_policy':'forge-evidence/2',
        'old_practice_score':None,'new_practice_score':None,'excluded_ambiguous_arena_events':1}
    assert (session.get(m.ArenaAttempt,old.id).model_dump(),session.get(m.MasteryEvidenceEvent,event.id).model_dump())==before

def test_approved_arena_verified_first_solve_counts_once_and_preserves_policy_snapshot(session):
    sync_problem_bank(session)
    from app.config import settings
    from app.services.curriculum import seed_default_curriculum
    from app.services.active_curriculum import activate_curriculum
    from app.services.content_registry import digest,database_graph
    second_curriculum=seed_default_curriculum(session,settings.curriculum_v2_path)
    activate_curriculum(session,session.get(m.Curriculum,1))
    sync_problem_bank(session)
    package=approved_package(session,json.loads(TWO_SUM.read_text()),'test-arena-v2','dsa/hash-maps')
    package['entries'][0]['targets'].append({'curriculum_name':second_curriculum.name,'curriculum_version':2,
        'graph_sha256':digest(database_graph(session,second_curriculum)),'topic':'dsa/hash-maps'})
    publish_release(session,package)
    revision=problem_revision(session,'dsa-two-sum-indices')
    p=json.loads(TWO_SUM.read_text())['payload']['problem']
    request=ArenaAttemptRequest(source=p['reference_solution'],passed=False,score=0,content_revision_id=revision.id)
    first=record_attempt(session,'dsa-two-sum-indices',request)
    assert first['passed'] and first['score']==100
    event=session.exec(select(m.MasteryEvidenceEvent).where(m.MasteryEvidenceEvent.event_type=='arena')).one()
    t=session.get(m.Topic,event.topic_id)
    assert practice_metrics(session,t.id)['score']==100
    assert session.get(m.LearnerTopicState,t.id).mastery_score==79
    assert projection_comparison(session,t.id)['old_practice_score'] is None
    assert projection_comparison(session,t.id)['new_practice_score']==100
    assert session.get(m.EvidencePolicyRecord,t.id).policy_version=='forge-evidence/2'
    assert json.loads(event.metadata_json)['arena_attempt_id']==first['attempt_id']
    record_attempt(session,'dsa-two-sum-indices',request)
    assert len(session.exec(select(m.MasteryEvidenceEvent)).all())==1
    activate_curriculum(session,second_curriculum)
    record_attempt(session,'dsa-two-sum-indices',request)
    assert len(session.exec(select(m.MasteryEvidenceEvent)).all())==1
    assert session.exec(select(m.EvidenceCredit)).one().global_key=='arena/dsa-two-sum-indices'
    wrong=ArenaAttemptRequest(source='def two_sum(nums, target):\n    return [0,0]',passed=True,score=100,content_revision_id=revision.id)
    result=record_attempt(session,'dsa-two-sum-indices',wrong)
    assert not result['passed'] and result['score']<100
    assert len(session.exec(select(m.MasteryEvidenceEvent)).all())==1
