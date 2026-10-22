from fastapi import APIRouter,Depends,HTTPException
from sqlalchemy import text
from sqlmodel import Session,select
from ..database import get_session
from ..models import TimedTestSession
from ..schemas.timed_tests import TimedStart,TimedAnswer
from ..schemas.assessment import AssessmentSubmission
from ..services import timed_tests as service

router=APIRouter(prefix='/api/timed-tests',tags=['timed tests'])


def row(session,key):
    value=session.get(TimedTestSession,key)
    if value is None:raise HTTPException(404,'Timed assessment not found')
    return value


def call(session,fn,*args):
    try:return fn(session,*args)
    except ValueError as error:
        session.rollback();raise HTTPException(409,str(error)) from error


@router.get('/blueprints')
def blueprints():
    return {kind:service.blueprint(kind,'python' if kind=='subject' else None,1 if kind=='level' else None) for kind in ['subject','level','mixed','coding']}


@router.get('/history')
def history(session:Session=Depends(get_session)):
    return [{'id':r.id,'status':r.status,'started_at':r.started_at,'deadline_at':r.deadline_at} for r in session.exec(select(TimedTestSession).order_by(TimedTestSession.started_at.desc())).all()]


@router.post('/start')
def start(request:TimedStart,session:Session=Depends(get_session)):
    session.exec(text('BEGIN IMMEDIATE'))
    return call(session,service.start,request.kind,request.subject,request.level)


@router.get('/{key}')
def read(key:str,session:Session=Depends(get_session)):
    return call(session,service.read,row(session,key))


@router.post('/{key}/draft')
def draft(key:str,request:TimedAnswer,session:Session=Depends(get_session)):
    body=AssessmentSubmission.model_validate(request.model_dump(exclude={'position'}))
    return call(session,service.save_draft,row(session,key),request.position,body)


@router.post('/{key}/answer')
def answer(key:str,request:TimedAnswer,session:Session=Depends(get_session)):
    body=AssessmentSubmission.model_validate(request.model_dump(exclude={'position'}))
    return call(session,service.answer,row(session,key),request.position,body)


@router.post('/{key}/complete')
def complete(key:str,session:Session=Depends(get_session)):
    session.exec(text('BEGIN IMMEDIATE'))
    return call(session,service.complete,row(session,key))


@router.post('/{key}/abandon')
def abandon(key:str,session:Session=Depends(get_session)):
    return call(session,service.abandon,row(session,key))


@router.get('/{key}/report')
def report(key:str,session:Session=Depends(get_session)):
    return call(session,service.report,row(session,key))
