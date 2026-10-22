from fastapi import APIRouter,Depends,HTTPException
from pydantic import BaseModel
from sqlmodel import Session
from ..database import get_session
from ..models import InterviewSession
from ..schemas.assessment import AssessmentSubmission
from ..services import interview as service
router=APIRouter(prefix="/api/interviews",tags=["static interviews"])
class Start(BaseModel):mode:str
class Answer(AssessmentSubmission):question_id:int

def row(session,key):
    value=session.get(InterviewSession,key)
    if value is None:raise HTTPException(404,"Interview not found")
    return value

def call(fn,*args):
    try:return fn(*args)
    except ValueError as error:raise HTTPException(409,str(error)) from error
@router.get("/modes")
def modes():return service.modes()
@router.post("/start")
def start(request:Start,session:Session=Depends(get_session)):
    return service.interview_read(session,call(service.start_interview,session,request.mode))
@router.get("/history")
def history(session:Session=Depends(get_session)):return service.history(session)
@router.get("/{key}")
def read(key:int,session:Session=Depends(get_session)):return call(service.interview_read,session,row(session,key))
@router.post("/{key}/answer")
def answer(key:int,request:Answer,session:Session=Depends(get_session)):
    return call(service.answer,session,row(session,key),request.question_id,AssessmentSubmission.model_validate(request.model_dump(exclude={"question_id"})))
@router.post("/{key}/complete")
def complete(key:int,session:Session=Depends(get_session)):return call(service.complete_interview,session,row(session,key))
@router.get("/{key}/report")
def report(key:int,session:Session=Depends(get_session)):return call(service.report_for,session,key)
@router.post("/{key}/{action}")
def transition(key:int,action:str,session:Session=Depends(get_session)):return call(service.transition,session,row(session,key),action)
