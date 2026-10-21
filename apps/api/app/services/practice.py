import json
from sqlmodel import Session,select
from ..models import Attempt,Exercise,ExerciseAttemptDetail,LearningSession,PracticeSessionExercise
from .course import current_course_exercise_ids

class PracticeError(ValueError):
    pass


def start_practice(session,topic):
    """Compatibility for static course tooling; no generation or provider use."""
    ids=sorted(current_course_exercise_ids(session,topic.id))[:3]
    if not ids:raise PracticeError("No static practice available")
    learning=LearningSession(topic_id=topic.id,mode="practice")
    session.add(learning);session.flush()
    for index,key in enumerate(ids):session.add(PracticeSessionExercise(session_id=learning.id,exercise_id=key,order_index=index))
    session.commit()
    return learning,[session.get(Exercise,key) for key in ids]

def _content(exercise):
    return json.loads(exercise.content_json)

def public_exercise(exercise: Exercise) -> dict:
    stored = _content(exercise)
    content = stored["content"]
    kind = exercise.exercise_type
    if kind == "multiple_choice":
        exposed = {"choices": content["choices"]}
    elif kind == "short_answer":
        exposed = {}
    else:
        exposed = {
            "starter_code": content.get("starter_code") or content.get("broken_code"),
            "function_name": content["function_name"],
            "sample_tests": content["sample_tests"],
            "time_limit_ms": content["time_limit_ms"],
        }
    return {
        "id": exercise.id,
        "topic_id": exercise.topic_id,
        "exercise_type": kind,
        "title": exercise.title,
        "prompt_markdown": exercise.prompt_markdown,
        "difficulty": exercise.difficulty,
        "hints_available": len(stored["hints"]),
        "validation_status": exercise.validation_status,
        "content": exposed,
    }



def attempt_to_dict(attempt: Attempt, detail: ExerciseAttemptDetail, exercise: Exercise) -> dict:
    pending = detail.evaluation_status != "complete"
    return {
        "attempt_id": attempt.id,
        "session_id": detail.session_id,
        "exercise_id": exercise.id,
        "exercise_title": exercise.title,
        "exercise_type": exercise.exercise_type,
        "score": None if pending else attempt.score,
        "passed": None if pending else attempt.passed,
        "hints_used_count": detail.hints_used_count,
        "grading_source": detail.grading_source,
        "evaluation_status": detail.evaluation_status,
        "feedback": detail.feedback,
        "created_at": attempt.created_at,
    }



def practice_history(session: Session, topic_id: int) -> dict:
    attempts = session.exec(
        select(Attempt)
        .where(Attempt.topic_id == topic_id)
        .order_by(Attempt.created_at.desc(), Attempt.id.desc())
    ).all()
    rows = []
    for attempt in attempts:
        detail = session.get(ExerciseAttemptDetail, attempt.id)
        if detail is None:
            continue
        exercise = session.get(Exercise, detail.exercise_id)
        if exercise:
            rows.append(attempt_to_dict(attempt, detail, exercise))
    from ..models import AssessmentSelection
    for selected in session.exec(select(AssessmentSelection).where(AssessmentSelection.topic_id==topic_id,AssessmentSelection.purpose!="interview",AssessmentSelection.attempt_id!=None)):
        attempt=session.get(Attempt,selected.attempt_id)
        result=json.loads(selected.result_json)
        item=json.loads(selected.snapshot_json)
        rows.append({"attempt_id":attempt.id,"session_id":selected.session_id,"exercise_id":0,"exercise_title":item["key"],
            "exercise_type":item["kind"],"score":result.get("score"),"passed":result.get("passed"),"hints_used_count":selected.hints_used,
            "grading_source":result.get("verification","reflection"),"evaluation_status":selected.status,
            "feedback":result.get("explanation",""),"created_at":attempt.created_at})
    rows.sort(key=lambda r:r["attempt_id"],reverse=True)
    scored = [row["score"] for row in rows[:10] if row["score"] is not None]
    return {
        "attempts": rows,
        "attempt_count": len(rows),
        "recent_average": round(sum(scored) / len(scored), 1) if scored else None,
        "last_practiced_at": rows[0]["created_at"] if rows else None,
    }
