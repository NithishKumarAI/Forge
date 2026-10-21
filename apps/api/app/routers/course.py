from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session
from ..database import get_session
from ..models import Topic
from ..services.course import CourseError, lesson_choices, load_lesson_for_topic, mark_section, progress, search_course

router = APIRouter(prefix="/api/course", tags=["course"])

def _topic(session, topic_id):
    topic=session.get(Topic,topic_id)
    if not topic: raise HTTPException(404,"Topic not found")
    return topic

@router.get("/topics/{topic_id}")
def lesson(topic_id:int, session:Session=Depends(get_session), lesson_id:int|None=None):
    topic=_topic(session,topic_id)
    try: content=load_lesson_for_topic(session,topic,lesson_id)
    except CourseError as exc: raise HTTPException(404,str(exc)) from exc
    return {"lesson":content,"progress":progress(session,topic,content),"lessons":lesson_choices(session,topic)}

@router.get("/topics/{topic_id}/sections")
def sections(topic_id:int, session:Session=Depends(get_session),lesson_id:int|None=None):
    return lesson(topic_id,session,lesson_id)

@router.get("/topics/{topic_id}/sections/{section_slug}")
def section(topic_id:int,section_slug:str,session:Session=Depends(get_session),lesson_id:int|None=None):
    result=lesson(topic_id,session,lesson_id); found=next((x for x in result["lesson"].sections if x.slug==section_slug),None)
    if not found: raise HTTPException(404,"Lesson section not found")
    return {"section":found,"progress":result["progress"]}

@router.post("/topics/{topic_id}/sections/{section_slug}/view")
def view(topic_id:int,section_slug:str,session:Session=Depends(get_session),lesson_id:int|None=None):
    try:return mark_section(session,_topic(session,topic_id),section_slug,lesson_id=lesson_id)
    except CourseError as exc: raise HTTPException(404,str(exc)) from exc

@router.post("/topics/{topic_id}/sections/{section_slug}/complete")
def complete(topic_id:int,section_slug:str,session:Session=Depends(get_session),lesson_id:int|None=None):
    try:return mark_section(session,_topic(session,topic_id),section_slug,True,lesson_id)
    except CourseError as exc: raise HTTPException(404,str(exc)) from exc

@router.get("/topics/{topic_id}/progress")
def topic_progress(topic_id:int,session:Session=Depends(get_session),lesson_id:int|None=None):
    topic=_topic(session,topic_id)
    try:return progress(session,topic,load_lesson_for_topic(session,topic,lesson_id))
    except CourseError as exc:raise HTTPException(404,str(exc)) from exc

@router.get("/search")
def search(q:str=Query(min_length=2,max_length=200),topic_id:int|None=None,session:Session=Depends(get_session)):
    try:return search_course(session,q,topic_id)
    except CourseError as exc:raise HTTPException(503,str(exc)) from exc
