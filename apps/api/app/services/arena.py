import hashlib,json
from pathlib import Path
from sqlmodel import Session,select
from ..config import settings
from ..models import ArenaAttempt,ArenaHintUse,ArenaProblem,MasteryEvidenceEvent,Topic,Track
from ..schemas.arena import CodingProblem
from .active_curriculum import get_active_curriculum

PROBLEM_ROOT=settings.course_content_path.parents[1]/"problem-bank"

def load_problem_files(root:Path=PROBLEM_ROOT):
    for path in root.glob("*/*.json"):
        yield path,CodingProblem.model_validate_json(path.read_text(encoding="utf-8"))

def sync_problem_bank(session:Session,root:Path=PROBLEM_ROOT)->int:
    count=0;active=get_active_curriculum(session);aliases={"python/syntax-data-types":"python/foundations","sql-cs/select-filtering":"sql-postgresql/query-basics","sql-cs/joins":"sql-postgresql/joins"}
    for path,problem in load_problem_files(root):
        topic=None
        mapped=aliases.get(problem.mapped_topic,problem.mapped_topic)
        if "/" in mapped:
            track_slug,topic_slug=mapped.split("/",1);track=session.exec(select(Track).where(Track.slug==track_slug,Track.curriculum_id==active.id)).first() if active else None;topic=session.exec(select(Topic).where(Topic.track_id==track.id,Topic.slug==topic_slug)).first() if track else None
        digest=hashlib.sha256(path.read_bytes()).hexdigest();row=session.get(ArenaProblem,problem.key)
        if row is None: row=ArenaProblem(key=problem.key,track=problem.track,title=problem.title,difficulty=problem.difficulty,source_path=str(path.relative_to(root)),content_hash=digest,version=problem.version)
        row.track,row.title,row.difficulty,row.topic_tags_json,row.source_path,row.content_hash,row.version,row.active,row.mapped_topic_id=problem.track,problem.title,problem.difficulty,json.dumps(problem.topic_tags),str(path.relative_to(root)),digest,problem.version,True,topic.id if topic else None
        session.add(row);count+=1
    session.commit();return count

def load_problem(key:str,root:Path=PROBLEM_ROOT)->CodingProblem:
    for _,problem in load_problem_files(root):
        if problem.key==key:return problem
    raise ValueError("Arena problem not found")

def public_problem(session:Session,row:ArenaProblem)->dict:
    p=load_problem(row.key);solved=session.exec(select(ArenaAttempt).where(ArenaAttempt.problem_key==row.key,ArenaAttempt.passed==True)).first() is not None
    data=p.model_dump(exclude={"reference_solution"});data["hints_available"]=len(p.hints);data["solved"]=solved;data["attempt_count"]=len(session.exec(select(ArenaAttempt).where(ArenaAttempt.problem_key==row.key)).all())
    if not solved:data.pop("explanation",None);data.pop("complexity",None)
    validation=data["validation"]
    if p.track=="sql": data["validation"]={k:v for k,v in validation.items() if k in {"setup_sql","visible_tables","sample_rows","expected_columns","mode","order_sensitive"}}
    else:data["validation"]={"judge_mode":validation.get("judge_mode","function"),"function_name":validation.get("function_name"),"sample_tests":validation["sample_tests"],"time_limit_ms":validation.get("time_limit_ms",5000),"input_format":validation.get("input_format"),"output_format":validation.get("output_format")}
    return data

def list_problems(session:Session,track=None,difficulty=None,tag=None,status=None)->list[dict]:
    rows=session.exec(select(ArenaProblem).where(ArenaProblem.active==True).order_by(ArenaProblem.track,ArenaProblem.difficulty,ArenaProblem.title)).all()
    out=[]
    for row in rows:
        data=public_problem(session,row)
        if track and row.track!=track:continue
        if difficulty and row.difficulty!=difficulty:continue
        if tag and tag not in data["topic_tags"]:continue
        if status=="solved" and not data["solved"]:continue
        if status=="unsolved" and data["solved"]:continue
        out.append(data)
    return out

def validation_payload(key:str)->dict:
    p=load_problem(key);return p.validation

def reveal_hint(session:Session,key:str)->dict:
    p=load_problem(key);use=session.get(ArenaHintUse,key) or ArenaHintUse(problem_key=key)
    if use.count>=len(p.hints):raise ValueError("No more hints")
    text=p.hints[use.count];use.count+=1;session.add(use);session.commit();return {"index":use.count,"text":text}

def record_attempt(session:Session,key:str,request)->dict:
    row=session.get(ArenaProblem,key)
    if not row:raise ValueError("Arena problem not found")
    use=session.get(ArenaHintUse,key);previous=session.exec(select(ArenaAttempt).where(ArenaAttempt.problem_key==key,ArenaAttempt.passed==True)).first()
    attempt=ArenaAttempt(problem_key=key,track=row.track,submitted_source=request.source,score=request.score,passed=request.passed,hints_used=use.count if use else 0,runtime_ms=request.runtime_ms,result_json=json.dumps(request.result));session.add(attempt);session.flush()
    if request.passed and not previous and row.mapped_topic_id:
        weight=(1.25 if row.difficulty=="medium" else 1.0)*(0.7 if attempt.hints_used else 1.0)
        session.add(MasteryEvidenceEvent(topic_id=row.mapped_topic_id,event_type="arena",score=request.score,evidence_weight=weight,assisted=attempt.hints_used>0,metadata_json=json.dumps({"problem_key":key,"difficulty":row.difficulty})))
    session.commit()
    if request.passed and row.mapped_topic_id:
        from .mastery import recalculate_topic
        recalculate_topic(session,row.mapped_topic_id)
    return {"attempt_id":attempt.id,"passed":attempt.passed,"score":attempt.score,"solution":load_problem(key).reference_solution if request.passed else None,"explanation":load_problem(key).explanation if request.passed else None,"complexity":load_problem(key).complexity if request.passed else None}

def give_up(session:Session,key:str,source:str="")->dict:
    row=session.get(ArenaProblem,key)
    if not row:raise ValueError("Arena problem not found")
    attempt=ArenaAttempt(problem_key=key,track=row.track,submitted_source=source or "# Gave up",score=0,passed=False,gave_up=True);session.add(attempt);session.commit();p=load_problem(key);return {"attempt_id":attempt.id,"passed":False,"score":0,"solution":p.reference_solution,"explanation":p.explanation,"complexity":p.complexity}
