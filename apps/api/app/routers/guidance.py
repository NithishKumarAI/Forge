"""Offline discovery and historical conversations with assessment help guards."""
from fastapi import APIRouter,Depends,HTTPException,Query
from sqlmodel import Session,select
from ..database import get_session
from ..models import ChatMessage,ContentRevision
from ..services.assessment import help_guard
from ..services.course import search_course,CourseError
router=APIRouter(prefix="/api/guidance",tags=["static guidance"])

@router.get("/search")
def search(q:str=Query(min_length=2,max_length=200),topic_id:int|None=None,session:Session=Depends(get_session)):
    try:
        help_guard(session)
        import json
        from ..services.content_registry import load_snapshot
        from ..services.content_publication import release_entries
        effective={(e.topic_id,r.id) for e,r in release_entries(session)}
        results=search_course(session,q,topic_id)
        for value in results:
            revision=session.get(ContentRevision,value["content_revision_id"])
            value["sources"]=load_snapshot(revision)["lesson"]["sources"]
            value["provenance"]=json.loads(revision.provenance_json)
            value["approval"]="approved" if (value["topic_id"],revision.id) in effective else "legacy_unverified"
        return {"results":results,"mode":"static_corpus","message":"Exact authored sections; no generated explanation"}
    except (ValueError,CourseError) as error:raise HTTPException(409,str(error)) from error

@router.get("/history")
def history(topic_id:int|None=None,session:Session=Depends(get_session)):
    try:help_guard(session)
    except ValueError as error:raise HTTPException(409,str(error)) from error
    query=select(ChatMessage).order_by(ChatMessage.id)
    if topic_id is not None:query=query.where(ChatMessage.topic_id==topic_id)
    return [{**r.model_dump(),"historical":True} for r in session.exec(query)]
