"""Only effective reviewed releases enter scored pools; no generated fallback."""
import json
from datetime import datetime,timedelta,timezone
from sqlmodel import select
from ..models import AssessmentSelection, EditionCurriculumBinding, Topic, Track, Exercise
from ..schemas.assessment import AssessmentBundle, AssessmentItem
from .content_publication import release_entries
from .content_registry import load_snapshot


def arena_item(problem, *, purpose="practice"):
    p=problem.model_dump() if hasattr(problem,"model_dump") else problem
    v=p["validation"]
    if p["track"]=="sql":
        contract={"columns":v["expected_columns"],"ordered":v.get("order_sensitive",False),"reference_solution":p["reference_solution"],
            "public_dataset":{"setup_sql":v["setup_sql"]},
            "datasets":[{"setup_sql":v["setup_sql"],"expected_rows":v["expected_rows"]},*v.get("hidden_datasets",[])]}
    else:
        import ast
        function=next((n for n in ast.parse(p["reference_solution"]).body if isinstance(n,ast.FunctionDef) and n.name==v.get("function_name")),None)
        contract={"mode":v.get("judge_mode","function"),"function_name":v.get("function_name"),"starter_code":p["starter_code"],
            "parameters":[a.arg for a in function.args.args] if function else [],
            "reference_solution":p["reference_solution"],"tests":v["sample_tests"]+v["hidden_tests"],"sample_tests":v["sample_tests"]}
    return AssessmentItem(key=p["key"],family="arena/"+p["key"],subject="sql-postgresql" if p["track"]=="sql" else p["track"],
        topic=p["key"],level=1 if p["difficulty"]=="easy" else 2,kind="sql" if p["track"]=="sql" else "python",
        purposes=[purpose],prompt=p["statement_markdown"],explanation=p["explanation"],hints=p["hints"],contract=contract)


def approved_items(session,topic):
    track=session.get(Track,topic.track_id)
    result=[]
    for entry,revision in release_entries(session,curriculum_id=track.curriculum_id):
        if entry.topic_id!=topic.id:continue
        payload=load_snapshot(revision)
        if revision.content_type=="assessment_bundle":
            for item in AssessmentBundle.model_validate(payload["assessment"]).items:
                if item.subject!=track.slug or item.topic!=topic.slug:
                    raise ValueError("Published assessment does not match target subject/topic")
                result.append((item,revision,"approved"))
        elif revision.content_type=="arena_problem":result.append((arena_item(payload["problem"]),revision,"approved"))
        elif revision.content_type=="lesson_bundle":
            for raw in payload["exercises"]:
                c=raw["content"]
                if raw["exercise_type"]=="multiple_choice":
                    kind="single_choice";contract={"choices":{str(i):v for i,v in enumerate(c["choices"])},"correct":[str(c["correct_index"]) ]};explanation=c["explanation"]
                elif raw["exercise_type"]=="short_answer":
                    kind="reflection";contract={"rubric":c["rubric"],"example":c["reference_answer"]};explanation=c["reference_answer"]
                else:continue
                item=AssessmentItem(key=raw["key"],family=revision.content_key+"/"+raw["key"],subject=track.slug,topic=topic.slug,level=1,
                    kind=kind,purposes=["practice"],prompt=raw["prompt_markdown"],explanation=explanation,hints=raw.get("hints",[]),contract=contract)
                result.append((item,revision,"approved"))
    return sorted(result,key=lambda p:(p[1].content_key,p[0].key,p[1].revision))


def candidates(session,topic,purpose,*,now=None):
    items=[p for p in approved_items(session,topic) if purpose in p[0].purposes]
    if purpose in {"transfer","recall"} and session.get(Track,topic.track_id).slug in {"python","sql-postgresql","sql-cs","dsa"}:
        items=[p for p in items if p[0].kind in {"python","sql"}]
    if purpose=="practice" and not session.get(EditionCurriculumBinding,session.get(Track,topic.track_id).curriculum_id):
        from .course import current_course_exercise_ids
        from ..models import CourseExerciseBinding,ContentRevision
        for eid in sorted(current_course_exercise_ids(session,topic.id)):
            exercise=session.get(Exercise,eid)
            binding=session.exec(select(CourseExerciseBinding).where(CourseExerciseBinding.exercise_id==eid)).one()
            revision=session.get(ContentRevision,binding.content_revision_id)
            # Approved course items are supported as ordinary practice but never reserved variants.
            c=json.loads(exercise.content_json)["content"]
            if exercise.exercise_type=="multiple_choice":
                contract={"choices":{str(i):v for i,v in enumerate(c["choices"])},"correct":[str(c["correct_index"])]}
                kind="single_choice";explanation=c["explanation"]
            elif exercise.exercise_type=="short_answer":
                contract={"rubric":c["rubric"],"example":c["reference_answer"]};kind="reflection";explanation=c["reference_answer"]
            else:continue
            item=AssessmentItem(key=binding.exercise_key,family=revision.content_key+"/"+binding.exercise_key,subject=session.get(Track,topic.track_id).slug,
                topic=topic.slug,level=1,kind=kind,purposes=["practice"],prompt=exercise.prompt_markdown,explanation=explanation,
                hints=json.loads(exercise.content_json).get("hints",[]),contract=contract)
            if not any(i.family==item.family for i,_,_ in items):items.append((item,revision,"legacy_unverified"))
    exposed={s.family for s in session.exec(select(AssessmentSelection))}
    from ..models import ArenaAttempt
    exposed.update("arena/"+a.problem_key for a in session.exec(select(ArenaAttempt)))
    from ..models import CourseExerciseBinding,ContentRevision,PracticeSessionExercise,ArenaHintUse
    for binding,revision in session.exec(select(CourseExerciseBinding,ContentRevision).join(ContentRevision,ContentRevision.id==CourseExerciseBinding.content_revision_id)
            .join(PracticeSessionExercise,PracticeSessionExercise.exercise_id==CourseExerciseBinding.exercise_id)):
        exposed.add(revision.content_key+"/"+binding.exercise_key)
    exposed.update("arena/"+h.problem_key for h in session.exec(select(ArenaHintUse)) if h.count)
    if purpose=="transfer":items=[p for p in items if p[0].independent_variant and p[0].family not in exposed and p[0].kind!="reflection"]
    if purpose=="recall":
        now=now or datetime.now(timezone.utc)
        def utc(value):return value.replace(tzinfo=timezone.utc) if value.tzinfo is None else value.astimezone(timezone.utc)
        recently_helped={s.family for s in session.exec(select(AssessmentSelection)) if (s.assisted or s.revealed or s.hints_used)
            and utc(now)-utc(s.completed_at or s.created_at)<timedelta(hours=24)}
        items=[p for p in items if p[0].family not in recently_helped]
    return sorted(items,key=lambda p:(p[0].family in exposed,p[0].key,p[1].id))
