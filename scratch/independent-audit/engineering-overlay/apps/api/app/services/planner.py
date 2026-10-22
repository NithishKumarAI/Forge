"""Budget-correct advisory plans over reviewed content; no evidence writes."""
import json
from datetime import datetime,timezone
from uuid import uuid4
from zoneinfo import ZoneInfo,ZoneInfoNotFoundError
from sqlmodel import select
from .. import models as m
from .active_curriculum import get_active_curriculum
from .assessment_pool import approved_items,candidates
from .content_publication import release_entries
from .content_registry import load_snapshot,digest
from .mastery import transfer_eligible

DEFAULT_SETTINGS={"daily_study_target":"300","python_daily_minimum":"45","sql_daily_minimum":"30","dsa_daily_minimum":"30","max_review_topics":"10","desired_retention":"0.90","study_timezone":"Asia/Kolkata"}
POLICY="forge-planner/2"


def utc(now):
    return now.replace(tzinfo=timezone.utc) if now.tzinfo is None else now.astimezone(timezone.utc)


def planner_settings(session):
    values={key:(row.value if (row:=session.get(m.AppSetting,key)) else default) for key,default in DEFAULT_SETTINGS.items()}
    return {key:value if key=="study_timezone" else float(value) if key=="desired_retention" else int(value) for key,value in values.items()}


def update_planner_settings(session,values):
    limits={"daily_study_target":(30,480),"python_daily_minimum":(0,180),"sql_daily_minimum":(0,180),"dsa_daily_minimum":(0,120),"max_review_topics":(1,30),"desired_retention":(.70,.97)}
    for key,value in values.items():
        if value is None:continue
        if key=="study_timezone":
            try:ZoneInfo(value)
            except (ZoneInfoNotFoundError,ValueError,TypeError) as error:raise ValueError("Choose an installed IANA timezone, such as Asia/Kolkata or UTC") from error
        elif key not in limits or isinstance(value,bool) or not limits[key][0]<=value<=limits[key][1]:
            raise ValueError("Invalid planner setting: "+key)
        row=session.get(m.AppSetting,key) or m.AppSetting(key=key,value=str(value));row.value=str(value);session.add(row)
    session.commit();return planner_settings(session)


def activities(session,curriculum,now):
    topics=session.exec(select(m.Topic).join(m.Track).where(m.Track.curriculum_id==curriculum.id).order_by(m.Topic.id)).all()
    released=release_entries(session,curriculum_id=curriculum.id)
    result=[]
    for topic in topics:
        track=session.get(m.Track,topic.track_id);state=session.get(m.LearnerTopicState,topic.id)
        placement=session.get(m.TopicPlacement,topic.id)
        mastery=state.mastery_score if state else 0
        links=session.exec(select(m.TopicPrerequisite).where(m.TopicPrerequisite.topic_id==topic.id)).all()
        weak_prerequisites=sum((session.get(m.LearnerTopicState,l.prerequisite_topic_id) or m.LearnerTopicState(topic_id=l.prerequisite_topic_id)).mastery_score<60 for l in links)
        mistakes=session.exec(select(m.Mistake).where(m.Mistake.topic_id==topic.id)).all()
        base={"topic_id":topic.id,"topic_name":topic.name,"subject":track.slug,"track_name":track.name,"level":placement.level if placement else None,
              "rank":(-sum(x.occurrence_count for x in mistakes),weak_prerequisites,mastery,-topic.priority,topic.order_index,topic.id)}
        def add(kind,path,refs,reason,duration=25):
            result.append({**base,"key":str(topic.id)+"/"+kind,"kind":kind,"action_path":path,"references":refs,"reason":reason,"minutes":duration})
        lessons=[r for entry,r in released if entry.topic_id==topic.id and r.content_type=="lesson_bundle"]
        if lessons and mastery<90:
            lesson=lessons[0];payload=load_snapshot(lesson)
            duration=min(45,sum(s["estimated_minutes"] for s in payload["lesson"]["sections"]))
            add("learn",f"/topics/{topic.id}/learn?lesson_id={lesson.id}",[{"id":lesson.id,"sha256":lesson.sha256}],"Read the exact approved lesson; reading does not award mastery.",duration)
        items=approved_items(session,topic)
        practice=[(i,r) for i,r,_ in items if "practice" in i.purposes]
        if practice and mastery<90:
            add("practice",f"/topics/{topic.id}/practice",[{"id":r.id,"sha256":r.sha256,"item_key":i.key} for i,r in practice],
                "Revisit a recorded mistake using approved practice." if mistakes else "Build independent practice evidence; static reflection remains unscored.")
        review=session.get(m.ReviewState,topic.id)
        if review and utc(review.due_at)<=now and candidates(session,topic,"recall",now=now):
            transfer=session.exec(select(m.MasteryEvidenceEvent).where(m.MasteryEvidenceEvent.topic_id==topic.id,m.MasteryEvidenceEvent.event_type=="transfer",m.MasteryEvidenceEvent.score>=75,m.MasteryEvidenceEvent.assisted==False).order_by(m.MasteryEvidenceEvent.created_at.desc())).first()
            if not transfer or (now-utc(transfer.created_at)).total_seconds()>=86400:
                add("review","/review",[{"id":r.id,"sha256":r.sha256,"item_key":i.key} for i,r,_ in candidates(session,topic,"recall",now=now)],"Due FSRS revision; UTC elapsed-time gates still apply.",10)
        if transfer_eligible(session,topic.id) and candidates(session,topic,"transfer",now=now):
            add("transfer",f"/topics/{topic.id}/transfer",[{"id":r.id,"sha256":r.sha256,"item_key":i.key} for i,r,_ in candidates(session,topic,"transfer",now=now)],"An approved unseen transfer variant is available.",25)
    return result


def _entries(session,plan):
    links=session.exec(select(m.StudyPlanEntry).where(m.StudyPlanEntry.plan_id==plan.id)).all()
    return sorted([(link,session.get(m.DailyPlanItem,link.item_id)) for link in links],key=lambda pair:(pair[1].order_index,pair[1].id))


def _new_item(session,plan,activity,minutes,order):
    item=m.DailyPlanItem(plan_date=plan.local_date,curriculum_id=plan.curriculum_id,topic_id=activity["topic_id"],item_type=activity["kind"],reason=activity["reason"],estimated_minutes=minutes,order_index=order)
    session.add(item);session.flush()
    session.add(m.StudyPlanEntry(plan_id=plan.id,item_id=item.id,activity_key=activity["key"],snapshot_json=json.dumps(activity)))
    return item


def _build(session,curriculum,settings,day,now,previous=None):
    retained=[(link,item) for link,item in _entries(session,previous) if item.status in {"completed","skipped"}] if previous else []
    target=settings["daily_study_target"]
    spent=sum(item.estimated_minutes for _,item in retained if item.status=="completed")
    if spent>target:raise ValueError("Completed study already exceeds the new target; retain this plan or choose a target covering completed work")
    if previous:previous.active=False;session.add(previous);session.flush()
    revisions=session.exec(select(m.StudyPlanRevision).where(m.StudyPlanRevision.curriculum_id==curriculum.id,m.StudyPlanRevision.local_date==day,m.StudyPlanRevision.timezone==settings["study_timezone"])).all()
    plan=m.StudyPlanRevision(id=str(uuid4()),curriculum_id=curriculum.id,local_date=day,timezone=settings["study_timezone"],revision=max((p.revision for p in revisions),default=0)+1,target_minutes=target,settings_json=json.dumps(settings))
    session.add(plan);session.flush();used={link.activity_key for link,_ in retained};allocated={}
    for link,item in retained:
        session.add(m.StudyPlanEntry(plan_id=plan.id,item_id=item.id,activity_key=link.activity_key,snapshot_json=link.snapshot_json))
        if item.status=="completed":
            subject=json.loads(link.snapshot_json)["subject"];allocated[subject]=allocated.get(subject,0)+item.estimated_minutes
    pool=activities(session,curriculum,now);remaining=target-spent;order=len(retained)
    cap=max(30,int(target*.35))
    def take(activity,requested=None):
        nonlocal remaining,order
        if activity["key"] in used:return False
        duration=min(activity["minutes"],requested if requested is not None else activity["minutes"],remaining,cap-allocated.get(activity["subject"],0))
        # Reading/practice blocks may be shortened; fewer than five minutes is not
        # presented as a meaningful session. Reviews/transfers keep their fixed slot.
        if duration<5 or activity["kind"] in {"review","transfer"} and duration<activity["minutes"]:return False
        _new_item(session,plan,activity,duration,order);order+=1;used.add(activity["key"])
        remaining-=duration;allocated[activity["subject"]]=allocated.get(activity["subject"],0)+duration
        return True
    review_budget=min(max(10,target//5),settings["max_review_topics"]*10,target)
    for activity in sorted((a for a in pool if a["kind"]=="review"),key=lambda a:a["rank"]):
        if review_budget<10:break
        if take(activity):review_budget-=10
    for subject,setting in [("python","python_daily_minimum"),("sql-postgresql","sql_daily_minimum"),("dsa","dsa_daily_minimum")]:
        minimum=min(settings[setting],target//3,cap)
        for activity in sorted((a for a in pool if a["subject"]==subject),key=lambda a:a["rank"]):
            needed=minimum-allocated.get(subject,0)
            if needed<=0:break
            take(activity,needed)
    subjects=sorted({a["subject"] for a in pool})
    if subjects:
        offset=datetime.fromisoformat(day).toordinal()%len(subjects);subjects=subjects[offset:]+subjects[:offset]
    while remaining>=5:
        changed=False
        for subject in sorted(subjects,key=lambda s:allocated.get(s,0)):
            choices=sorted((a for a in pool if a["subject"]==subject and a["key"] not in used),key=lambda a:a["rank"])
            if any(take(activity) for activity in choices):changed=True
        if not changed:break
    session.commit();return plan


def today_plan(session,*,now=None,regenerate=False):
    now=utc(now or datetime.now(timezone.utc));settings=planner_settings(session)
    day=now.astimezone(ZoneInfo(settings["study_timezone"])).date().isoformat();curriculum=get_active_curriculum(session)
    if not curriculum:return {"date":day,"timezone":settings["study_timezone"],"target_minutes":settings["daily_study_target"],"planned_minutes":0,"scheduled_minutes":0,"completed_minutes":0,"unallocated_minutes":settings["daily_study_target"],"items":[]}
    plan=session.exec(select(m.StudyPlanRevision).where(m.StudyPlanRevision.curriculum_id==curriculum.id,m.StudyPlanRevision.local_date==day,m.StudyPlanRevision.timezone==settings["study_timezone"],m.StudyPlanRevision.active==True)).one_or_none()
    if plan is None or regenerate:plan=_build(session,curriculum,settings,day,now,plan)
    rows=[]
    for order,(link,item) in enumerate(_entries(session,plan)):
        activity=json.loads(link.snapshot_json)
        rows.append({"id":item.id,"topic_id":item.topic_id,"topic_name":activity["topic_name"],"track_name":activity["track_name"],"subject":activity["subject"],"level":activity["level"],"item_type":item.item_type,"reason":item.reason,"estimated_minutes":item.estimated_minutes,"order_index":order,"status":item.status,"action_path":activity["action_path"],"content_references":activity["references"]})
    completed=sum(i["estimated_minutes"] for i in rows if i["status"]=="completed");scheduled=sum(i["estimated_minutes"] for i in rows if i["status"]=="planned")
    return {"id":plan.id,"revision":plan.revision,"policy_version":plan.policy_version,"date":day,"timezone":plan.timezone,"target_minutes":plan.target_minutes,"requested_target_minutes":settings["daily_study_target"],"planned_minutes":completed+scheduled,"scheduled_minutes":scheduled,"completed_minutes":completed,"unallocated_minutes":max(0,plan.target_minutes-completed-scheduled),"settings_changed":digest(settings)!=digest(json.loads(plan.settings_json)),"missing_content_warning":"Unallocated minutes are left free when approved activities or subject diversity are insufficient. Legacy material remains manually accessible.","items":rows}


def set_plan_status(session,item_id,status):
    if status not in {"completed","skipped"}:raise ValueError("Unknown task status")
    item=session.get(m.DailyPlanItem,item_id)
    if item is None:raise ValueError("Plan item not found")
    if item.status in {"completed","skipped"}:
        if item.status!=status:raise ValueError("Completed/skipped decisions are preserved")
        return
    current=today_plan(session)
    if item_id not in {i["id"] for i in current["items"]}:raise ValueError("Choose an item in the current plan")
    item.status=status;session.add(item);session.commit()


def replacement_options(session):
    curriculum=get_active_curriculum(session)
    return activities(session,curriculum,datetime.now(timezone.utc)) if curriculum else []


def replace_item(session,item_id,activity_key):
    current=today_plan(session);plan=session.get(m.StudyPlanRevision,current.get("id"))
    if plan is None:raise ValueError("No current plan")
    entries=_entries(session,plan);old=next((item for _,item in entries if item.id==item_id),None)
    if old is None or old.status!="planned":raise ValueError("Only a planned current task may be replaced")
    activity=next((a for a in replacement_options(session) if a["key"]==activity_key),None)
    if activity is None:raise ValueError("Replacement has no approved available activity")
    if activity_key in {link.activity_key for link,_ in entries}:raise ValueError("That task is already in this plan")
    available=plan.target_minutes-sum(item.estimated_minutes for _,item in entries if item.id!=item_id and item.status!="skipped")
    duration=min(activity["minutes"],available)
    if duration<5 or activity["kind"] in {"transfer","review"} and duration<activity["minutes"]:raise ValueError("Replacement does not fit the remaining budget")
    plan.active=False;session.add(plan);session.flush()
    replacement=m.StudyPlanRevision(id=str(uuid4()),curriculum_id=plan.curriculum_id,local_date=plan.local_date,timezone=plan.timezone,revision=plan.revision+1,target_minutes=plan.target_minutes,settings_json=plan.settings_json)
    session.add(replacement);session.flush()
    for link,item in entries:
        if item.id!=item_id:session.add(m.StudyPlanEntry(plan_id=replacement.id,item_id=item.id,activity_key=link.activity_key,snapshot_json=link.snapshot_json))
    _new_item(session,replacement,activity,duration,old.order_index);session.commit();return today_plan(session)
