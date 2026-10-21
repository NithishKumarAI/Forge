import hashlib,json
from pathlib import Path
from sqlmodel import Session,select
from ..config import settings
from ..models import ArenaAttempt,ArenaHintUse,ArenaProblem,MasteryEvidenceEvent,ArenaTopicBinding,ContentRevision
from ..schemas.arena import CodingProblem
from .active_curriculum import get_active_curriculum
from .content_paths import safe_path
from .content_registry import RegistryError,register_revision,load_snapshot,matched_curricula,load_manifest

PROBLEM_ROOT = settings.problem_bank_path


def load_problem_files(root: Path | None = None):
    root = root or settings.problem_bank_path
    for path in sorted(root.glob("*/*.json")):
        relative = path.relative_to(root).as_posix()
        path = safe_path(root, relative)
        yield path, CodingProblem.model_validate_json(path.read_text(encoding="utf-8"))


def resolve_arena_topic(session: Session, key: str) -> int | None:
    active = get_active_curriculum(session)
    binding = session.get(ArenaTopicBinding, (active.id, key)) if active else None
    return binding.topic_id if binding else None


def sync_problem_bank(session: Session, root: Path | None = None) -> int:
    root = root or settings.problem_bank_path
    try:
        revisions = {}
        for path, problem in load_problem_files(root):
            raw = json.loads(path.read_text(encoding="utf-8"))
            revision = register_revision(session, key=f"arena/{problem.key}", revision=problem.version,
                content_type="arena_problem", source_path=path.relative_to(root).as_posix(),
                payload={"problem": raw}, provenance={"source_file_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                    "legacy_metadata": {key: raw[key] for key in ("source_type","source_project","source_exercise","license","adapted") if key in raw}})
            revisions[problem.key] = revision
            row = session.get(ArenaProblem, problem.key)
            if row is None:
                row = ArenaProblem(key=problem.key, track=problem.track, title=problem.title,
                    difficulty=problem.difficulty, topic_tags_json=json.dumps(problem.topic_tags),
                    source_path=path.relative_to(root).as_posix(), content_hash=hashlib.sha256(path.read_bytes()).hexdigest(),
                    version=problem.version)
                session.add(row)
        session.flush()
        for spec, curriculum, topics in matched_curricula(session, load_manifest()):
            if {item.problem_key for item in spec.arena} != set(revisions):
                raise RegistryError("Arena manifest and problem bank differ; explicit review is required")
            for item in spec.arena:
                revision = revisions[item.problem_key]
                if revision.revision != item.revision or (item.topic is not None and item.topic not in topics):
                    raise RegistryError("Arena binding references a missing topic or problem revision")
                topic_id = topics[item.topic].id if item.topic else None
                expected = {"content_revision_id": revision.id, "topic_id": topic_id, "rationale": item.rationale}
                existing = session.get(ArenaTopicBinding, (curriculum.id, item.problem_key))
                if existing and any(getattr(existing, field) != value for field, value in expected.items()):
                    raise RegistryError("Arena binding changed without an explicit migration")
                if not existing:
                    session.add(ArenaTopicBinding(curriculum_id=curriculum.id, problem_key=item.problem_key, **expected))
        session.flush()
        for key in revisions:
            row = session.get(ArenaProblem, key)
            mapped = resolve_arena_topic(session, key)
            if row.mapped_topic_id != mapped:
                row.mapped_topic_id = mapped
                session.add(row)
        session.commit()
        return len(revisions)
    except BaseException:
        session.rollback()
        raise


def load_problem(key: str, root: Path | None = None, *, session: Session | None = None) -> CodingProblem:
    if session is not None:
        row = session.get(ArenaProblem, key)
        revision = session.exec(select(ContentRevision).where(ContentRevision.content_key == f"arena/{key}",
            ContentRevision.revision == row.version)).one_or_none() if row else None
        if revision is None:
            raise RegistryError("Arena problem has no registered immutable revision")
        return CodingProblem.model_validate(load_snapshot(revision)["problem"])
    # Compatibility for development validators; HTTP workflows always supply a session.
    for _, problem in load_problem_files(root):
        if problem.key == key:
            return problem
    raise ValueError("Arena problem not found")

def public_problem(session:Session,row:ArenaProblem)->dict:
    p=load_problem(row.key,session=session);solved=session.exec(select(ArenaAttempt).where(ArenaAttempt.problem_key==row.key,ArenaAttempt.passed==True)).first() is not None
    data=p.model_dump(exclude={"reference_solution"});data["mapped_topic_id"]=resolve_arena_topic(session,row.key);data["mapping_status"]="bound" if data["mapped_topic_id"] else "unresolved";data["hints_available"]=len(p.hints);data["solved"]=solved;data["attempt_count"]=len(session.exec(select(ArenaAttempt).where(ArenaAttempt.problem_key==row.key)).all())
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

def validation_payload(key:str,session:Session|None=None)->dict:
    p=load_problem(key,session=session);return p.validation

def reveal_hint(session:Session,key:str)->dict:
    p=load_problem(key,session=session);use=session.get(ArenaHintUse,key) or ArenaHintUse(problem_key=key)
    if use.count>=len(p.hints):raise ValueError("No more hints")
    text=p.hints[use.count];use.count+=1;session.add(use);session.commit();return {"index":use.count,"text":text}

def record_attempt(session:Session,key:str,request)->dict:
    row=session.get(ArenaProblem,key)
    if not row:raise ValueError("Arena problem not found")
    use=session.get(ArenaHintUse,key);previous=session.exec(select(ArenaAttempt).where(ArenaAttempt.problem_key==key,ArenaAttempt.passed==True)).first()
    attempt=ArenaAttempt(problem_key=key,track=row.track,submitted_source=request.source,score=request.score,passed=request.passed,hints_used=use.count if use else 0,runtime_ms=request.runtime_ms,result_json=json.dumps(request.result));session.add(attempt);session.flush()
    topic_id=resolve_arena_topic(session,key)
    if request.passed and not previous and topic_id:
        weight=(1.25 if row.difficulty=="medium" else 1.0)*(0.7 if attempt.hints_used else 1.0)
        session.add(MasteryEvidenceEvent(topic_id=topic_id,event_type="arena",score=request.score,evidence_weight=weight,assisted=attempt.hints_used>0,metadata_json=json.dumps({"problem_key":key,"difficulty":row.difficulty})))
    session.commit()
    if request.passed and topic_id:
        from .mastery import recalculate_topic
        recalculate_topic(session,topic_id)
    return {"attempt_id":attempt.id,"passed":attempt.passed,"score":attempt.score,"solution":load_problem(key,session=session).reference_solution if request.passed else None,"explanation":load_problem(key,session=session).explanation if request.passed else None,"complexity":load_problem(key,session=session).complexity if request.passed else None}

def give_up(session:Session,key:str,source:str="")->dict:
    row=session.get(ArenaProblem,key)
    if not row:raise ValueError("Arena problem not found")
    attempt=ArenaAttempt(problem_key=key,track=row.track,submitted_source=source or "# Gave up",score=0,passed=False,gave_up=True);session.add(attempt);session.commit();p=load_problem(key,session=session);return {"attempt_id":attempt.id,"passed":False,"score":0,"solution":p.reference_solution,"explanation":p.explanation,"complexity":p.complexity}
