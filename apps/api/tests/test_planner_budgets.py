import json
from datetime import datetime,timezone,timedelta
import pytest
from sqlmodel import select
from app import models as m
from app.services import planner as p
from tests.phase5_fixtures import published_scope


@pytest.mark.parametrize('target',[300,360,480])
def test_budget_presets_diversity_p0_and_no_mastery(session,target):
    published_scope(session)
    p.update_planner_settings(session,{'daily_study_target':target})
    plan=p.today_plan(session)
    assert plan['planned_minutes']<=target
    assert plan['planned_minutes']+plan['unallocated_minutes']==target
    assert len({i['subject'] for i in plan['items']})>=5
    assert {'python','sql-postgresql','dsa'}<={i['subject'] for i in plan['items']}
    assert len({(i['topic_id'],i['item_type']) for i in plan['items']})==len(plan['items'])
    assert p.today_plan(session)==plan
    assert not session.exec(select(m.MasteryEvidenceEvent)).all()


def test_missing_approved_content_leaves_budget_free_and_legacy_plan_untouched(session):
    old=m.DailyPlanItem(plan_date='2026-10-22',curriculum_id=1,item_type='learn',reason='Historical plan',estimated_minutes=45,status='completed')
    session.add(old);session.commit();session.refresh(old);before=old.model_dump()
    plan=p.today_plan(session)
    assert plan['items']==[] and plan['unallocated_minutes']==300
    assert session.get(m.DailyPlanItem,old.id).model_dump()==before


def test_local_midnight_settings_change_and_utc_are_explicit(session):
    now=datetime(2026,10,21,20,tzinfo=timezone.utc)
    first=p.today_plan(session,now=now)
    assert first['date']=='2026-10-22' and first['timezone']=='Asia/Kolkata'
    p.update_planner_settings(session,{'study_timezone':'UTC'})
    second=p.today_plan(session,now=now)
    assert second['date']=='2026-10-21' and second['id']!=first['id']
    p.update_planner_settings(session,{'study_timezone':'America/New_York'})
    assert p.today_plan(session,now=datetime(2026,11,1,5,30,tzinfo=timezone.utc))['date']=='2026-11-01'
    with pytest.raises(ValueError):p.update_planner_settings(session,{'study_timezone':'not/a/timezone'})


def test_regeneration_retains_completed_skipped_and_never_writes_evidence(session):
    published_scope(session);before=p.today_plan(session)
    completed,skipped=before['items'][:2]
    p.set_plan_status(session,completed['id'],'completed');p.set_plan_status(session,skipped['id'],'skipped')
    p.update_planner_settings(session,{'daily_study_target':360})
    assert p.today_plan(session)['settings_changed']
    after=p.today_plan(session,regenerate=True);statuses={i['id']:i['status'] for i in after['items']}
    assert statuses[completed['id']]=='completed' and statuses[skipped['id']]=='skipped'
    assert after['revision']==2 and after['planned_minutes']<=360
    assert len(session.exec(select(m.StudyPlanRevision)).all())==2
    assert not session.exec(select(m.MasteryEvidenceEvent)).all()
    with pytest.raises(ValueError):p.set_plan_status(session,completed['id'],'skipped')


def test_manual_replacement_keeps_other_tasks_and_exact_references(session):
    published_scope(session);before=p.today_plan(session)
    used={(i['topic_id'],i['item_type']) for i in before['items']}
    replacement=next(a for a in p.replacement_options(session) if (a['topic_id'],a['kind']) not in used)
    removed=before['items'][0];after=p.replace_item(session,removed['id'],replacement['key'])
    assert after['revision']==2 and after['planned_minutes']<=after['target_minutes']
    assert {i['id'] for i in before['items'][1:]}<={i['id'] for i in after['items']}
    assert removed['id'] not in {i['id'] for i in after['items']}
    assert all(i['content_references'] for i in after['items'])
    assert session.get(m.DailyPlanItem,removed['id']) is not None


def test_due_review_priority_oversized_minima_and_small_budget(session):
    curriculum=published_scope(session)
    topic=session.exec(select(m.Topic).join(m.Track).where(m.Track.curriculum_id==curriculum.id,m.Track.slug=='quantitative-aptitude').order_by(m.Topic.order_index)).first()
    session.add(m.ReviewState(topic_id=topic.id,due_at=datetime.now(timezone.utc)-timedelta(hours=1)));session.commit()
    p.update_planner_settings(session,{'daily_study_target':30,'python_daily_minimum':180,'sql_daily_minimum':180,'dsa_daily_minimum':120})
    plan=p.today_plan(session)
    assert plan['items'][0]['item_type']=='review'
    assert plan['planned_minutes']<=30
