"""Historical reads; new work uses frozen /api/assessment selections."""
from fastapi import APIRouter,Depends,HTTPException
from sqlmodel import Session
from ..database import get_session
from ..services.practice import practice_history,public_exercise
from ..models import Exercise,LearningSession,PracticeSessionExercise,ExerciseAttemptDetail
from sqlmodel import select
router=APIRouter(prefix="/api/practice",tags=["practice history"])
@router.get("/topics/{topic_id}/history")
def history(topic_id:int,session:Session=Depends(get_session)):
    from ..services.assessment import help_guard
    try:help_guard(session)
    except ValueError as error:raise HTTPException(409,str(error)) from error
    return practice_history(session,topic_id)
@router.get("/exercises/{exercise_id}")
def exercise(exercise_id:int,session:Session=Depends(get_session)):
    row=session.get(Exercise,exercise_id)
    if not row:raise HTTPException(404,"Historical exercise not found")
    return {**public_exercise(row),"approval":"historical_unverified","continuation":"read_only"}

@router.get("/sessions/{session_id}")
def legacy_session(session_id:int,session:Session=Depends(get_session)):
    from ..services.assessment import help_guard
    try:help_guard(session)
    except ValueError as error:raise HTTPException(409,str(error)) from error
    row=session.get(LearningSession,session_id)
    if row is None:raise HTTPException(404,"Historical session not found")
    exercises=[public_exercise(session.get(Exercise,link.exercise_id)) for link in session.exec(select(PracticeSessionExercise).where(PracticeSessionExercise.session_id==session_id))]
    responses=[{"exercise_id":d.exercise_id,"saved_answer":d.answer,"evaluation_status":d.evaluation_status,"grading_source":d.grading_source,"feedback":d.feedback}
        for d in session.exec(select(ExerciseAttemptDetail).where(ExerciseAttemptDetail.session_id==session_id))]
    return {"session_id":row.id,"topic_id":row.topic_id,"mode":row.mode,"read_only":True,"exercises":exercises,"responses":responses}
@router.get("/{path:path}",operation_id="retired_practice_get")
@router.post("/{path:path}",operation_id="retired_practice_post")
@router.put("/{path:path}",operation_id="retired_practice_put")
def retired(path:str):
    raise HTTPException(410,"Use static assessment. Reference validation and generated sessions are retired; history is preserved.")
