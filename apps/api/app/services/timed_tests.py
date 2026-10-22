"""Fixed static timed assessments. Reports are not mastery or hiring probability."""
import json
from datetime import datetime,timedelta,timezone
from uuid import uuid4
from sqlalchemy.exc import IntegrityError
from sqlmodel import select
from .. import models as m
from ..config import REPO_ROOT
from ..schemas.assessment import AssessmentSubmission,AssessmentItem
from .active_curriculum import get_active_curriculum
from .assessment_pool import approved_items
from . import assessment


def blueprint(kind,subject=None,level=None):
    templates=json.loads((REPO_ROOT/'data/timed-test-blueprints/v1.json').read_text(encoding='utf-8'))['templates']
    if kind not in templates:raise ValueError('Unknown test blueprint')
    from ..schemas.editions import SUBJECT_KEYS
    if subject is not None and subject not in SUBJECT_KEYS:raise ValueError('Unknown subject')
    if kind=='subject' and subject is None:raise ValueError('Choose a subject')
    if kind=='level' and level is None:raise ValueError('Choose a level')
    if level is not None and (type(level) is not int or not 1<=level<=3):raise ValueError('Forge V1 supports levels 1–3')
    if kind in {'mixed','coding'} and subject is not None:raise ValueError('This blueprint fixes its subject mix')
    value=templates[kind]
    if sum(s['count'] for s in value['slots'])!=value['question_count'] or not 1<=value['question_count']<=50 or not 60<=value['allowed_seconds']<=7200 or not 0<=value['negative_mark']<=1:
        raise ValueError('Invalid authored blueprint')
    if any(s['count']<1 or s['weight']<=0 for s in value['slots']):raise ValueError('Invalid blueprint weights')
    return {**value,'kind':kind,'subject_filter':subject,'level_filter':level,'scoring_policy':'forge-timed/binary-1',
            'notice':'Original Forge practice blueprint; not an official employer exam. Local timing is not remote proctoring. No mastery credit.'}


def items(session,row):
    return session.exec(select(m.TimedTestItem).where(m.TimedTestItem.session_id==row.id).order_by(m.TimedTestItem.position)).all()


def owner(session,selection):
    link=session.exec(select(m.TimedTestItem).where(m.TimedTestItem.selection_id==selection.id)).one_or_none()
    if link is None:raise ValueError('Timed selection has no test owner')
    return session.get(m.TimedTestSession,link.session_id),link


def validate_submission(session,selection,now):
    row,link=owner(session,selection)
    if row.status!='active':raise ValueError('Timed test is no longer active')
    if assessment.utc(now)>=assessment.utc(row.deadline_at):raise ValueError('Timed test deadline elapsed; complete the test')
    return row,link


def start(session,kind,subject=None,level=None,*,now=None):
    now=assessment.utc(now or m.utc_now())
    if assessment.active_scored_interview(session):raise ValueError('Finish or abandon the active scored assessment first')
    curriculum=get_active_curriculum(session)
    if not curriculum or curriculum.status!='confirmed':raise ValueError('Choose a confirmed curriculum')
    spec=blueprint(kind,subject,level)
    exposed={s.family for s in session.exec(select(m.AssessmentSelection))}
    topics=session.exec(select(m.Topic).join(m.Track).where(m.Track.curriculum_id==curriculum.id).order_by(m.Topic.id)).all()
    pool=[]
    for topic in topics:
        for item,revision,_ in approved_items(session,topic):
            if 'interview' not in item.purposes or item.kind=='reflection' or item.family in exposed:continue
            if level is not None and item.level!=level:continue
            if subject and item.subject!=subject:continue
            if spec.get('coding_only') and item.kind not in {'python','sql'}:continue
            pool.append((topic,item,revision))
    chosen=[];used=set()
    for slot in spec['slots']:
        expected=subject if slot['subject']=='$subject' else slot['subject']
        candidates=[p for p in pool if (expected=='*' or p[1].subject==expected) and p[1].family not in used]
        # Level-wide tests rotate subjects rather than consuming one whole track.
        groups={s:sorted([p for p in candidates if p[1].subject==s],key=lambda p:(p[1].key,p[2].sha256)) for s in sorted({p[1].subject for p in candidates})}
        ordered=[]
        while any(groups.values()):
            for values in groups.values():
                if values:ordered.append(values.pop(0))
        unique=[]
        for candidate in ordered:
            if candidate[1].family not in used:
                unique.append(candidate);used.add(candidate[1].family)
                if len(unique)==slot['count']:break
        if len(unique)!=slot['count']:raise ValueError('No approved unused test pool for '+str(expected)+' at this level; no session was created')
        chosen.extend((topic,item,revision,slot['weight']) for topic,item,revision in unique)
    assessment.help_guard(session,commit=False)
    row=m.TimedTestSession(id=str(uuid4()),curriculum_id=curriculum.id,blueprint_json=json.dumps(spec),started_at=now,deadline_at=now+timedelta(seconds=spec['allowed_seconds']))
    session.add(row);session.flush()
    for position,(topic,item,revision,weight) in enumerate(chosen):
        selection=assessment.make_selection(session,topic,item,revision,'approved','timed',created_at=now)
        session.add(m.TimedTestItem(session_id=row.id,position=position,selection_id=selection.id,weight=weight,negative_mark=spec['negative_mark']))
    session.commit();return read(session,row,now=now)


def read(session,row,*,now=None):
    now=assessment.utc(now or m.utc_now())
    if row.status=='active' and now>=assessment.utc(row.deadline_at):complete(session,row,now=now,reason='timeout')
    if row.status=='completed' and assessment.active_scored_interview(session):raise ValueError('Finish the active scored assessment before reading saved answers')
    questions=[]
    for link in items(session,row):
        selected=session.get(m.AssessmentSelection,link.selection_id)
        public=assessment.public(session,selected)
        if link.draft_json!='{}':public['draft']=json.loads(link.draft_json)
        questions.append({'position':link.position,'assessment':public,'weight':link.weight,'negative_mark':link.negative_mark})
    return {'id':row.id,'status':row.status,'blueprint':json.loads(row.blueprint_json),'started_at':row.started_at,'deadline_at':row.deadline_at,
            'remaining_seconds':max(0,int((assessment.utc(row.deadline_at)-now).total_seconds())) if row.status=='active' else 0,
            'questions':questions,'report':json.loads(row.report_json) if row.status=='completed' else None}


def _selection(session,row,position):
    link=session.get(m.TimedTestItem,(row.id,position))
    if link is None:raise ValueError('Question does not belong to this test')
    return link,session.get(m.AssessmentSelection,link.selection_id)


def save_draft(session,row,position,request,*,now=None):
    link,selected=_selection(session,row,position)
    validate_submission(session,selected,now or m.utc_now())
    if selected.status!='open':raise ValueError('Submitted answers are locked')
    if request.content_sha256!=selected.content_sha256:raise ValueError('Stale content revision')
    link.draft_json=request.model_dump_json();session.add(link);session.commit()
    return read(session,row,now=now)


def answer(session,row,position,request,*,clock=None):
    clock=clock or m.utc_now
    link,selected=_selection(session,row,position)
    if row.status=='completed' or selected.status=='complete':return read(session,row,now=clock())
    save_draft(session,row,position,request,now=clock())
    try:
        result=assessment.submit(session,selected,request,now=clock(),commit=False,allow_timed=True)
        if result.get('error'):
            session.rollback();return {**read(session,session.get(m.TimedTestSession,row.id),now=clock()),'error':result['error']}
        finished=assessment.utc(clock())
        session.refresh(row)
        if row.status!='active' or finished>=assessment.utc(row.deadline_at):
            key=row.id;session.rollback();row=session.get(m.TimedTestSession,key)
            if row.status=='active':complete(session,row,now=finished,reason='timeout')
            return read(session,row,now=finished)
        session.commit();return read(session,row,now=finished)
    except IntegrityError:
        key=row.id;session.rollback();row=session.get(m.TimedTestSession,key)
        if row.status!='active':return read(session,row,now=clock())
        raise


def complete(session,row,*,now=None,reason='submitted'):
    if row.status=='completed':return report(session,row)
    if row.status!='active':raise ValueError('An abandoned assessment has no scored report')
    now=assessment.utc(now or m.utc_now());results=[];earned=0;maximum=0
    for link in items(session,row):
        selected=session.get(m.AssessmentSelection,link.selection_id);item=AssessmentItem.model_validate_json(selected.snapshot_json)
        unanswered=selected.status=='open'
        outcome=json.loads(selected.result_json) if not unanswered else {}
        passed=bool(outcome.get('passed'))
        points=link.weight if passed else 0 if unanswered else -link.weight*link.negative_mark
        earned+=points;maximum+=link.weight
        if unanswered:
            selected.status='expired';selected.completed_at=now
            selected.result_json=json.dumps({'score':0,'passed':False,'unanswered':True,'explanation':item.explanation})
            session.add(selected)
        worked=item.contract.get('reference_solution',item.contract.get('correct',item.contract.get('answer')))
        results.append({'position':link.position,'subject':item.subject,'item_key':item.key,'content_sha256':selected.content_sha256,
            'score':100 if passed else 0,'points':points,'weight':link.weight,'unanswered':unanswered,'explanation':item.explanation,'worked_answer':worked,
            'submitted_answer':outcome.get('answer',json.loads(link.draft_json).get('source') or json.loads(link.draft_json).get('answer')),
            'mistake_analysis':None if passed else 'Unanswered' if unanswered else 'Submitted response did not satisfy the frozen objective contract'})
    result_report={'label':'Forge timed practice score','overall_score':round(max(0,earned)/maximum*100,2) if maximum else 0,
        'earned_points':earned,'maximum_points':maximum,'completion_reason':'timeout' if now>=assessment.utc(row.deadline_at) else reason,
        'blueprint':json.loads(row.blueprint_json),'questions':results,'disclaimer':'Original local practice assessment; not a hiring probability, official employer exam or technical mastery update.'}
    row.status='completed';row.completed_at=now;row.report_json=json.dumps(result_report);session.add(row);session.commit();return result_report


def abandon(session,row):
    if row.status=='abandoned':return read(session,row)
    if row.status!='active':raise ValueError('The test is already complete')
    for link in items(session,row):
        selected=session.get(m.AssessmentSelection,link.selection_id)
        if selected.status=='open':selected.status='abandoned';selected.completed_at=m.utc_now();session.add(selected)
    row.status='abandoned';row.completed_at=m.utc_now();session.add(row);session.commit();return read(session,row)


def report(session,row):
    if assessment.active_scored_interview(session):raise ValueError('Reports are unavailable during an active scored assessment')
    if row.status!='completed':raise ValueError('Complete the assessment before reading feedback')
    return json.loads(row.report_json)
