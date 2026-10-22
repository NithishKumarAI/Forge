"""Static objective interviews and explicitly unscored rehearsal; legacy reports remain raw."""
import json
from datetime import datetime,timezone,timedelta
from sqlmodel import select
from .. import models as m
from ..config import REPO_ROOT
from ..schemas.assessment import AssessmentItem
from . import assessment
from .assessment_pool import approved_items
from .active_curriculum import get_active_curriculum


def blueprint(name):
    value=json.loads((REPO_ROOT/"data/interview-blueprints"/(name+"-v1.json")).read_text(encoding="utf-8"))
    if name=="objective" and (value["version"]!="1" or value["allowed_seconds"]!=1800 or value["scoring_policy"]!="forge-evidence/2"
            or [(s["subject"],s["weight"]) for s in value["slots"]]!=[("python",.4),("sql-postgresql",.3),("dsa",.3)]):
        raise ValueError("Unexpected objective blueprint revision/weights")
    return value

def modes():
    return [{"mode":"objective","title":"Objective technical interview","scored":True},{"mode":"reflection","title":"Communication and project rehearsal","scored":False}]

def static(row):return json.loads(row.metadata_json).get("engine")=="static/1"

def questions(session,row):return session.exec(select(m.InterviewQuestion).where(m.InterviewQuestion.session_id==row.id).order_by(m.InterviewQuestion.order_index)).all()

def selection(session,q):return session.exec(select(m.AssessmentSelection).where(m.AssessmentSelection.interview_question_id==q.id)).one()

def start_interview(session,mode):
    if mode not in {"objective","reflection"}:raise ValueError("Historical modes are read-only; choose a static interview")
    if assessment.active_scored_interview(session):raise ValueError("An objective interview is already active")
    curriculum=get_active_curriculum(session)
    if not curriculum:raise ValueError("Choose a confirmed curriculum")
    b=blueprint(mode)
    chosen=[]
    if mode=="objective":
        topics=session.exec(select(m.Topic).join(m.Track).where(m.Track.curriculum_id==curriculum.id).order_by(m.Topic.id)).all()
        exposed={r.family for r in session.exec(select(m.AssessmentSelection))}
        for slot in b["slots"]:
            pool=[(topic,item,rev) for topic in topics for item,rev,_ in approved_items(session,topic)
                if item.subject==slot["subject"] and "interview" in item.purposes and item.kind!="reflection" and item.family not in exposed]
            if not pool:raise ValueError("No approved interview questions for "+slot["subject"]+"; no session was created")
            chosen.append((*pool[0],slot["weight"],slot["competency"]))
    else:
        for i in b["items"]:
            item=AssessmentItem(key=i["key"],family="reflection/"+i["key"],subject="interview-communication",topic="communication-rehearsal",level=1,
                kind="reflection",purposes=["interview"],prompt=i["prompt"],explanation=i["example"],contract={"rubric":i["rubric"],"example":i["example"]})
            chosen.append((None,item,None,0,i["key"]))
    assessment.help_guard(session)
    snapshot={**b,"items":[{"item_key":item.key,"family":item.family,"content_key":revision.content_key if revision else "reflection/"+item.key,
        "revision":revision.revision if revision else b["version"],"sha256":revision.sha256 if revision else assessment.digest(item.model_dump(mode="json")),
        "weight":weight,"competency":competency} for _,item,revision,weight,competency in chosen]}
    row=m.InterviewSession(curriculum_id=curriculum.id,mode=mode,metadata_json=json.dumps({"engine":"static/1","blueprint":snapshot,"weights":[c[3] for c in chosen]}))
    session.add(row);session.flush()
    for index,(topic,item,revision,weight,competency) in enumerate(chosen):
        selected=assessment.make_selection(session,topic,item,revision,"approved" if revision else "reflection_only","interview",curriculum_id=curriculum.id)
        q=m.InterviewQuestion(session_id=row.id,section=competency,competency=competency,question_type=item.kind,prompt_markdown=item.prompt,
            topic_id=topic.id if topic else None,learning_session_id=selected.session_id,rubric_json=json.dumps({"weight":weight}),order_index=index,generated_by="static/1")
        session.add(q);session.flush();selected.interview_question_id=q.id;session.add(selected)
    session.commit();return row

def interview_read(session,row):
    if not static(row):
        if assessment.active_scored_interview(session):raise ValueError("History details are unavailable during a scored interview")
        responses=[]
        for response in session.exec(select(m.InterviewResponse).join(m.InterviewQuestion).where(m.InterviewQuestion.session_id==row.id)):
            detail=session.get(m.ExerciseAttemptDetail,response.attempt_id) if response.attempt_id else None
            responses.append({**response.model_dump(),"saved_answer":response.response_text if response.response_text is not None else detail.answer if detail else None})
        return {**row.model_dump(),"legacy":True,"read_only":True,"questions":[q.model_dump() for q in questions(session,row)],"responses":responses,"message":"Historical model-generated session. Continuation is unavailable; saved reports remain unchanged."}
    allq=questions(session,row)
    b=json.loads(row.metadata_json)["blueprint"]
    deadline=(assessment.utc(row.started_at)+timedelta(seconds=b["allowed_seconds"])).isoformat() if row.mode=="objective" else None
    return {"id":row.id,"mode":row.mode,"status":row.status,"legacy":False,"deadline_at":deadline,"questions":[{"id":q.id,"competency":q.competency,"assessment":assessment.public(session,selection(session,q))} for q in allq],"blueprint":{k:v for k,v in b.items() if k!="items"}}

def require_active(row):
    if not static(row) or row.status!="active":raise ValueError("This session is not an active static interview")

def answer(session,row,qid,request):
    require_active(row)
    q=session.get(m.InterviewQuestion,qid)
    if not q or q.session_id!=row.id:raise ValueError("Question does not belong to interview")
    selected=selection(session,q)
    result=assessment.submit(session,selected,request,commit=False)
    if result.get("error"):raise ValueError(result["error"])
    finished=assessment.utc(datetime.now(timezone.utc))
    session.refresh(row)
    if row.mode=="objective" and finished>=assessment.utc(row.started_at)+timedelta(seconds=json.loads(row.metadata_json)["blueprint"]["allowed_seconds"]):
        key=row.id
        session.rollback()
        row=session.get(m.InterviewSession,key)
        if row.status=="active":complete_interview(session,row,now=finished)
        return interview_read(session,row)
    if row.status!="active":
        key=row.id
        session.rollback()
        return interview_read(session,session.get(m.InterviewSession,key))
    if selected.status in {"complete","reflection"} and not session.exec(select(m.InterviewResponse).where(m.InterviewResponse.question_id==qid)).first():
        result=json.loads(selected.result_json)
        session.add(m.InterviewResponse(question_id=qid,response_text=str(request.answer or request.source),attempt_id=selected.attempt_id,
            score=result["score"] or 0,evaluation_json=json.dumps({"reflection_only":row.mode=="reflection","selection_id":selected.id})))
        session.commit()
    return interview_read(session,row)

def complete_interview(session,row,*,now=None):
    if row.status=="completed":return report_for(session,row.id)
    require_active(row)
    allq=questions(session,row)
    selected=[selection(session,q) for q in allq]
    now=assessment.utc(now or datetime.now(timezone.utc))
    expired=row.mode=="objective" and now-assessment.utc(row.started_at)>=timedelta(seconds=json.loads(row.metadata_json)["blueprint"]["allowed_seconds"])
    if expired:
        for s in selected:
            if s.status=="open":
                item=AssessmentItem.model_validate_json(s.snapshot_json)
                s.status="expired";s.completed_at=now;s.result_json=json.dumps({"score":0,"passed":False,"unanswered":True,"assisted":s.assisted,"explanation":item.explanation,"verification":"not_answered"})
                session.add(s)
    if any(s.status not in {"complete","reflection","expired"} for s in selected):raise ValueError("Complete every question before requesting feedback")
    weights=json.loads(row.metadata_json)["weights"]
    score=round(sum(json.loads(s.result_json)["score"]*w for s,w in zip(selected,weights)),1) if row.mode=="objective" else None
    data={"label":"Forge Interview Score" if score is not None else "Reflection only","overall_score":score,
        "scoring_policy":"forge-evidence/2","questions":[{"competency":q.competency,**json.loads(s.result_json)} for q,s in zip(allq,selected)],
        "disclaimer":"A curriculum assessment, not hiring probability. Communication reflection never changes technical mastery."}
    data["time_limit_elapsed"]=expired
    data["assisted"]=any(s.assisted for s in selected)
    row.status="completed";row.completed_at=now;row.overall_score=score
    session.add(row);session.add(m.InterviewReport(session_id=row.id,report_json=json.dumps(data)));session.commit();return data

def report_for(session,interview_id):
    if assessment.active_scored_interview(session):raise ValueError("Saved answer reports are unavailable during a scored interview")
    row=session.get(m.InterviewSession,interview_id)
    if static(row) and row.status!="completed":raise ValueError("Complete the entire interview before detailed feedback")
    report=session.exec(select(m.InterviewReport).where(m.InterviewReport.session_id==interview_id)).first()
    if report is None:raise ValueError("No saved report")
    return json.loads(report.report_json)

def history(session,curriculum_id=None):
    query=select(m.InterviewSession).order_by(m.InterviewSession.started_at.desc())
    if curriculum_id:query=query.where(m.InterviewSession.curriculum_id==curriculum_id)
    return [{**r.model_dump(),"title":r.mode,"legacy":not static(r)} for r in session.exec(query)]

def transition(session,row,action):
    if not static(row):raise ValueError("Historical model interviews are read-only")
    if action=="save" and row.status=="active":row.status="saved"
    elif action=="resume" and row.status=="saved":
        if assessment.active_scored_interview(session):raise ValueError("Another scored interview is active")
        row.status="active"
    elif action=="abandon" and row.status in {"active","saved"}:row.status="abandoned"
    else:raise ValueError("Unsupported interview transition")
    session.add(row);session.commit();return interview_read(session,row)
