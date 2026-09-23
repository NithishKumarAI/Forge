from fastapi import APIRouter,Depends,HTTPException,Query
from sqlmodel import Session
from ..database import get_session
from ..models import ArenaAttempt,ArenaProblem
from ..schemas.arena import ArenaAttemptRequest
from ..services.arena import give_up,list_problems,public_problem,record_attempt,reveal_hint,validation_payload

router=APIRouter(prefix="/api/arena",tags=["arena"])
@router.get("/problems")
def problems(track:str|None=None,difficulty:str|None=None,tag:str|None=None,status:str|None=None,session:Session=Depends(get_session)):return list_problems(session,track,difficulty,tag,status)
@router.get("/problems/{key}")
def problem(key:str,session:Session=Depends(get_session)):
    row=session.get(ArenaProblem,key)
    if not row:raise HTTPException(404,"Arena problem not found")
    return public_problem(session,row)
@router.get("/problems/{key}/validation")
def validation(key:str,session:Session=Depends(get_session)):
    if not session.get(ArenaProblem,key):raise HTTPException(404,"Arena problem not found")
    return validation_payload(key)
@router.post("/problems/{key}/hint")
def hint(key:str,session:Session=Depends(get_session)):
    try:return reveal_hint(session,key)
    except ValueError as exc:raise HTTPException(409,str(exc)) from exc
@router.post("/problems/{key}/submit")
def submit(key:str,request:ArenaAttemptRequest,session:Session=Depends(get_session)):
    try:return record_attempt(session,key,request)
    except ValueError as exc:raise HTTPException(404,str(exc)) from exc
@router.post("/problems/{key}/give-up")
def giveup(key:str,session:Session=Depends(get_session)):
    try:return give_up(session,key)
    except ValueError as exc:raise HTTPException(404,str(exc)) from exc
@router.get("/summary")
def summary(session:Session=Depends(get_session)):
    problems=session.query(ArenaProblem).all();attempts=session.query(ArenaAttempt).all();solved={a.problem_key for a in attempts if a.passed}
    return {"tracks":{t:{"total":sum(p.track==t for p in problems),"solved":sum(p.key in solved and p.track==t for p in problems)} for t in ("python","sql","dsa")},"recent":[{"problem_key":a.problem_key,"track":a.track,"passed":a.passed,"score":a.score,"created_at":a.created_at} for a in sorted(attempts,key=lambda x:x.created_at,reverse=True)[:5]]}
