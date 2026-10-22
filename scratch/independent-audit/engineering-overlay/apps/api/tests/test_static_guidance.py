import json
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlmodel import select
from app import models as m
from app.database import get_session
from app.routers.guidance import router
from app.routers.course import router as course
from app.services.course import sync_course_pack,mark_section,load_lesson_for_topic
from app.services import assessment as a
from tests.assessment_fixtures import item,publish,topic

def client_for(session):
    app=FastAPI();app.include_router(router);app.include_router(course)
    def sessions():yield session
    app.dependency_overrides[get_session]=sessions
    return TestClient(app)

def test_static_search_scoped_exact_revision_and_no_evidence(session):
    sync_course_pack(session);t=topic(session)
    before=session.get(m.LearnerTopicState,t.id).model_dump()
    with client_for(session) as client:
        response=client.get('/api/guidance/search',params={'q':'booleans','topic_id':t.id})
        assert response.status_code==200
        results=response.json()['results'];assert results
        assert all('lesson_id=' in r['url'] and r['curriculum_id']==1 and r['section_slug'] for r in results)
        assert client.get('/api/guidance/search',params={'q':'nonexistentxyz','topic_id':t.id}).json()['results']==[]
    assert session.get(m.LearnerTopicState,t.id).model_dump()==before
    assert not session.exec(select(m.MasteryEvidenceEvent)).all()

def test_help_marks_transfer_assisted_and_preserves_legacy_chat(session):
    t=publish(session,[item(purposes=['transfer'])])
    revision=__import__('app.services.assessment_pool',fromlist=['approved_items']).approved_items(session,t)[0][1]
    selected=a.make_selection(session,t,item(purposes=['transfer']),revision,'approved','transfer');session.commit()
    old=m.ChatMessage(topic_id=t.id,role='assistant',chat_type='doubt',content='Historical explanation')
    session.add(old);session.commit();session.refresh(old);before=old.model_dump()
    with client_for(session) as client:
        assert client.get('/api/guidance/history',params={'topic_id':t.id}).json()[0]['content']=='Historical explanation'
    assert session.get(m.AssessmentSelection,selected.id).assisted
    assert session.get(m.ChatMessage,old.id).model_dump()==before

def test_active_scored_interview_blocks_all_static_help_endpoints(session):
    t=topic(session)
    row=m.InterviewSession(curriculum_id=1,mode='objective',metadata_json='{"engine":"static/1"}')
    session.add(row);session.commit()
    with client_for(session) as client:
        for path in ('/api/guidance/search?q=python','/api/guidance/history',f'/api/course/topics/{t.id}','/api/course/search?q=python'):
            assert client.get(path).status_code==409,path
    assert not session.exec(select(m.MasteryEvidenceEvent)).all()
