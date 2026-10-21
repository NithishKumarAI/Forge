import hashlib,json
from pathlib import Path
from sqlmodel import Session,select
from ..config import settings
from ..models import ArenaAttempt,ArenaHintUse,ArenaProblem,MasteryEvidenceEvent,ArenaTopicBinding,ContentRevision,ArenaAttemptContent
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
    from .content_publication import release_entries
    for entry, revision in release_entries(session, curriculum_id=active.id if active else -1):
        if revision.content_key == f"arena/{key}":
            return entry.topic_id
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


def problem_revision(session, key, revision_id=None):
    if revision_id is not None:
        revision = session.get(ContentRevision, revision_id)
        if not revision or revision.content_key != f"arena/{key}" or revision.content_type != "arena_problem":
            raise RegistryError("Unknown problem revision")
        return revision
    from .content_publication import release_entries
    active = get_active_curriculum(session)
    for entry, revision in release_entries(session, curriculum_id=active.id if active else -1):
        if revision.content_key == f"arena/{key}":
            return revision
    row = session.get(ArenaProblem, key)
    revision = session.exec(select(ContentRevision).where(ContentRevision.content_key == f"arena/{key}",
        ContentRevision.revision == row.version)).one_or_none() if row else None
    if revision is None:
        raise RegistryError("Arena problem has no registered immutable revision")
    if revision.approval_status != "legacy_baseline":
        raise RegistryError("Problem is unavailable in the selected approved release")
    return revision


def load_problem(key: str, root: Path | None = None, *, session: Session | None = None, revision_id: int | None = None) -> CodingProblem:
    if session is not None:
        revision = problem_revision(session, key, revision_id)
        return CodingProblem.model_validate(load_snapshot(revision)["problem"])
    # Compatibility for development validators; HTTP workflows always supply a session.
    for _, problem in load_problem_files(root):
        if problem.key == key:
            return problem
    raise ValueError("Arena problem not found")

def public_problem(session:Session,row:ArenaProblem,revision_id:int|None=None)->dict:
    from .assessment import help_guard
    help_guard(session)
    revision=problem_revision(session,row.key,revision_id)
    p=load_problem(row.key,session=session,revision_id=revision.id)
    attempts=session.exec(select(ArenaAttempt).where(ArenaAttempt.problem_key==row.key,ArenaAttempt.passed==True)).all()
    solved=any((session.get(ArenaAttemptContent,a.id).content_revision_id==revision.id if session.get(ArenaAttemptContent,a.id) else revision.approval_status=="legacy_baseline") for a in attempts)
    data=p.model_dump(exclude={"reference_solution", "publication_contract", "negative_solutions", "hints"});data["content_revision_id"]=revision.id;data["mapped_topic_id"]=resolve_arena_topic(session,row.key);data["mapping_status"]="bound" if data["mapped_topic_id"] else "unresolved";data["hints_available"]=len(p.hints);data["solved"]=solved;data["attempt_count"]=len(session.exec(select(ArenaAttempt).where(ArenaAttempt.problem_key==row.key)).all())
    if p.adapted or p.source_project:
        data["declared_source_type"]=p.source_type
        data["source_type"]="adapted"
    data["content_sha256"]=revision.sha256
    data["provenance"]=json.loads(revision.provenance_json)
    data["approval_status"]="published" if revision.approval_status=="candidate" and revision_id is None else ("historical_release" if revision.approval_status=="candidate" else "legacy_baseline")
    if not solved:data.pop("explanation",None);data.pop("complexity",None)
    validation=data["validation"]
    if p.track=="sql": data["validation"]={k:v for k,v in validation.items() if k in {"setup_sql","visible_tables","sample_rows","expected_columns","mode","order_sensitive"}}
    else:data["validation"]={"judge_mode":validation.get("judge_mode","function"),"function_name":validation.get("function_name"),"sample_tests":validation["sample_tests"],"time_limit_ms":validation.get("time_limit_ms",5000),"input_format":validation.get("input_format"),"output_format":validation.get("output_format")}
    return data

def list_problems(session:Session,track=None,difficulty=None,tag=None,status=None)->list[dict]:
    rows=session.exec(select(ArenaProblem).where(ArenaProblem.active==True).order_by(ArenaProblem.track,ArenaProblem.difficulty,ArenaProblem.title)).all()
    out=[]
    from .content_publication import release_entries
    active=get_active_curriculum(session)
    released_keys={revision.content_key for _,revision in release_entries(session,curriculum_id=active.id if active else -1)}
    for row in rows:
        base=session.exec(select(ContentRevision).where(ContentRevision.content_key==f"arena/{row.key}",ContentRevision.revision==row.version)).one()
        if base.approval_status!="legacy_baseline" and base.content_key not in released_keys:continue
        data=public_problem(session,row)
        if track and row.track!=track:continue
        if difficulty and row.difficulty!=difficulty:continue
        if tag and tag not in data["topic_tags"]:continue
        if status=="solved" and not data["solved"]:continue
        if status=="unsolved" and data["solved"]:continue
        out.append(data)
    return out

def validation_payload(key,session=None):
    if session is None:raise ValueError("Learner validation requires a session")
    from .assessment import help_guard
    help_guard(session)
    return public_problem(session,session.get(ArenaProblem,key))["validation"]

def reveal_hint(session:Session,key:str)->dict:
    from .assessment import help_guard
    help_guard(session)
    p=load_problem(key,session=session);use=session.get(ArenaHintUse,key) or ArenaHintUse(problem_key=key)
    if use.count>=len(p.hints):raise ValueError("No more hints")
    text=p.hints[use.count];use.count+=1;session.add(use);session.commit();return {"index":use.count,"text":text}

def record_attempt(session,key,request):
    from .assessment_pool import arena_item
    from .assessment import make_selection,submit,active_scored_interview
    from ..schemas.assessment import AssessmentSubmission
    from ..models import Topic
    if active_scored_interview(session):raise ValueError("Complete or save the scored interview first")
    revision=problem_revision(session,key)
    if getattr(request,"content_revision_id",None) is None:raise ValueError("An exact content_revision_id is required")
    if request.content_revision_id!=revision.id:raise ValueError("Problem release changed; reload before submitting")
    topic_id=resolve_arena_topic(session,key)
    item=arena_item(load_problem(key,session=session))
    from .content_publication import release_entries
    active=get_active_curriculum(session)
    approved=any(r.id==revision.id for _,r in release_entries(session,curriculum_id=active.id if active else -1))
    if not topic_id:
        from .assessment_judge import judge
        checked=judge(item,request.source)
        if checked["status"]!="verified":raise ValueError("Awaiting local worker verification; no mastery evidence")
        passed=checked["total"]>0 and checked["passed"]==checked["total"]
        score=round(100*checked["passed"]/checked["total"],1) if checked["total"] else 0
        attempt=ArenaAttempt(problem_key=key,track=session.get(ArenaProblem,key).track,submitted_source=request.source,score=score,passed=passed,
            result_json=json.dumps({**checked,"policy_version":"forge-evidence/2","judge_version":"forge-worker/1","content_sha256":revision.sha256,"unmapped":True,"verification":"backend_bounded_worker"}))
        session.add(attempt);session.flush();session.add(ArenaAttemptContent(attempt_id=attempt.id,content_revision_id=revision.id));session.commit()
        p=load_problem(key,session=session)
        return {"attempt_id":attempt.id,"passed":passed,"score":score,"approval":"unmapped_legacy","verification":"backend_bounded_worker",
            "solution":p.reference_solution if passed else None,"explanation":p.explanation if passed else None,"complexity":p.complexity if passed else None}
    selected=make_selection(session,session.get(Topic,topic_id),item,revision,"approved" if approved else "legacy_unverified","arena")
    use=session.get(ArenaHintUse,key)
    selected.hints_used=use.count if use else 0;selected.assisted=bool(selected.assisted or selected.hints_used)
    session.add(selected);session.commit()
    result=submit(session,selected,AssessmentSubmission(content_sha256=revision.sha256,source=request.source))
    if result.get("error"):raise ValueError(result["error"])
    actual=result["result"]
    p=load_problem(key,session=session)
    return {"attempt_id":selected.arena_attempt_id,"passed":actual["passed"],"score":actual["score"],
        "verification":actual["verification"],"approval":selected.approval,
        "solution":p.reference_solution if actual["passed"] else None,"explanation":p.explanation if actual["passed"] else None,"complexity":p.complexity if actual["passed"] else None}


def give_up(session:Session,key:str,source:str="")->dict:
    from .assessment import help_guard
    help_guard(session)
    row=session.get(ArenaProblem,key)
    if not row:raise ValueError("Arena problem not found")
    attempt=ArenaAttempt(problem_key=key,track=row.track,submitted_source=source or "# Gave up",score=0,passed=False,gave_up=True);session.add(attempt);session.flush();session.add(ArenaAttemptContent(attempt_id=attempt.id,content_revision_id=problem_revision(session,key).id));session.commit();p=load_problem(key,session=session);return {"attempt_id":attempt.id,"passed":False,"score":0,"solution":p.reference_solution,"explanation":p.explanation,"complexity":p.complexity}
