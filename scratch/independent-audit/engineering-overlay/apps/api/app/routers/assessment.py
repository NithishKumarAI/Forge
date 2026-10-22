from fastapi import APIRouter,Depends,HTTPException
from sqlmodel import Session
from sqlalchemy import text
from ..database import get_session
from ..models import AssessmentSelection,Topic
from ..schemas.assessment import AssessmentStart,AssessmentSubmission
from ..services import assessment

router=APIRouter(prefix="/api/assessment",tags=["assessment"])

def _row(session,key):
    row=session.get(AssessmentSelection,key)
    if row is None:raise HTTPException(404,"Assessment not found")
    return row

def _call(fn,*args):
    try:return fn(*args)
    except ValueError as error:
        args[0].rollback()
        raise HTTPException(409,str(error)) from error

@router.post("/start")
def start(request:AssessmentStart,session:Session=Depends(get_session)):
    session.exec(text("BEGIN IMMEDIATE"))
    topic=session.get(Topic,request.topic_id)
    if topic is None:raise HTTPException(404,"Topic not found")
    return _call(assessment.start,session,topic,request.purpose)

@router.get("/{key}")
def read(key:str,session:Session=Depends(get_session)):
    selected=_row(session,key)
    if selected.purpose in {"practice","arena","recall"} and selected.status!="open":_call(assessment.help_guard,session)
    return assessment.public(session,selected)

@router.post("/{key}/submit")
def submit(key:str,request:AssessmentSubmission,session:Session=Depends(get_session)):
    # Serialize local submissions before reading state; repeated requests return the saved result.
    session.exec(text("BEGIN IMMEDIATE"))
    return _call(assessment.submit,session,_row(session,key),request)

@router.post("/{key}/hint")
def hint(key:str,session:Session=Depends(get_session)):
    return _call(assessment.hint,session,_row(session,key))

@router.post("/{key}/give-up")
def reveal(key:str,session:Session=Depends(get_session)):
    return _call(assessment.reveal,session,_row(session,key))
