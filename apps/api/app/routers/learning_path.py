from typing import Any, Literal
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session

from ..database import get_session
from ..schemas.learning_path import (
    ArenaStageDetail,
    BeginnerExerciseRead,
    BeginnerExerciseSubmitRequest,
    BeginnerExerciseSubmitResponse,
    ConceptStepDetail,
    ConceptStepSummary,
    LearningPathDashboardResponse,
    LearningStage,
    SubjectProgressSummary,
)
from ..services.learning_path import (
    evaluate_beginner_exercise,
    get_all_concepts_summary,
    get_arena_stages_detail,
    get_beginner_exercise,
    get_concept_step_progress,
    get_learning_path_dashboard,
    get_subject_progress_summaries,
    load_concept_steps_manifest,
    set_concept_step_progress,
)

router = APIRouter(prefix="/api/learning-path", tags=["learning-path"])


@router.get("/dashboard", response_model=LearningPathDashboardResponse)
def dashboard(
    active_subject: str = Query("python", pattern=r"^[a-z0-9-]+$"),
    session: Session = Depends(get_session),
) -> LearningPathDashboardResponse:
    return get_learning_path_dashboard(session, active_subject=active_subject)


@router.get("/subjects", response_model=list[SubjectProgressSummary])
def subjects(session: Session = Depends(get_session)) -> list[SubjectProgressSummary]:
    return get_subject_progress_summaries(session)


@router.get("/subjects/{subject_key}", response_model=list[ConceptStepSummary])
def subject_concepts(
    subject_key: str, session: Session = Depends(get_session)
) -> list[ConceptStepSummary]:
    all_concepts = get_all_concepts_summary(session)
    filtered = [c for c in all_concepts if c.subject_key == subject_key]
    return filtered


@router.get("/steps/{step_key}", response_model=ConceptStepDetail)
def concept_step(
    step_key: str, session: Session = Depends(get_session)
) -> ConceptStepDetail:
    manifest = load_concept_steps_manifest()
    concept = next((c for c in manifest.get("concepts", []) if c["key"] == step_key), None)
    if not concept:
        raise HTTPException(status_code=404, detail="Concept step not found")

    state = get_concept_step_progress(session, concept)
    all_concepts = get_all_concepts_summary(session)
    summary = next((c for c in all_concepts if c.key == step_key), None)

    return ConceptStepDetail(
        key=concept["key"],
        subject_key=concept["subject_key"],
        topic_slug=concept["topic_slug"],
        title=concept["title"],
        stage=concept.get("stage", "first_steps"),
        order_index=concept.get("order_index", 1),
        objective=concept.get("objective", ""),
        prerequisite_keys=concept.get("prerequisite_keys", []),
        progress_state=state,
        prerequisites_met=summary.prerequisites_met if summary else True,
        is_current=summary.is_current if summary else False,
        action_path=summary.action_path if summary else "",
        action_label=summary.action_label if summary else "Start",
        teaching_ref=concept.get("teaching_ref"),
        worked_example=concept.get("worked_example"),
        guided_practice_refs=concept.get("guided_practice_refs", []),
        independent_practice_refs=concept.get("independent_practice_refs", []),
        availability_status=concept.get("availability_status", "available"),
        review_eligible=concept.get("review_eligible", True),
    )


@router.post("/steps/{step_key}/progress")
def update_step_progress(
    step_key: str,
    state: LearningStage,
    session: Session = Depends(get_session),
) -> dict[str, Any]:
    manifest = load_concept_steps_manifest()
    concept = next((c for c in manifest.get("concepts", []) if c["key"] == step_key), None)
    if not concept:
        raise HTTPException(status_code=404, detail="Concept step not found")

    set_concept_step_progress(session, step_key, state)
    return {"status": "ok", "step_key": step_key, "progress_state": state}


@router.get("/arena/stages", response_model=list[ArenaStageDetail])
def arena_stages(
    track: str | None = None, session: Session = Depends(get_session)
) -> list[ArenaStageDetail]:
    return get_arena_stages_detail(session, track=track)


@router.get("/exercises/{exercise_key}", response_model=BeginnerExerciseRead)
def get_exercise(
    exercise_key: str, session: Session = Depends(get_session)
) -> BeginnerExerciseRead:
    ex = get_beginner_exercise(session, exercise_key)
    if not ex:
        raise HTTPException(status_code=404, detail="Beginner exercise not found")
    return ex


@router.post("/exercises/{exercise_key}/submit", response_model=BeginnerExerciseSubmitResponse)
def submit_exercise(
    exercise_key: str,
    request: BeginnerExerciseSubmitRequest,
    session: Session = Depends(get_session),
) -> BeginnerExerciseSubmitResponse:
    try:
        return evaluate_beginner_exercise(session, exercise_key, request.source)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e
