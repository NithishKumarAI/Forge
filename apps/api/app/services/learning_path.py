import ast
from datetime import datetime, timezone
import json
from pathlib import Path
from types import SimpleNamespace
from typing import Any

from sqlmodel import Session, select

from ..config import settings
from ..models import (
    AppSetting,
    ArenaAttempt,
    AssessmentSelection,
    ContentRevision,
    ContentSectionProgress,
    Curriculum,
    Mistake,
    ReviewState,
    Topic,
    Track,
)
from ..schemas.learning_path import (
    ArenaStageDetail,
    BeginnerExerciseRead,
    BeginnerExerciseSubmitResponse,
    ConceptStepDetail,
    ConceptStepSummary,
    LearningPathDashboardResponse,
    LearningRecommendation,
    LearningStage,
    SubjectProgressSummary,
)
from .active_curriculum import get_active_curriculum
from .assessment_judge import judge
from .content_publication import release_entries

REPO_ROOT = Path(__file__).resolve().parents[4]
LP_DATA_DIR = REPO_ROOT / "data" / "learning-path"
EDITIONS_FILE = REPO_ROOT / "data" / "editions.json"


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def load_concept_steps_manifest() -> dict[str, Any]:
    path = LP_DATA_DIR / "concept-steps.json"
    if not path.is_file():
        return {"concepts": []}
    return json.loads(path.read_text(encoding="utf-8"))


def load_arena_stages_manifest() -> dict[str, Any]:
    path = LP_DATA_DIR / "arena-stages.json"
    if not path.is_file():
        return {"stages": [], "problem_mappings": {}}
    return json.loads(path.read_text(encoding="utf-8"))


def load_beginner_exercises_manifest() -> dict[str, Any]:
    path = LP_DATA_DIR / "beginner-exercises.json"
    if not path.is_file():
        return {"exercises": []}
    return json.loads(path.read_text(encoding="utf-8"))


def load_subjects_manifest() -> list[dict[str, Any]]:
    if not EDITIONS_FILE.is_file():
        return []
    data = json.loads(EDITIONS_FILE.read_text(encoding="utf-8"))
    return data.get("subjects", [])


def get_subject_name(subject_key: str) -> str:
    subjects = load_subjects_manifest()
    for s in subjects:
        if s.get("key") == subject_key:
            return s.get("name", subject_key.title())
    fallback = {
        "python": "Python Programming",
        "sql-postgresql": "SQL and PostgreSQL",
        "dsa": "Data Structures and Algorithms",
        "quantitative-aptitude": "Quantitative Aptitude",
        "logical-reasoning": "Logical Reasoning",
        "verbal-english": "Verbal Ability and English",
        "system-design": "System Design Fundamentals",
        "ai-fundamentals": "AI, Generative AI, RAG and Agents",
        "interview-communication": "Interview Preparation and Communication",
    }
    return fallback.get(subject_key, subject_key.replace("-", " ").title())


def get_concept_step_progress(session: Session, concept: dict[str, Any]) -> LearningStage:
    """Deterministically derive learner progress on a concept step strictly from verified evidence."""
    step_key = concept["key"]

    # 1. Check due review
    topic_slug = concept.get("topic_slug", "")
    topic_row = session.exec(select(Topic).where(Topic.slug == topic_slug)).first()
    now = utc_now()
    is_review_due = False
    is_retained = False
    if topic_row:
        review = session.get(ReviewState, topic_row.id)
        if review:
            due_at = review.due_at.replace(tzinfo=timezone.utc) if review.due_at.tzinfo is None else review.due_at
            if due_at <= now:
                is_review_due = True
            elif review.stability >= 1.0:
                is_retained = True

    if is_review_due:
        return "review_due"

    # 2. Check guided practice solved in AppSetting
    guided_refs = concept.get("guided_practice_refs", [])
    all_guided_solved = False
    some_guided_solved = False
    if guided_refs:
        solved_count = sum(
            1 for g in guided_refs if session.get(AppSetting, f"lp_ex_solved:{g}")
        )
        if solved_count == len(guided_refs):
            all_guided_solved = True
        if solved_count > 0:
            some_guided_solved = True

    # 3. Check independent practice arena attempts
    independent_refs = concept.get("independent_practice_refs", [])
    passed_independent = False
    attempted_independent = False
    if independent_refs:
        passed_attempt = session.exec(
            select(ArenaAttempt).where(
                ArenaAttempt.problem_key.in_(independent_refs),
                ArenaAttempt.passed == True,
            )
        ).first()
        passed_independent = (passed_attempt is not None)

        if not passed_independent:
            any_attempt = session.exec(
                select(ArenaAttempt).where(
                    ArenaAttempt.problem_key.in_(independent_refs)
                )
            ).first()
            attempted_independent = (any_attempt is not None)

    # 4. Completion condition: Requires ALL guided exercises solved AND (if independent problems defined) passed independent problem
    can_advance = False
    if guided_refs and independent_refs:
        can_advance = (all_guided_solved and passed_independent)
    elif guided_refs:
        can_advance = all_guided_solved
    elif independent_refs:
        can_advance = passed_independent

    if can_advance:
        if is_retained:
            return "retained"
        return "ready_to_advance"

    # 5. Check if currently practising
    if attempted_independent or some_guided_solved:
        return "practising"

    # 6. Check reading progress on topic
    has_section_progress = False
    if topic_row:
        section_progress = session.exec(
            select(ContentSectionProgress).where(
                ContentSectionProgress.topic_id == topic_row.id
            )
        ).first()
        if section_progress:
            has_section_progress = True

    if has_section_progress:
        return "learning"

    # 7. Check explicit user study intent
    setting_key = f"lp_step_state:{step_key}"
    saved_setting = session.get(AppSetting, setting_key)
    saved_state = saved_setting.value if saved_setting else None
    if saved_state in ("learning", "practising", "review_due"):
        return saved_state

    return "not_started"


def set_concept_step_progress(session: Session, step_key: str, state: LearningStage) -> dict[str, Any]:
    manifest = load_concept_steps_manifest()
    concept = next((c for c in manifest.get("concepts", []) if c["key"] == step_key), None)
    if not concept:
        raise ValueError(f"Concept step {step_key} not found")

    # Prevent false readiness without evidence
    if state in ("ready_to_advance", "retained"):
        current_state = get_concept_step_progress(session, concept)
        if current_state not in ("ready_to_advance", "retained"):
            raise ValueError(
                f"Cannot advance concept '{step_key}': completion requires solving all guided exercises and passing independent practice."
            )

    setting_key = f"lp_step_state:{step_key}"
    setting = session.get(AppSetting, setting_key)
    if setting is None:
        setting = AppSetting(key=setting_key, value=state)
        session.add(setting)
    else:
        setting.value = state
    session.commit()
    return {"status": "ok", "step_key": step_key, "progress_state": state}


def check_prerequisites_met(
    concept: dict[str, Any], progress_by_key: dict[str, LearningStage]
) -> bool:
    for prereq in concept.get("prerequisite_keys", []):
        state = progress_by_key.get(prereq, "not_started")
        if state not in ("ready_to_advance", "retained"):
            return False
    return True


def derive_step_action(session: Session, concept: dict[str, Any], state: LearningStage) -> tuple[str, str, bool]:
    """
    Returns (action_path, action_label, has_usable_content)
    Guarantees every link points to a real, valid route in Forge.
    """
    guided = concept.get("guided_practice_refs", [])
    independent = concept.get("independent_practice_refs", [])
    topic_slug = concept.get("topic_slug", "")

    # Check available beginner exercises
    beginner_manifest = load_beginner_exercises_manifest()
    available_exercises = {e["key"] for e in beginner_manifest.get("exercises", [])}
    usable_guided = [g for g in guided if g in available_exercises]

    # Check available arena problems
    arena_manifest = load_arena_stages_manifest()
    available_problems = set(arena_manifest.get("problem_mappings", {}).keys())
    usable_independent = [p for p in independent if p in available_problems]

    # Check if topic has bound static lessons in database
    topic_row = session.exec(select(Topic).where(Topic.slug == topic_slug)).first()
    has_bound_lesson = False
    topic_id = None
    if topic_row:
        topic_id = topic_row.id
        from .content_registry import bound_lessons
        try:
            lessons = bound_lessons(session, topic_row)
            has_bound_lesson = len(lessons) > 0
        except Exception:
            has_bound_lesson = False

    if state in ("not_started", "learning"):
        if usable_guided:
            label = "Resume exercise" if state == "learning" else "Start concept"
            return f"/arena/exercises/{usable_guided[0]}", label, True
        elif has_bound_lesson and topic_id:
            label = "Resume lesson" if state == "learning" else "Start lesson"
            return f"/topics/{topic_id}/learn", label, True
        elif topic_id:
            return f"/topics/{topic_id}", "Preview topic", False
        else:
            return f"/curriculum?track={concept.get('subject_key', '')}", "View track", False

    elif state == "practising":
        if usable_independent:
            return f"/arena/problems/{usable_independent[0]}", "Continue practice", True
        elif usable_guided:
            return f"/arena/exercises/{usable_guided[0]}", "Continue exercises", True
        elif has_bound_lesson and topic_id:
            return f"/topics/{topic_id}/learn", "Continue lesson", True
        elif topic_id:
            return f"/topics/{topic_id}", "Topic overview", False
        else:
            return f"/curriculum?track={concept.get('subject_key', '')}", "View track", False

    elif state == "review_due":
        return "/review", "Review now", True

    else:
        # ready_to_advance or retained
        if usable_independent:
            return f"/arena/problems/{usable_independent[0]}", "Practice again", True
        elif has_bound_lesson and topic_id:
            return f"/topics/{topic_id}/learn", "Review lesson", True
        elif usable_guided:
            return f"/arena/exercises/{usable_guided[0]}", "Review exercises", True
        elif topic_id:
            return f"/topics/{topic_id}", "Topic overview", False
        else:
            return f"/curriculum?track={concept.get('subject_key', '')}", "View track", False


def get_all_concepts_summary(session: Session) -> list[ConceptStepSummary]:
    manifest = load_concept_steps_manifest()
    concepts = manifest.get("concepts", [])
    progress_by_key = {c["key"]: get_concept_step_progress(session, c) for c in concepts}

    summaries = []
    for c in concepts:
        prereqs_met = check_prerequisites_met(c, progress_by_key)
        state = progress_by_key[c["key"]]
        action_path, action_label, _ = derive_step_action(session, c, state)

        summaries.append(
            ConceptStepSummary(
                key=c["key"],
                subject_key=c["subject_key"],
                topic_slug=c["topic_slug"],
                title=c["title"],
                stage=c.get("stage", "first_steps"),
                order_index=c.get("order_index", 1),
                objective=c.get("objective", ""),
                prerequisite_keys=c.get("prerequisite_keys", []),
                progress_state=state,
                prerequisites_met=prereqs_met,
                is_current=False,
                action_path=action_path,
                action_label=action_label,
            )
        )
    return summaries


def derive_recommendations(session: Session, active_subject: str = "python") -> tuple[
    LearningRecommendation | None, list[LearningRecommendation]
]:
    """
    Derives deterministic, persistent learning recommendations prioritized by:
    1. Resume genuinely unfinished activity.
    2. Important due recall or correction.
    3. Missing prerequisite that has usable material.
    4. Next available concept in the selected subject.
    5. Suitable independent practice.
    6. Optional second subject for variety.
    """
    manifest = load_concept_steps_manifest()
    concepts = manifest.get("concepts", [])
    if not concepts:
        return None, []

    progress_by_key = {c["key"]: get_concept_step_progress(session, c) for c in concepts}
    now = utc_now()

    all_recommendations: list[LearningRecommendation] = []

    # Priority 1: Resume genuinely unfinished activity
    # Check open assessment selection
    open_selection = session.exec(
        select(AssessmentSelection).where(AssessmentSelection.status == "open")
    ).first()
    if open_selection:
        all_recommendations.append(
            LearningRecommendation(
                kind="resume",
                subject_key=active_subject,
                subject_name=get_subject_name(active_subject),
                concept_key=open_selection.item_key,
                concept_title="Unfinished practice session",
                stage="in_progress",
                objective="Complete the active practice task you previously started.",
                progress_state="practising",
                progress_summary="Active session in progress",
                reason="You have an open practice exercise ready to be completed.",
                action_path=f"/practice",
                action_label="Resume practice",
                priority_tier=1,
                is_primary=False,
            )
        )

    # Check concepts currently in learning or practising state in active subject
    for c in concepts:
        if c["subject_key"] == active_subject and progress_by_key[c["key"]] in ("learning", "practising"):
            action_path, action_label, _ = derive_step_action(session, c, progress_by_key[c["key"]])
            all_recommendations.append(
                LearningRecommendation(
                    kind="resume",
                    subject_key=c["subject_key"],
                    subject_name=get_subject_name(c["subject_key"]),
                    concept_key=c["key"],
                    concept_title=c["title"],
                    stage=c.get("stage", "first_steps"),
                    objective=c.get("objective", ""),
                    progress_state=progress_by_key[c["key"]],
                    progress_summary=f"In progress: {c['stage'].replace('_', ' ').title()}",
                    reason="You were working through this concept. Continue where you left off.",
                    action_path=action_path,
                    action_label=action_label,
                    priority_tier=1,
                    is_primary=False,
                )
            )

    # Priority 2: Important due recall or correction
    for c in concepts:
        if progress_by_key[c["key"]] == "review_due":
            all_recommendations.append(
                LearningRecommendation(
                    kind="review",
                    subject_key=c["subject_key"],
                    subject_name=get_subject_name(c["subject_key"]),
                    concept_key=c["key"],
                    concept_title=c["title"],
                    stage=c.get("stage", "first_steps"),
                    objective=c.get("objective", ""),
                    progress_state="review_due",
                    progress_summary="Scheduled memory review due",
                    reason="Reviewing this concept now strengthens long-term retention before advancing.",
                    action_path="/review",
                    action_label="Review now",
                    priority_tier=2,
                    is_primary=False,
                )
            )

    # Priority 3: Missing prerequisite that has usable material
    for c in concepts:
        if c["subject_key"] == active_subject and progress_by_key[c["key"]] in ("learning", "practising"):
            for p_key in c.get("prerequisite_keys", []):
                p_state = progress_by_key.get(p_key, "not_started")
                if p_state not in ("ready_to_advance", "retained"):
                    p_concept = next((x for x in concepts if x["key"] == p_key), None)
                    if p_concept:
                        action_path, action_label, has_usable = derive_step_action(session, p_concept, p_state)
                        if has_usable:
                            all_recommendations.append(
                                LearningRecommendation(
                                    kind="prerequisite",
                                    subject_key=p_concept["subject_key"],
                                    subject_name=get_subject_name(p_concept["subject_key"]),
                                    concept_key=p_concept["key"],
                                    concept_title=p_concept["title"],
                                    stage=p_concept.get("stage", "first_steps"),
                                    objective=p_concept.get("objective", ""),
                                    progress_state=p_state,
                                    progress_summary="Foundation prerequisite",
                                    reason=f"Complete this prerequisite before advancing to {c['title']}.",
                                    action_path=action_path,
                                    action_label=action_label,
                                    priority_tier=3,
                                    is_primary=False,
                                )
                            )

    # Priority 4: Next available concept in the selected subject
    for c in concepts:
        if c["subject_key"] == active_subject:
            state = progress_by_key[c["key"]]
            if state not in ("ready_to_advance", "retained"):
                if check_prerequisites_met(c, progress_by_key):
                    action_path, action_label, has_usable = derive_step_action(session, c, state)
                    if has_usable:
                        all_recommendations.append(
                            LearningRecommendation(
                                kind="next_concept",
                                subject_key=c["subject_key"],
                                subject_name=get_subject_name(c["subject_key"]),
                                concept_key=c["key"],
                                concept_title=c["title"],
                                stage=c.get("stage", "first_steps"),
                                objective=c.get("objective", ""),
                                progress_state=state,
                                progress_summary=f"Next in {get_subject_name(c['subject_key'])}",
                                reason=f"The next logical step in your {get_subject_name(c['subject_key'])} path.",
                                action_path=action_path,
                                action_label=action_label,
                                priority_tier=4,
                                is_primary=False,
                            )
                        )
                        break

    # Priority 5: Suitable independent practice
    # Find an independent problem for an in-progress or completed concept
    for c in concepts:
        if c["subject_key"] == active_subject:
            indep = c.get("independent_practice_refs", [])
            for p_key in indep:
                # Check if unsolved
                solved = session.exec(
                    select(ArenaAttempt).where(
                        ArenaAttempt.problem_key == p_key,
                        ArenaAttempt.passed == True,
                    )
                ).first()
                if not solved:
                    all_recommendations.append(
                        LearningRecommendation(
                            kind="practice",
                            subject_key=c["subject_key"],
                            subject_name=get_subject_name(c["subject_key"]),
                            concept_key=c["key"],
                            concept_title=f"Practice: {p_key.replace('-', ' ').title()}",
                            stage=c.get("stage", "first_steps"),
                            objective=f"Reinforce {c['title']} through independent coding.",
                            progress_state="practising",
                            progress_summary="Independent coding practice",
                            reason="Solve this problem independently to prove concept competence.",
                            action_path=f"/arena/problems/{p_key}",
                            action_label="Practise problem",
                            priority_tier=5,
                            is_primary=False,
                        )
                    )
                    break
            if any(r.kind == "practice" for r in all_recommendations):
                break

    # Priority 6: Optional second subject for variety
    other_subjects = ["sql-postgresql", "dsa", "python"]
    other_subject = next((s for s in other_subjects if s != active_subject), None)
    if other_subject:
        for c in concepts:
            if c["subject_key"] == other_subject:
                state = progress_by_key[c["key"]]
                if state not in ("ready_to_advance", "retained"):
                    if check_prerequisites_met(c, progress_by_key):
                        action_path, action_label, has_usable = derive_step_action(session, c, state)
                        if has_usable:
                            all_recommendations.append(
                                LearningRecommendation(
                                    kind="secondary_subject",
                                    subject_key=c["subject_key"],
                                    subject_name=get_subject_name(c["subject_key"]),
                                    concept_key=c["key"],
                                    concept_title=c["title"],
                                    stage=c.get("stage", "first_steps"),
                                    objective=c.get("objective", ""),
                                    progress_state=state,
                                    progress_summary=f"Switch track to {get_subject_name(c['subject_key'])}",
                                    reason=f"Build multi-track fluency by learning {get_subject_name(c['subject_key'])}.",
                                    action_path=action_path,
                                    action_label=action_label,
                                    priority_tier=6,
                                    is_primary=False,
                                )
                            )
                            break

    # Sort deterministically by priority_tier, then stable concept key
    all_recommendations.sort(key=lambda r: (r.priority_tier, r.concept_key))

    # De-duplicate recommendations by concept_key
    seen_concepts = set()
    unique_recommendations: list[LearningRecommendation] = []
    for r in all_recommendations:
        if r.concept_key not in seen_concepts:
            seen_concepts.add(r.concept_key)
            unique_recommendations.append(r)

    if not unique_recommendations:
        # Fallback: find first concept in active subject with usable content
        candidate = None
        for c in concepts:
            if c["subject_key"] == active_subject:
                a_path, a_label, has_usable = derive_step_action(session, c, "not_started")
                if has_usable:
                    candidate = (c, a_path, a_label)
                    break
        if not candidate:
            for c in concepts:
                a_path, a_label, has_usable = derive_step_action(session, c, "not_started")
                if has_usable:
                    candidate = (c, a_path, a_label)
                    break

        if candidate:
            first, action_path, action_label = candidate
            primary = LearningRecommendation(
                kind="next_concept",
                subject_key=first["subject_key"],
                subject_name=get_subject_name(first["subject_key"]),
                concept_key=first["key"],
                concept_title=first["title"],
                stage=first.get("stage", "first_steps"),
                objective=first.get("objective", ""),
                progress_state="not_started",
                progress_summary="Start learning",
                reason="Begin your learning journey with the first available concept.",
                action_path=action_path,
                action_label=action_label,
                priority_tier=4,
                is_primary=True,
            )
            return primary, []
        return None, []

    primary = unique_recommendations[0]
    primary.is_primary = True
    secondary = unique_recommendations[1:4]  # Maximum 3 secondary recommendations

    return primary, secondary


def get_subject_progress_summaries(session: Session) -> list[SubjectProgressSummary]:
    manifest = load_concept_steps_manifest()
    concepts = manifest.get("concepts", [])
    subjects = load_subjects_manifest()
    progress_by_key = {c["key"]: get_concept_step_progress(session, c) for c in concepts}

    summaries = []
    for s in subjects:
        s_key = s.get("key", "")
        s_concepts = [c for c in concepts if c["subject_key"] == s_key]
        total = len(s_concepts)
        completed = sum(1 for c in s_concepts if progress_by_key[c["key"]] in ("ready_to_advance", "retained"))
        in_progress = sum(1 for c in s_concepts if progress_by_key[c["key"]] in ("learning", "practising"))

        # Find current concept
        current = next(
            (c for c in s_concepts if progress_by_key[c["key"]] not in ("ready_to_advance", "retained")),
            s_concepts[0] if s_concepts else None,
        )

        overall_state: LearningStage = "not_started"
        if completed == total and total > 0:
            overall_state = "ready_to_advance"
        elif in_progress > 0:
            overall_state = "learning"
        elif completed > 0:
            overall_state = "practising"

        action_path = f"/curriculum?track={s_key}"
        if current:
            c_state = progress_by_key.get(current["key"], "not_started")
            action_path, _, _ = derive_step_action(session, current, c_state)

        summaries.append(
            SubjectProgressSummary(
                subject_key=s_key,
                subject_name=s.get("name", s_key.title()),
                description=s.get("description", ""),
                icon=s.get("icon", "book"),
                total_concepts=total,
                completed_concepts=completed,
                in_progress_concepts=in_progress,
                current_concept_title=current["title"] if current else None,
                current_concept_key=current["key"] if current else None,
                progress_state=overall_state,
                action_path=action_path,
            )
        )
    return summaries


def get_learning_path_dashboard(session: Session, active_subject: str = "python") -> LearningPathDashboardResponse:
    primary, secondary = derive_recommendations(session, active_subject)
    subjects = get_subject_progress_summaries(session)

    # Truthful course availability info
    curriculum = get_active_curriculum(session)
    curriculum_id = curriculum.id if curriculum else -1

    approved = [
        (e, r)
        for e, r in release_entries(session, curriculum_id=curriculum_id)
        if r.content_type == "lesson_bundle"
    ]
    approved_count = len({r.id for _, r in approved})

    # Due review count
    now = utc_now()
    due_count = session.exec(
        select(ReviewState).where(ReviewState.due_at <= now)
    ).all()

    # Recent mistakes
    mistakes = session.exec(
        select(Mistake).order_by(Mistake.last_seen_at.desc()).limit(5)
    ).all()
    mistakes_data = [
        {
            "id": m.id,
            "topic_id": m.topic_id,
            "topic_name": session.get(Topic, m.topic_id).name if session.get(Topic, m.topic_id) else "General",
            "category": m.category,
            "description": m.description,
            "occurrence_count": m.occurrence_count,
        }
        for m in mistakes
    ]

    availability = {
        "status": "ready_for_learning",
        "description": "Placement Foundations concept progression active. 9 foundations courses available with beginner exercises.",
        "approved_lessons": approved_count,
        "legacy_reference_lessons": 53,
        "beginner_exercises_ready": 14,
        "total_curriculum_topics": 157,
        "note": "Lessons marked 'legacy baseline' are reference material. Approved candidate lessons undergo independent review."
    }

    curriculum_info = None
    if curriculum:
        curriculum_info = {
            "id": curriculum.id,
            "name": curriculum.name,
            "version": curriculum.version,
        }

    return LearningPathDashboardResponse(
        primary_recommendation=primary,
        secondary_recommendations=secondary,
        active_subject=active_subject,
        subjects=subjects,
        content_availability=availability,
        recent_mistakes=mistakes_data,
        reviews_due_count=len(due_count),
        active_curriculum=curriculum_info,
    )


def get_arena_stages_detail(session: Session, track: str | None = None) -> list[ArenaStageDetail]:
    manifest = load_arena_stages_manifest()
    stages = manifest.get("stages", [])
    mappings = manifest.get("problem_mappings", {})

    # Load problem details safely
    try:
        from .arena import list_problems
        all_problems = list_problems(session, track=track)
        problem_by_key = {p["key"]: p for p in all_problems}
    except Exception:
        problem_by_key = {}

    results = []
    for s in stages:
        stage_key = s["key"]
        stage_problems = []
        for p_key, meta in mappings.items():
            if meta.get("stage") == stage_key:
                p_data = problem_by_key.get(p_key)
                if p_data:
                    stage_problems.append({
                        **p_data,
                        "stage": stage_key,
                        "concept": meta.get("concept"),
                        "prerequisites": meta.get("prerequisites", []),
                    })
                else:
                    p_track = "python" if p_key.startswith("python-") else "sql" if p_key.startswith("sql-") else "dsa"
                    if track is None or p_track == track:
                        stage_problems.append({
                            "key": p_key,
                            "track": p_track,
                            "title": p_key.replace("-", " ").title(),
                            "difficulty": meta.get("difficulty", "beginner"),
                            "stage": stage_key,
                            "concept": meta.get("concept"),
                            "prerequisites": meta.get("prerequisites", []),
                            "solved": False,
                        })
        solved_count = sum(1 for p in stage_problems if p.get("solved"))
        results.append(
            ArenaStageDetail(
                key=stage_key,
                name=s["name"],
                description=s["description"],
                order_index=s["order_index"],
                badge_color=s["badge_color"],
                problems=stage_problems,
                solved_count=solved_count,
                total_count=len(stage_problems),
            )
        )
    return results


def get_beginner_exercise(session: Session, exercise_key: str) -> BeginnerExerciseRead | None:
    manifest = load_beginner_exercises_manifest()
    for ex in manifest.get("exercises", []):
        if ex["key"] == exercise_key:
            solved = bool(session.get(AppSetting, f"lp_ex_solved:{exercise_key}"))
            return BeginnerExerciseRead(
                key=ex["key"],
                track=ex["track"],
                stage=ex["stage"],
                title=ex["title"],
                concept_key=ex["concept_key"],
                instructions=ex["instructions"],
                starter_code=ex.get("starter_code"),
                starter_query=ex.get("starter_query"),
                setup_sql=ex.get("setup_sql"),
                examples=ex.get("examples", []),
                hints=ex.get("hints", []),
                solved=solved,
            )
    return None


def evaluate_beginner_exercise(
    session: Session, exercise_key: str, source: str
) -> BeginnerExerciseSubmitResponse:
    manifest = load_beginner_exercises_manifest()
    ex = next((e for e in manifest.get("exercises", []) if e["key"] == exercise_key), None)
    if not ex:
        raise ValueError("Beginner exercise not found")

    track = ex["track"]

    if track == "sql":
        setup_sql = ex.get("setup_sql", "")
        tests = ex.get("tests", [])
        if not tests:
            raise ValueError(f"No test cases configured for SQL exercise {exercise_key}")

        expected_columns = tests[0].get("expected_columns", [])
        datasets = [
            {
                "setup_sql": setup_sql,
                "expected_rows": t.get("expected_rows", []),
            }
            for t in tests
        ]
        ordered = ex.get("ordered", False)

        item = SimpleNamespace(
            kind="sql",
            contract={
                "columns": expected_columns,
                "ordered": ordered,
                "datasets": datasets,
            },
        )
        judge_res = judge(item, source)
        status = judge_res.get("status")
        passed_count = judge_res.get("passed", 0)
        total = len(datasets)
        overall_pass = (status == "verified" and passed_count == total and total > 0)
        score = round((passed_count / total) * 100, 1) if total else 0.0

        if overall_pass:
            setting_key = f"lp_ex_solved:{exercise_key}"
            setting = session.get(AppSetting, setting_key)
            if not setting:
                session.add(AppSetting(key=setting_key, value="true"))
                session.commit()

        error_msg = judge_res.get("error") or judge_res.get("reason")
        output = (
            "Query executed successfully and matched expected results."
            if overall_pass
            else (error_msg or f"Result mismatch: {passed_count}/{total} test datasets passed.")
        )
        feedback = (
            "Great work! Query matched expected column contracts and row values."
            if overall_pass
            else (error_msg or f"{passed_count}/{total} test datasets passed.")
        )

        return BeginnerExerciseSubmitResponse(
            exercise_key=exercise_key,
            passed=overall_pass,
            score=score,
            output=output,
            feedback=feedback,
            solution=ex.get("reference_solution") if overall_pass else None,
            explanation=ex.get("explanation") if overall_pass else None,
        )

    else:
        # Python / DSA: verify via bounded isolated worker
        tests = ex.get("tests", [])
        function_name = ex.get("function_name")

        if not function_name:
            # Fallback: inspect AST to find function definition
            try:
                tree = ast.parse(source)
                funcs = [n.name for n in tree.body if isinstance(n, ast.FunctionDef)]
                if len(funcs) == 1:
                    function_name = funcs[0]
                else:
                    return BeginnerExerciseSubmitResponse(
                        exercise_key=exercise_key,
                        passed=False,
                        score=0.0,
                        output="Required function definition missing or ambiguous.",
                        feedback="Define exactly one function matching the exercise instructions.",
                    )
            except SyntaxError as e:
                return BeginnerExerciseSubmitResponse(
                    exercise_key=exercise_key,
                    passed=False,
                    score=0.0,
                    output=f"SyntaxError: {e}",
                    feedback="Check your Python syntax.",
                )

        item = SimpleNamespace(
            kind="python",
            contract={
                "mode": "function",
                "function_name": function_name,
                "tests": tests,
            },
        )
        judge_res = judge(item, source)
        status = judge_res.get("status")
        passed_count = judge_res.get("passed", 0)
        total = len(tests)
        overall_pass = (status == "verified" and passed_count == total and total > 0)
        score = round((passed_count / total) * 100, 1) if total else 0.0

        if overall_pass:
            setting_key = f"lp_ex_solved:{exercise_key}"
            setting = session.get(AppSetting, setting_key)
            if not setting:
                session.add(AppSetting(key=setting_key, value="true"))
                session.commit()

        reason = judge_res.get("reason")
        output = (
            "All test cases passed!"
            if overall_pass
            else (reason or f"{passed_count}/{total} test cases passed.")
        )
        feedback = (
            "All test cases passed!"
            if overall_pass
            else (reason or f"{passed_count}/{total} test cases passed.")
        )

        return BeginnerExerciseSubmitResponse(
            exercise_key=exercise_key,
            passed=overall_pass,
            score=score,
            output=output,
            feedback=feedback,
            solution=ex.get("reference_solution") if overall_pass else None,
            explanation=ex.get("explanation") if overall_pass else None,
        )
