from pathlib import Path
import json
from sqlmodel import select
from app.models import ArenaProblem,Curriculum,MasteryEvidenceEvent,Track
from app.schemas.arena import ArenaAttemptRequest
from app.services.arena import list_problems,public_problem,record_attempt,sync_problem_bank,validation_payload
from app.services.curriculum import seed_default_curriculum
from app.services.curriculum_migration import migrate_default_v2
from app.services.planner import planner_settings,today_plan
from scripts.problem_builder.validate import validate_problem

ROOT=Path(__file__).resolve().parents[3]

def test_v2_coverage_contracts_include_every_track():
    contract=json.loads((ROOT/"data/course-coverage/interview-curriculum-v2.json").read_text())
    expected={"python","sql-postgresql","dsa","backend-engineering","cs-fundamentals","llm-engineering","rag","machine-learning","production-devops","frontend-basics","interview-engineering"}
    assert set(contract)==expected
    assert "bool" in contract["python"]["foundations"] and "window-functions" in contract["sql-postgresql"]

def activate_v2(session):
    from app.services.active_curriculum import activate_curriculum
    old=session.exec(select(Curriculum).where(Curriculum.version==1)).first();new=seed_default_curriculum(session,ROOT/"data/default-interview-curriculum-v2.json");migrate_default_v2(session,old,new,ROOT/"data/curriculum-migrations/v1-to-v2.json");activate_curriculum(session,new);return new

def test_v2_priority_tracks_and_old_curriculum_preserved(session):
    new=activate_v2(session);assert len(session.exec(select(Curriculum)).all())==2
    tracks=session.exec(select(Track).where(Track.curriculum_id==new.id).order_by(Track.order_index)).all()
    assert [(x.slug,x.priority) for x in tracks[:3]]==[("python",100),("sql-postgresql",100),("dsa",98)]

def test_problem_bank_validates_loads_and_hides_solutions(session):
    activate_v2(session)
    for path in (ROOT/"content/problem-bank").glob("*/*.json"):validate_problem(path)
    assert sync_problem_bank(session)>=6
    rows=list_problems(session);assert {x["track"] for x in rows}=={"python","sql","dsa"}
    problem=public_problem(session,session.get(ArenaProblem,"python-normalize-name"));assert "reference_solution" not in problem and "hidden_tests" not in problem["validation"]

def test_unverified_legacy_arena_cannot_farm_evidence(session):
    activate_v2(session);sync_problem_bank(session);request=ArenaAttemptRequest(source="def normalize_name(value): return ' '.join(value.split()).title()",passed=True,score=100,result={},content_revision_id=__import__("app.services.arena",fromlist=["problem_revision"]).problem_revision(session,"python-normalize-name").id)
    first=record_attempt(session,"python-normalize-name",request);assert first["verification"]=="backend_bounded_worker"
    count=len(session.exec(select(MasteryEvidenceEvent).where(MasteryEvidenceEvent.event_type=="arena")).all());record_attempt(session,"python-normalize-name",request)
    assert len(session.exec(select(MasteryEvidenceEvent).where(MasteryEvidenceEvent.event_type=="arena")).all())==count

def test_sql_hidden_dataset_and_planner_foundation_targets(session):
    activate_v2(session);sync_problem_bank(session);sql=validation_payload("sql-active-users",session=session)
    assert "hidden_datasets" not in sql and "expected_rows" not in sql
    settings=planner_settings(session);assert (settings["python_daily_minimum"],settings["sql_daily_minimum"],settings["dsa_daily_minimum"])==(45,30,30)
    plan=today_plan(session);assert plan['items']==[] and plan['unallocated_minutes']==plan['target_minutes']
