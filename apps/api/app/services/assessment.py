"""One version-aware assessment path backed by existing Attempt/evidence/FSRS tables."""
import json
from datetime import datetime,timezone,timedelta
from uuid import uuid4
from sqlmodel import select
from .. import models as m
from ..schemas.assessment import AssessmentItem
from .assessment_pool import candidates
from .content_registry import digest
from .scoring_policy import objective,POLICY_VERSION
from .assessment_judge import judge


def utc(value):return value.replace(tzinfo=timezone.utc) if value.tzinfo is None else value.astimezone(timezone.utc)


def active_scored_interview(session):
    rows=session.exec(select(m.InterviewSession).where(m.InterviewSession.status=="active")).all()
    interview=next((r for r in rows if json.loads(r.metadata_json).get("engine")=="static/1" and r.mode=="objective"),None)
    return interview or session.exec(select(m.TimedTestSession).where(m.TimedTestSession.status=="active")).first()


def help_guard(session,*,commit=True):
    if active_scored_interview(session):raise ValueError("Static help is unavailable during an active scored interview")
    for row in session.exec(select(m.AssessmentSelection).where(m.AssessmentSelection.purpose.in_(["transfer","recall"]),m.AssessmentSelection.status=="open")):
        row.assisted=True;session.add(row)
        session.add(m.AssessmentHelpEvent(selection_id=row.id,kind="static_help"))
    saved={r.id for r in session.exec(select(m.InterviewSession).where(m.InterviewSession.status=="saved",m.InterviewSession.mode=="objective"))
        if json.loads(r.metadata_json).get("engine")=="static/1"}
    for selected in session.exec(select(m.AssessmentSelection).where(m.AssessmentSelection.purpose=="interview",m.AssessmentSelection.status=="open")):
        question=session.get(m.InterviewQuestion,selected.interview_question_id) if selected.interview_question_id else None
        if question and question.session_id in saved:
            selected.assisted=True;session.add(selected);session.add(m.AssessmentHelpEvent(selection_id=selected.id,kind="help_while_saved"))
    if commit:session.commit()
    else:session.flush()


def make_selection(session,topic,item,revision,approval,purpose,*,learning=None,curriculum_id=None,created_at=None):
    created_at=utc(created_at or m.utc_now())
    if topic is None and (item.kind!="reflection" or purpose!="interview" or curriculum_id is None):raise ValueError("Only unscored rehearsal may have no curriculum topic mapping")
    if topic is not None:curriculum_id=session.get(m.Track,topic.track_id).curriculum_id
    if revision and revision.content_type=="arena_problem" and topic is not None:
        placement=session.get(m.TopicPlacement,topic.id)
        item=item.model_copy(update={"subject":session.get(m.Track,topic.track_id).slug,"topic":topic.slug,"level":placement.level if placement else item.level})
    learning=learning or m.LearningSession(topic_id=topic.id if topic else None,mode=purpose,started_at=created_at)
    session.add(learning);session.flush()
    row=m.AssessmentSelection(id=str(uuid4()),session_id=learning.id,curriculum_id=curriculum_id,
        topic_id=topic.id if topic else None,content_revision_id=revision.id if revision else None,content_sha256=revision.sha256 if revision else digest(item.model_dump(mode="json")),
        item_key=item.key,family=item.family,purpose=purpose,approval=approval,snapshot_json=json.dumps(item.model_dump(mode="json")),created_at=created_at)
    helped=session.exec(select(m.AssessmentSelection).where(m.AssessmentSelection.family==item.family,
        (m.AssessmentSelection.revealed==True)|(m.AssessmentSelection.hints_used>0)|(m.AssessmentSelection.assisted==True))).first()
    if helped and purpose!="recall":row.assisted=True
    if item.family.startswith("arena/") and purpose!="recall":
        key=item.family.removeprefix("arena/")
        use=session.get(m.ArenaHintUse,key)
        gave_up=session.exec(select(m.ArenaAttempt).where(m.ArenaAttempt.problem_key==key,m.ArenaAttempt.gave_up==True)).first()
        row.assisted=bool(row.assisted or gave_up or use and use.count)
    session.add(row);session.flush();return row


def start(session,topic,purpose="practice",*,now=None):
    now=utc(now or datetime.now(timezone.utc))
    if active_scored_interview(session):raise ValueError("Complete or save the active interview before another assessment")
    if purpose=="practice":help_guard(session,commit=False)
    curriculum=session.get(m.Curriculum,session.get(m.Track,topic.track_id).curriculum_id)
    if curriculum.status!="confirmed":raise ValueError("Confirm the curriculum before scored study")
    existing=session.exec(select(m.AssessmentSelection).where(m.AssessmentSelection.topic_id==topic.id,
        m.AssessmentSelection.purpose==purpose,m.AssessmentSelection.status=="open").order_by(m.AssessmentSelection.created_at)).first()
    if existing:
        session.commit()
        return public(session,existing)
    if purpose=="transfer":
        from .mastery import transfer_eligible
        if not transfer_eligible(session,topic.id):raise ValueError("More independent approved practice evidence is needed")
    if purpose=="recall":
        due=session.get(m.ReviewState,topic.id)
        if not due or utc(due.due_at)>now:raise ValueError("Recall is not due yet")
        transfer=session.exec(select(m.MasteryEvidenceEvent).where(m.MasteryEvidenceEvent.topic_id==topic.id,
            m.MasteryEvidenceEvent.event_type=="transfer",m.MasteryEvidenceEvent.assisted==False,m.MasteryEvidenceEvent.score>=75)
            .order_by(m.MasteryEvidenceEvent.created_at.desc())).first()
        if transfer and now-utc(transfer.created_at)<timedelta(hours=24):raise ValueError("Recall requires 24 elapsed hours after clean transfer")
    pool=candidates(session,topic,purpose,now=now)
    if not pool:raise ValueError("Transfer pool exhausted: no reviewed unseen independent variant" if purpose=="transfer" else "No approved questions for this context. Read lessons or choose ordinary practice where available.")
    item,revision,approval=pool[0]
    row=make_selection(session,topic,item,revision,approval,purpose,created_at=now);session.commit();return public(session,row)


def feedback_allowed(session,row):
    if active_scored_interview(session):return False
    if row.purpose=="timed":
        from .timed_tests import owner
        return owner(session,row)[0].status=="completed"
    if row.interview_question_id:
        q=session.get(m.InterviewQuestion,row.interview_question_id)
        return session.get(m.InterviewSession,q.session_id).status=="completed"
    return row.status in {"complete","revealed","reflection"}


def public(session,row):
    item=AssessmentItem.model_validate_json(row.snapshot_json)
    c=item.contract
    safe={}
    if item.kind in {"single_choice","multi_choice"}:safe={"choices":c["choices"]}
    elif item.kind=="numeric":safe={k:c[k] for k in ("unit","representation","rounding","boundary")}
    elif item.kind=="python":safe={"starter_code":c["starter_code"],"function_name":c.get("function_name"),"mode":c["mode"],"sample_tests":c.get("sample_tests",[])}
    elif item.kind=="sql":safe={"starter_code":c.get("starter_code","SELECT "),"columns":c["columns"],"ordered":c["ordered"],"public_dataset":{"setup_sql":c["public_dataset"]["setup_sql"]} if c.get("public_dataset") else None}
    elif item.kind=="reflection":safe={"rubric":c["rubric"]}
    result=json.loads(row.result_json) if feedback_allowed(session,row) else None
    return {"id":row.id,"session_id":row.session_id,"topic_id":row.topic_id,"purpose":row.purpose,"kind":item.kind,
        "prompt":item.prompt,"item_key":row.item_key,"content_sha256":row.content_sha256,"status":row.status,
        "approval":row.approval,"assisted":row.assisted,"hints_used":row.hints_used,"hints_available":len(item.hints),
        "contract":safe,"result":result,"policy_version":row.policy_version,"judge_version":row.judge_version}


def hint(session,row):
    if active_scored_interview(session):raise ValueError("Hints are unavailable during an active scored interview")
    if row.status!="open":raise ValueError("Assessment is already completed")
    if row.purpose=="interview":raise ValueError("Hints are unavailable during scored interviews")
    help_guard(session,commit=False)
    item=AssessmentItem.model_validate_json(row.snapshot_json)
    if row.hints_used>=len(item.hints):raise ValueError("No more authored hints")
    value=item.hints[row.hints_used];row.hints_used+=1;row.assisted=True;session.add(row)
    session.add(m.AssessmentHelpEvent(selection_id=row.id,kind="hint"));session.commit()
    return {"text":value,"index":row.hints_used}


def reveal(session,row):
    if active_scored_interview(session):raise ValueError("Answers are unavailable during an active scored interview")
    if row.purpose=="interview" and not feedback_allowed(session,row):raise ValueError("Complete the interview before revealing answers")
    help_guard(session,commit=False)
    item=AssessmentItem.model_validate_json(row.snapshot_json)
    worked=item.contract.get("reference_solution",item.contract.get("correct",item.contract.get("answer",item.contract.get("example"))))
    if row.status=="open":
        row.revealed=True;row.assisted=True;row.status="revealed";row.completed_at=datetime.now(timezone.utc)
        row.result_json=json.dumps({"score":None,"passed":False,"explanation":item.explanation,"worked_answer":worked})
        session.add(row);session.flush()
    if not feedback_allowed(session,row):raise ValueError("Feedback is unavailable")
    session.add(m.AssessmentHelpEvent(selection_id=row.id,kind="solution_reveal"));session.commit()
    return {**json.loads(row.result_json),"worked_answer":worked}


def _credit(session,row,attempt,item,score):
    if row.approval!="approved" or item.kind=="reflection" or row.revealed or row.purpose in {"interview","timed"}:return
    if row.arena_attempt_id and row.assisted:return
    purpose="practice" if row.purpose=="arena" else row.purpose
    due=session.get(m.ReviewState,row.topic_id) if purpose=="recall" else None
    credit_purpose="recall:"+due.due_at.isoformat() if due else purpose
    prior=session.exec(select(m.EvidenceCredit).where(m.EvidenceCredit.topic_id==row.topic_id,m.EvidenceCredit.family==row.family,m.EvidenceCredit.purpose==credit_purpose)).first()
    if row.arena_attempt_id:
        prior=prior or session.exec(select(m.EvidenceCredit).where(m.EvidenceCredit.global_key==row.family)).first()
    # Failed practice can diagnose but never consumes the one passing credit for a family.
    if prior or purpose=="practice" and (score<75 or not attempt.passed):return
    if not session.get(m.EvidencePolicyRecord,row.topic_id):
        state=session.get(m.LearnerTopicState,row.topic_id)
        session.add(m.EvidencePolicyRecord(topic_id=row.topic_id,policy_version=POLICY_VERSION,
            previous_projection_json=json.dumps({"previous_policy":"legacy/unversioned","projection":state.model_dump(mode="json") if state else {},
                "evidence_ids":[e.id for e in session.exec(select(m.MasteryEvidenceEvent).where(m.MasteryEvidenceEvent.topic_id==row.topic_id))]})))
    weights={"single_choice":0.6,"multi_choice":0.6,"numeric":0.8,"python":1.0,"sql":1.0}
    types={"single_choice":"multiple_choice","multi_choice":"multiple_choice","numeric":"numeric","python":"python_code","sql":"sql_code"}
    # Partial coding feedback is not a clean contract pass. Gates/FSRS use the binary contract outcome.
    evidence_score=score if attempt.passed or item.kind not in {"python","sql"} else 0
    event=m.MasteryEvidenceEvent(topic_id=row.topic_id,event_type="arena" if row.arena_attempt_id else purpose,source_attempt_id=attempt.id,
        score=evidence_score,evidence_weight=weights[item.kind]*(0.9**row.hints_used),assisted=row.assisted,
        metadata_json=json.dumps({"policy_version":POLICY_VERSION,"selection_id":row.id,"exercise_type":types[item.kind],
            "verified":True,"contract_passed":attempt.passed,"observed_score":score,"family":row.family,"arena_attempt_id":row.arena_attempt_id}),created_at=attempt.created_at)
    session.add(event);session.flush();session.add(m.EvidenceCredit(selection_id=row.id,topic_id=row.topic_id,family=row.family,purpose=credit_purpose,event_id=event.id,global_key=row.family if row.arena_attempt_id else None))
    return event


def submit(session,row,request,*,now=None,commit=True,allow_timed=False):
    now=utc(now or datetime.now(timezone.utc))
    if row.purpose=="timed":
        if not allow_timed:raise ValueError("Use the timed assessment answer endpoint")
        from .timed_tests import validate_submission
        validate_submission(session,row,now)
    if active_scored_interview(session) and row.purpose not in {"interview","timed"}:raise ValueError("Complete or save the scored interview before other assessments")
    if request.content_sha256!=row.content_sha256:raise ValueError("Stale content revision; reload the selected item")
    if row.status!="open":
        if row.purpose in {"practice","arena","recall"}:help_guard(session,commit=False)
        if commit:session.commit()
        else:session.flush()
        return public(session,row)
    if row.purpose in {"practice","arena"}:help_guard(session,commit=False)
    if row.interview_question_id:
        question=session.get(m.InterviewQuestion,row.interview_question_id)
        interview=session.get(m.InterviewSession,question.session_id)
        if interview.status!="active":raise ValueError("Resume the interview before submitting")
        if interview.mode=="objective":
            allowed=json.loads(interview.metadata_json)["blueprint"]["allowed_seconds"]
            if now-utc(interview.started_at)>=timedelta(seconds=allowed):raise ValueError("Interview time limit elapsed. Complete it to review answered and unanswered questions.")
    item=AssessmentItem.model_validate_json(row.snapshot_json)
    if row.purpose=="recall":
        due=session.get(m.ReviewState,row.topic_id)
        if due is None or utc(due.due_at)>now:raise ValueError("Recall is not due yet")
        transfers=session.exec(select(m.MasteryEvidenceEvent).where(m.MasteryEvidenceEvent.topic_id==row.topic_id,
            m.MasteryEvidenceEvent.event_type=="transfer",m.MasteryEvidenceEvent.score>=75,m.MasteryEvidenceEvent.assisted==False)
            .order_by(m.MasteryEvidenceEvent.created_at.desc())).all()
        if transfers and now-utc(transfers[0].created_at)<timedelta(hours=24):raise ValueError("Recall requires 24 elapsed hours after clean transfer")
    result={"verification":"backend_objective","explanation":item.explanation}
    if item.kind=="reflection":
        if not isinstance(request.answer,str) or not request.answer.strip():raise ValueError("Write a reflection before saving")
        score=None;passed=False;status="reflection";result.update(rubric=item.contract["rubric"],example=item.contract["example"],message="Reflection only; no technical mastery score")
    else:
        if item.kind in {"python","sql"}:
            checked=judge(item,request.source)
            if checked["status"]!="verified":return {**public(session,row),"error":checked.get("reason","Awaiting local verification; no evidence created")}
            passed=checked["passed"]==checked["total"] and checked["total"]>0
            score=round(100*checked["passed"]/checked["total"],1) if checked["total"] else 0
            result.update(verification="backend_bounded_worker",tests_passed=checked["passed"],tests_total=checked["total"])
        else:passed=objective(item,request.answer,request.unit);score=100 if passed else 0
        status="complete"
    attempt=None
    if row.topic_id is not None:
        attempt=m.Attempt(topic_id=row.topic_id,attempt_type=item.kind,score=score or 0,passed=passed,used_hint=row.assisted,created_at=now)
        session.add(attempt);session.flush()
    if score is not None and score<70 and row.purpose not in {"interview","timed"}:
        description="Incorrect objective response in "+item.key
        mistake=session.exec(select(m.Mistake).where(m.Mistake.topic_id==row.topic_id,m.Mistake.category==item.kind,m.Mistake.description==description)).first()
        if mistake:mistake.occurrence_count+=1;mistake.last_seen_at=now
        else:mistake=m.Mistake(topic_id=row.topic_id,category=item.kind,description=description,last_seen_at=now)
        session.add(mistake)
    source_revision=session.get(m.ContentRevision,row.content_revision_id) if row.content_revision_id else None
    if row.purpose=="arena" or source_revision and source_revision.content_type=="arena_problem" and row.purpose=="practice":
        revision=session.get(m.ContentRevision,row.content_revision_id)
        key=revision.content_key.removeprefix("arena/")
        problem=session.get(m.ArenaProblem,key)
        arena=m.ArenaAttempt(problem_key=key,track=problem.track,submitted_source=request.source,score=score or 0,passed=passed,
            hints_used=row.hints_used,result_json=json.dumps(result))
        session.add(arena);session.flush();row.arena_attempt_id=arena.id
        session.add(m.ArenaAttemptContent(attempt_id=arena.id,content_revision_id=revision.id))
    row.attempt_id=attempt.id if attempt else None;row.completed_at=now
    result.update(score=score,passed=passed,assisted=row.assisted,answer=request.source or request.answer,submitted_unit=request.unit)
    row.result_json=json.dumps(result)
    # Append credit before marking the immutable completed snapshot.
    new_credit=_credit(session,row,attempt,item,score or 0) if attempt else None
    row.status=status;session.add(row);session.flush()
    if new_credit:
        from .mastery import recalculate_topic
        if row.purpose=="recall":
            from .review import apply_review
            apply_review(session,row.topic_id,new_credit.score,session_id=row.session_id,attempt_id=attempt.id,assisted=row.assisted,reviewed_at=now,commit=False)
        recalculate_topic(session,row.topic_id,now=now,commit=False)
    if commit:session.commit()
    else:session.flush()
    return public(session,row)
