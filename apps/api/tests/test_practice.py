"""HTTP replacements for retired generated practice; legacy tests remain archived as text."""
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlmodel import select
from app import models as m
from app.database import get_session
from app.routers.assessment import router
from app.routers.practice import router as legacy
from tests.assessment_fixtures import item,publish,topic

def client_for(session):
    app=FastAPI();app.include_router(router);app.include_router(legacy)
    def sessions():yield session
    app.dependency_overrides[get_session]=sessions
    return TestClient(app)

def test_static_http_submit_is_versioned_idempotent_and_cannot_accept_client_score(session):
    t=publish(session,[item()])
    with client_for(session) as client:
        selected=client.post('/api/assessment/start',json={'topic_id':t.id,'purpose':'practice'})
        assert selected.status_code==200,selected.text
        row=selected.json();assert 'correct' not in row['contract']
        assert client.post('/api/assessment/start',json={'topic_id':t.id,'purpose':'practice'}).json()['id']==row['id']
        path='/api/assessment/'+row['id']+'/submit'
        body={'content_sha256':row['content_sha256'],'answer':'a'}
        assert client.post(path,json={**body,'score':100,'passed':True}).status_code==422
        assert client.post(path,json={**body,'content_sha256':'0'*64}).status_code==409
        first=client.post(path,json=body);assert first.status_code==200,first.text
        assert first.json()['result']['score']==100
        assert client.post(path,json=body).json()==first.json()
        assert len(session.exec(select(m.Attempt)).all())==1
        assert len(session.exec(select(m.MasteryEvidenceEvent)).all())==1
        assert client.get('/api/practice/exercises/1/reference-validation').status_code==410
        assert client.get('/api/practice/exercises/1/submission-tests').status_code==410

def test_pending_model_era_answer_stays_readable_and_pending(session):
    t=topic(session);track=session.get(m.Track,t.track_id)
    exercise=m.Exercise(curriculum_id=1,track_id=track.id,topic_id=t.id,exercise_type='short_answer',title='Historic answer',prompt_markdown='Explain your original reasoning',difficulty='working',source='gemini',content_json='{"hints":[],"content":{}}')
    learning=m.LearningSession(topic_id=t.id,mode='practice');session.add_all([exercise,learning]);session.flush()
    attempt=m.Attempt(topic_id=t.id,attempt_type='short_answer',score=0,passed=False);session.add(attempt);session.flush()
    detail=m.ExerciseAttemptDetail(attempt_id=attempt.id,exercise_id=exercise.id,session_id=learning.id,answer='My saved pending answer',grading_source='pending_gemini',evaluation_status='pending')
    session.add_all([detail,m.PracticeSessionExercise(session_id=learning.id,exercise_id=exercise.id,order_index=0)]);session.commit();session.refresh(detail);before=detail.model_dump()
    with client_for(session) as client:
        history=client.get('/api/practice/topics/'+str(t.id)+'/history').json()
        assert history['attempts'][0]['score'] is None
        saved=client.get('/api/practice/sessions/'+str(learning.id)).json()
        assert saved['read_only'] and saved['responses'][0]['saved_answer']=='My saved pending answer'
        assert saved['responses'][0]['evaluation_status']=='pending'
        assert client.post('/api/practice/exercises/'+str(exercise.id)+'/submit/short-answer',json={'session_id':learning.id,'answer':'Changed'}).status_code==410
    assert session.get(m.ExerciseAttemptDetail,attempt.id).model_dump()==before
    assert not session.exec(select(m.MasteryEvidenceEvent)).all()
