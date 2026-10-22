"""Independent negative cases; all records belong to disposable synthetic learners."""
import json
from datetime import datetime,timedelta,timezone

from fastapi.testclient import TestClient
from sqlmodel import select

from app import models as m
from app.database import get_session
from app.main import create_app
from app.schemas.assessment import AssessmentSubmission
from app.services import assessment as a,interview as interviews
from tests.phase5_fixtures import published_scope


def client_for(session):
    app=create_app()
    app.dependency_overrides[get_session]=lambda:session
    # No lifespan: the provided migrated in-memory fixture is authoritative.
    return TestClient(app)


def test_untrusted_web_origin_cannot_create_or_change_a_plan(session):
    client=client_for(session)
    response=client.get('/api/planner/today',headers={'Origin':'https://untrusted.example','Sec-Fetch-Site':'cross-site'})
    assert response.status_code==403
    assert not session.exec(select(m.StudyPlanRevision)).all()
    assert client.post('/api/planner/regenerate',headers={'Origin':'null'}).status_code==403
    assert client.get('/api/planner/today',headers={'Origin':'http://testserver'}).status_code==200


def test_dns_rebinding_host_is_rejected_and_local_browser_is_supported(session):
    client=client_for(session)
    assert client.get('/health',headers={'Host':'rebound.untrusted.example'}).status_code==400
    assert client.get('/health',headers={'Host':'127.0.0.1:18100'}).status_code==200
    assert client.options('/api/planner/regenerate',headers={'Origin':'http://localhost:5173','Access-Control-Request-Method':'POST'}).status_code==200


def test_objective_interview_cannot_commit_a_grade_after_its_deadline(session,monkeypatch):
    published_scope(session,1)
    row=interviews.start_interview(session,'objective')
    question=interviews.questions(session,row)[0];selected=interviews.selection(session,question)
    deadline=a.utc(row.started_at)+timedelta(seconds=1800)
    clock={'now':deadline-timedelta(seconds=1)}
    class TestClock(datetime):
        @classmethod
        def now(cls,tz=None):return clock['now']
    monkeypatch.setattr(a,'datetime',TestClock);monkeypatch.setattr(interviews,'datetime',TestClock)
    def slow_grade(*args):
        clock['now']=deadline+timedelta(seconds=1)
        return True
    monkeypatch.setattr(a,'objective',slow_grade)
    result=interviews.answer(session,row,question.id,AssessmentSubmission(content_sha256=selected.content_sha256,answer=['a']))
    assert result['status']=='completed'
    report=interviews.report_for(session,row.id)
    assert report['time_limit_elapsed'] and report['overall_score']==0
    assert all(q['unanswered'] for q in report['questions'])
    assert not session.exec(select(m.Attempt)).all()
    assert not session.exec(select(m.InterviewResponse)).all()
    assert not session.exec(select(m.MasteryEvidenceEvent)).all()
