import json
from datetime import datetime, timezone
from pathlib import Path

from sqlmodel import Session, select

from ..config import settings
from ..models import (
    Curriculum, Exercise, InterviewQuestion, InterviewReport, InterviewResponse,
    InterviewSession, LearnerTopicState, LearningSession, PracticeSessionExercise,
    Topic, Track,
)
from ..providers import InvalidStructuredResponse, LLMProvider, ProviderError
from ..schemas.interview import InterviewEvaluation, InterviewQuestionProposal, InterviewReportNarrative
from ..schemas.practice import CodeSubmission
from .active_curriculum import get_active_curriculum
from .practice import public_exercise, submit_code
from .usage import record_usage


QUESTION_POLICY = """You are generating one question for a scored entry-level engineering interview.
Use only the supplied fixed competency, curriculum context, project profile, allowed type, and difficulty.
Do not teach, reveal an answer, change the rubric, invent project features, or discuss hiring probability.
For coding, return a compact standard-library exercise with empty hints and deterministic tests.
The question must be concise, practical, and answerable without external research."""

EVALUATION_POLICY = """Evaluate one scored interview answer against the supplied immutable rubric and expected concepts.
Return scores for exactly the named dimensions. Do not change weights, teach a perfect answer, infer personality,
or predict hiring outcomes. Request one non-leading contextual follow-up only when it would materially clarify depth."""

REPORT_POLICY = """Write a concise final interview summary from the supplied deterministic scores and findings.
Do not recalculate scores, add unsupported project claims, or mention hiring probability. This is Forge rubric feedback."""


def _slot(section: str, competency: str, allowed: list[str], weight: float, seconds: int = 180) -> dict:
    return {"section": section, "competency": competency, "allowed": allowed, "weight": weight, "suggested_seconds": seconds}


BLUEPRINTS = {
    "quick": {"title": "Quick Mock", "target_minutes": 18, "slots": [
        _slot("python_backend", "Python and backend fundamentals", ["technical_short_answer", "scenario"], .25),
        _slot("llm_rag", "LLM or RAG engineering fundamentals", ["technical_short_answer", "scenario"], .20),
        _slot("coding", "Python problem solving", ["python_code", "python_debug"], .25, 600),
        _slot("project", "Project architecture and engineering trade-offs", ["project"], .15, 240),
        _slot("behavioral", "Engineering ownership and reflection", ["behavioral"], .15, 240),
    ]},
    "full_ai_engineer": {"title": "Full AI Engineer", "target_minutes": 55, "slots": [
        _slot("python_backend", "Python, async APIs, reliability, and production debugging", ["technical_short_answer", "scenario"], .20),
        _slot("llm_rag", "LLM tool use, structured output, retrieval, and evaluation", ["technical_short_answer", "scenario"], .25),
        _slot("sql_cs", "SQL and computer-science fundamentals", ["technical_short_answer", "scenario"], .10),
        _slot("coding", "Python implementation or debugging", ["python_code", "python_debug"], .15, 720),
        _slot("project", "Project architecture and trade-offs", ["project"], .15, 300),
        _slot("system_design", "Entry-level AI system design", ["system_design"], .10, 480),
        _slot("behavioral", "Engineering ownership and communication", ["behavioral"], .05, 240),
    ]},
    "python_backend": {"title": "Python / Backend", "target_minutes": 35, "slots": [
        _slot("python", "Python language and unfamiliar-code reasoning", ["technical_short_answer", "scenario"], .20),
        _slot("backend", "FastAPI, HTTP, authentication, async, and external APIs", ["technical_short_answer", "scenario"], .25),
        _slot("sql", "SQL, transactions, and indexing", ["technical_short_answer", "scenario"], .15),
        _slot("coding", "Python implementation or debugging", ["python_code", "python_debug"], .30, 720),
        _slot("production", "Testing, failure handling, and production debugging", ["scenario"], .10),
    ]},
    "llm_rag": {"title": "LLM / RAG", "target_minutes": 35, "slots": [
        _slot("llm", "Tokens, structured output, tool calling, state, and approval", ["technical_short_answer", "scenario"], .30),
        _slot("reliability", "Retries, rate limits, latency, and cost", ["scenario"], .20),
        _slot("retrieval", "Embeddings, chunking, retrieval, and reranking", ["technical_short_answer", "scenario"], .25),
        _slot("evaluation", "Hallucination control and RAG evaluation", ["scenario"], .25),
    ]},
    "project_deep_dive": {"title": "Project Deep Dive", "target_minutes": 30, "slots": [
        _slot("project_architecture", "Project request-to-result architecture", ["project"], .30),
        _slot("project_reliability", "Project failure handling and approvals", ["project"], .25),
        _slot("project_tradeoffs", "Project choices, weaknesses, and trade-offs", ["project"], .25),
        _slot("project_evolution", "Practical next architectural improvement", ["project"], .20),
    ]},
    "system_design": {"title": "System Design Basics", "target_minutes": 30, "slots": [
        _slot("requirements", "Clarify requirements for a small AI service", ["system_design"], .20, 420),
        _slot("architecture", "Components, data flow, API boundaries, and storage", ["system_design"], .35, 480),
        _slot("reliability", "Failures, security, and trade-offs", ["system_design"], .30, 420),
        _slot("scaling", "Basic scaling awareness without hyperscale assumptions", ["system_design"], .15, 300),
    ]},
    "behavioral": {"title": "Behavioral", "target_minutes": 25, "slots": [
        _slot("debugging", "A difficult bug and how it was resolved", ["behavioral"], .25, 300),
        _slot("decision", "A technical decision that changed with evidence", ["behavioral"], .25, 300),
        _slot("learning", "Learning unfamiliar technology", ["behavioral"], .25, 300),
        _slot("prioritization", "Prioritization, ownership, and reflection", ["behavioral"], .25, 300),
    ]},
}


RUBRICS = {
    "technical_short_answer": [("correctness", .35), ("completeness", .25), ("reasoning", .20), ("practicality", .10), ("clarity", .10)],
    "scenario": [("correctness", .25), ("reasoning", .25), ("practicality", .25), ("failure_handling", .15), ("clarity", .10)],
    "project": [("accuracy", .30), ("architecture", .25), ("tradeoffs", .20), ("ownership", .15), ("clarity", .10)],
    "system_design": [("requirements", .15), ("architecture", .20), ("data_flow", .15), ("failure_handling", .15), ("security", .10), ("tradeoffs", .15), ("communication", .10)],
    "behavioral": [("clarity", .20), ("specificity", .25), ("ownership", .20), ("reflection", .20), ("structure", .15)],
    "python_code": [("correctness", 1.0)],
    "python_debug": [("correctness", 1.0)],
}


def modes() -> list[dict]:
    return [{"mode": key, "title": value["title"], "target_minutes": value["target_minutes"], "question_count": len(value["slots"])} for key, value in BLUEPRINTS.items()]


def _projects(path: Path | None = None) -> list[dict]:
    with (path or settings.projects_path).open(encoding="utf-8") as handle:
        return json.load(handle)["projects"]


def active_interview(session: Session) -> InterviewSession | None:
    return session.exec(select(InterviewSession).where(InterviewSession.status == "active").order_by(InterviewSession.started_at.desc())).first()


def assert_assessment_available(session: Session) -> None:
    if active_interview(session):
        raise ValueError("Forge tutoring and doubts are unavailable during a scored interview. Save or end the interview first.")


def _topic_for_slot(session: Session, curriculum_id: int, slot: dict) -> Topic | None:
    terms = set((slot["section"] + " " + slot["competency"]).lower().replace("/", " ").split())
    topics = session.exec(select(Topic).join(Track).where(Track.curriculum_id == curriculum_id)).all()
    def rank(topic: Topic) -> tuple:
        track = session.get(Track, topic.track_id)
        text = f"{track.slug} {track.name} {topic.name} {topic.description}".lower()
        matches = sum(1 for term in terms if len(term) > 2 and term in text)
        state = session.get(LearnerTopicState, topic.id) or LearnerTopicState(topic_id=topic.id)
        return (matches, topic.priority, -state.mastery_score, -topic.order_index)
    return max(topics, key=rank) if topics else None


def _difficulty(session: Session, topic: Topic | None) -> str:
    mastery = (session.get(LearnerTopicState, topic.id).mastery_score if topic and session.get(LearnerTopicState, topic.id) else 0)
    return "easy" if mastery < 40 else "medium" if mastery < 90 else "medium_deep"


def _fixed_rubric(question_type: str, competency: str) -> list[dict]:
    return [{"name": name, "weight": weight, "criteria": f"Demonstrates {name.replace('_', ' ')} for {competency}."} for name, weight in RUBRICS[question_type]]


def _question_context(session: Session, interview: InterviewSession, slot: dict, topic: Topic | None) -> tuple[str, dict | None]:
    project = None
    if slot["section"].startswith("project") or slot["section"] == "project":
        profiles = _projects()
        project_index = json.loads(interview.metadata_json or "{}").get("project_index", 0)
        project = profiles[project_index % len(profiles)]
    context = {
        "fixed_competency": slot["competency"], "allowed_question_types": slot["allowed"],
        "difficulty": _difficulty(session, topic),
        "topic": None if not topic else {"id": topic.id, "name": topic.name, "description": topic.description, "target_level": topic.target_level},
        "project_profile": project,
        "fixed_rubric": {kind: _fixed_rubric(kind, slot["competency"]) for kind in slot["allowed"]},
    }
    return json.dumps(context, indent=2), project


def _generate_question(session: Session, interview: InterviewSession, provider: LLMProvider, slot_index: int) -> InterviewQuestion:
    blueprint = BLUEPRINTS[interview.mode]; slot = blueprint["slots"][slot_index]
    topic = _topic_for_slot(session, interview.curriculum_id, slot)
    context, project = _question_context(session, interview, slot, topic)
    prompt = f"Generate exactly one interview question from this authoritative JSON context:\n{context}"
    last_error = None
    for attempt in range(2):
        try:
            proposal, result = provider.generate_structured(
                system_instruction=QUESTION_POLICY, prompt=prompt,
                thinking_level=settings.gemini_interview_thinking,
                response_model=InterviewQuestionProposal,
            )
            if proposal.competency != slot["competency"] or proposal.question_type not in slot["allowed"]:
                raise InvalidStructuredResponse("Question changed the fixed competency or allowed type")
            if proposal.difficulty != _difficulty(session, topic):
                raise InvalidStructuredResponse("Question changed the assigned difficulty")
            if project and project["name"].lower() not in proposal.question.lower():
                raise InvalidStructuredResponse("Project question must name the grounded project")
            rubric = _fixed_rubric(proposal.question_type, slot["competency"])
            exercise_id = learning_session_id = None
            prompt_markdown = proposal.question
            if proposal.coding_exercise:
                coding = proposal.coding_exercise
                coding.hints = []
                if topic is None:
                    raise InvalidStructuredResponse("Coding question requires a mapped curriculum topic")
                track = session.get(Track, topic.track_id)
                exercise = Exercise(
                    curriculum_id=interview.curriculum_id, track_id=track.id, topic_id=topic.id,
                    exercise_type=coding.exercise_type, title=coding.title,
                    prompt_markdown=coding.prompt_markdown, difficulty="interview", source="interview",
                    generator_model=result.model, generator_version="phase5-v1", validation_status="pending",
                    content_json=json.dumps({"key": coding.key, "hints": [], "content": coding.content.model_dump()}),
                )
                session.add(exercise); session.flush(); exercise_id = exercise.id
                learning = LearningSession(topic_id=topic.id, mode="interview")
                session.add(learning); session.flush(); learning_session_id = learning.id
                session.add(PracticeSessionExercise(session_id=learning.id, exercise_id=exercise.id, order_index=0))
                prompt_markdown = coding.prompt_markdown
            order = len(session.exec(select(InterviewQuestion).where(InterviewQuestion.session_id == interview.id)).all())
            question = InterviewQuestion(
                session_id=interview.id, section=slot["section"], competency=slot["competency"],
                question_type=proposal.question_type, prompt_markdown=prompt_markdown,
                topic_id=topic.id if topic else None, exercise_id=exercise_id, learning_session_id=learning_session_id,
                rubric_json=json.dumps(rubric), expected_concepts_json=json.dumps(proposal.expected_concepts),
                difficulty=proposal.difficulty, suggested_seconds=slot["suggested_seconds"],
                blueprint_slot=slot_index, order_index=order,
            )
            session.add(question); session.commit(); session.refresh(question)
            record_usage(session, provider, result, purpose="interview_question_repair" if attempt else "interview_question_generation", thinking_level=settings.gemini_interview_thinking)
            return question
        except (InvalidStructuredResponse, ValueError) as exc:
            last_error = exc
            if attempt:
                break
            prompt += f"\nRepair the complete response without changing the authoritative fields. Error: {str(exc)[:1000]}"
    raise ProviderError("Interview question generation returned invalid structured output. Try again.") from last_error


def start_interview(session: Session, mode: str, provider: LLMProvider) -> InterviewSession:
    if mode not in BLUEPRINTS:
        raise ValueError("Unknown interview mode")
    current = active_interview(session)
    if current:
        if current.mode == mode:
            return current
        raise ValueError(f"Interview {current.id} is already active. Resume, save, or end it first.")
    curriculum = get_active_curriculum(session)
    if not curriculum:
        raise ValueError("No active confirmed curriculum")
    interview = InterviewSession(curriculum_id=curriculum.id, mode=mode, metadata_json=json.dumps({"blueprint_version": 1, "project_index": 0}))
    session.add(interview); session.commit(); session.refresh(interview)
    try:
        _generate_question(session, interview, provider, 0)
    except Exception:
        interview.status = "generation_failed"; interview.completed_at = datetime.now(timezone.utc)
        session.add(interview); session.commit()
        raise
    return interview


def _questions(session: Session, interview_id: int) -> list[InterviewQuestion]:
    return session.exec(select(InterviewQuestion).where(InterviewQuestion.session_id == interview_id).order_by(InterviewQuestion.order_index)).all()


def current_question(session: Session, interview: InterviewSession) -> InterviewQuestion | None:
    for question in _questions(session, interview.id):
        if not session.exec(select(InterviewResponse).where(InterviewResponse.question_id == question.id)).first():
            return question
    return None


def _public_question(session: Session, question: InterviewQuestion | None) -> dict | None:
    if not question:
        return None
    return {
        "id": question.id, "section": question.section, "competency": question.competency,
        "question_type": question.question_type, "prompt_markdown": question.prompt_markdown,
        "difficulty": question.difficulty, "suggested_seconds": question.suggested_seconds,
        "order_index": question.order_index, "is_follow_up": question.follow_up_of_id is not None,
        "exercise": public_exercise(session.get(Exercise, question.exercise_id)) if question.exercise_id else None,
    }


def interview_read(session: Session, interview: InterviewSession) -> dict:
    blueprint = BLUEPRINTS[interview.mode]; questions = _questions(session, interview.id)
    answered = sum(1 for question in questions if session.exec(select(InterviewResponse).where(InterviewResponse.question_id == question.id)).first())
    return {
        "id": interview.id, "mode": interview.mode, "title": blueprint["title"], "status": interview.status,
        "target_minutes": blueprint["target_minutes"], "main_question_count": len(blueprint["slots"]),
        "answered_count": answered, "current_question": _public_question(session, current_question(session, interview)),
        "can_complete": current_question(session, interview) is None and len([q for q in questions if q.follow_up_of_id is None]) >= len(blueprint["slots"]),
        "started_at": interview.started_at, "completed_at": interview.completed_at, "overall_score": interview.overall_score,
    }


def _evaluate(session: Session, question: InterviewQuestion, answer: str, provider: LLMProvider) -> tuple[dict, float]:
    rubric = json.loads(question.rubric_json); expected = json.loads(question.expected_concepts_json)
    prompt = json.dumps({"question": question.prompt_markdown, "competency": question.competency, "rubric": rubric, "expected_concepts": expected, "learner_answer": answer}, indent=2)
    last_error = None
    for attempt in range(2):
        try:
            value, result = provider.generate_structured(system_instruction=EVALUATION_POLICY, prompt=prompt, thinking_level=settings.gemini_interview_evaluation_thinking, response_model=InterviewEvaluation)
            expected_names = {item["name"] for item in rubric}
            if set(value.dimension_scores) != expected_names:
                raise InvalidStructuredResponse("Evaluation must score exactly the fixed rubric dimensions")
            if question.follow_up_of_id is not None:
                value.follow_up_needed = False; value.recommended_follow_up = None; value.follow_up_reason = None
            score = round(sum(value.dimension_scores[item["name"]] * item["weight"] for item in rubric), 1)
            payload = value.model_dump(); payload["score"] = score; payload["rubric"] = rubric
            record_usage(session, provider, result, purpose="interview_evaluation_repair" if attempt else "interview_evaluation", thinking_level=settings.gemini_interview_evaluation_thinking)
            return payload, score
        except (InvalidStructuredResponse, ValueError) as exc:
            last_error = exc
            if attempt:
                break
            prompt += f"\nReturn a corrected complete evaluation. Error: {str(exc)[:1000]}"
    raise ProviderError("Interview evaluation returned invalid structured output. Try again.") from last_error


def _add_follow_up(session: Session, question: InterviewQuestion, evaluation: dict) -> None:
    if not evaluation.get("follow_up_needed") or question.follow_up_of_id is not None:
        return
    existing = session.exec(select(InterviewQuestion).where(InterviewQuestion.follow_up_of_id == question.id)).first()
    if existing:
        return
    order = len(_questions(session, question.session_id))
    session.add(InterviewQuestion(
        session_id=question.session_id, section=question.section, competency=question.competency,
        question_type="scenario" if question.question_type != "behavioral" else "behavioral",
        prompt_markdown=evaluation["recommended_follow_up"], topic_id=question.topic_id,
        follow_up_of_id=question.id, rubric_json=question.rubric_json,
        expected_concepts_json=question.expected_concepts_json, difficulty=question.difficulty,
        suggested_seconds=min(question.suggested_seconds, 180), blueprint_slot=question.blueprint_slot,
        order_index=order, generated_by="evaluation_follow_up",
    ))
    session.commit()


def _ensure_next_main(session: Session, interview: InterviewSession, provider: LLMProvider) -> None:
    if current_question(session, interview):
        return
    main = [q for q in _questions(session, interview.id) if q.follow_up_of_id is None]
    if len(main) < len(BLUEPRINTS[interview.mode]["slots"]):
        _generate_question(session, interview, provider, len(main))


def prepare_next(session: Session, interview: InterviewSession, provider: LLMProvider) -> dict:
    if interview.status != "active":
        raise ValueError("Interview is not active")
    _ensure_next_main(session, interview, provider)
    return interview_read(session, interview)


def answer_current(session: Session, interview: InterviewSession, answer: str, duration_seconds: int | None, provider: LLMProvider) -> dict:
    if interview.status != "active":
        raise ValueError("Interview is not active")
    question = current_question(session, interview)
    if not question or question.question_type in {"python_code", "python_debug"}:
        raise ValueError("Current question requires a coding submission")
    evaluation, score = _evaluate(session, question, answer, provider)
    session.add(InterviewResponse(question_id=question.id, response_text=answer, score=score, evaluation_json=json.dumps(evaluation), duration_seconds=duration_seconds))
    session.commit(); _add_follow_up(session, question, evaluation)
    try: _ensure_next_main(session, interview, provider)
    except ProviderError: pass  # The recorded answer remains safe; /next can retry generation.
    return interview_read(session, interview)


def submit_current_code(session: Session, interview: InterviewSession, source: str, execution, duration_seconds: int | None, provider: LLMProvider) -> dict:
    if interview.status != "active":
        raise ValueError("Interview is not active")
    question = current_question(session, interview)
    if not question or question.question_type not in {"python_code", "python_debug"}:
        raise ValueError("Current question is not coding")
    exercise = session.get(Exercise, question.exercise_id)
    attempt = submit_code(session, exercise, CodeSubmission(session_id=question.learning_session_id, source=source, execution=execution), evidence_type="none")
    score = float(attempt["score"] or 0)
    evaluation = {"score": score, "rubric": json.loads(question.rubric_json), "strengths": ["Deterministic tests passed."] if score >= 70 else [], "missing_concepts": [], "misconceptions": [], "feedback": attempt["feedback"], "follow_up_needed": False}
    session.add(InterviewResponse(question_id=question.id, response_text=None, attempt_id=attempt["attempt_id"], score=score, evaluation_json=json.dumps(evaluation), duration_seconds=duration_seconds))
    session.commit()
    try: _ensure_next_main(session, interview, provider)
    except ProviderError: pass  # Preserve the deterministic coding result and allow retry.
    return interview_read(session, interview)


def _deterministic_report(session: Session, interview: InterviewSession) -> dict:
    blueprint = BLUEPRINTS[interview.mode]; questions = _questions(session, interview.id)
    responses = {row.question_id: row for row in session.exec(select(InterviewResponse).join(InterviewQuestion).where(InterviewQuestion.session_id == interview.id)).all()}
    section_scores = {}
    for slot_index, slot in enumerate(blueprint["slots"]):
        values = [responses[q.id].score for q in questions if q.blueprint_slot == slot_index and q.id in responses]
        section_scores[slot["section"]] = round(sum(values) / len(values), 1) if values else 0
    overall = round(sum(section_scores[slot["section"]] * slot["weight"] for slot in blueprint["slots"]), 1)
    findings = [json.loads(response.evaluation_json) for response in responses.values()]
    strengths = list(dict.fromkeys(item for finding in findings for item in finding.get("strengths", [])))[:6]
    gaps = []
    recommendations = []
    for question in questions:
        response = responses.get(question.id)
        if not response or response.score >= 70:
            continue
        evaluation = json.loads(response.evaluation_json)
        gaps.extend(evaluation.get("missing_concepts", []) or [question.competency])
        if question.topic_id and all(item["topic_id"] != question.topic_id for item in recommendations):
            topic = session.get(Topic, question.topic_id)
            recommendations.append({"topic_id": topic.id, "topic_name": topic.name, "reason": f"Interview evidence in {question.competency}: {response.score:.0f}%."})
    return {
        "label": "Forge Interview Score", "overall_score": overall, "section_scores": section_scores,
        "strengths": strengths, "priority_gaps": list(dict.fromkeys(gaps))[:8],
        "communication_feedback": [], "recommended_topics": recommendations[:6],
        "summary": "This score reflects Forge's fixed interview rubric, not hiring probability or employer judgement.",
        "disclaimer": "Forge Interview Score is not a hiring probability.",
    }


def complete_interview(session: Session, interview: InterviewSession, provider: LLMProvider | None) -> dict:
    if interview.status != "active":
        report = session.exec(select(InterviewReport).where(InterviewReport.session_id == interview.id)).first()
        if report:
            return json.loads(report.report_json)
        raise ValueError("Interview is not active")
    _ensure_next_main(session, interview, provider) if provider else None
    if current_question(session, interview) or len([q for q in _questions(session, interview.id) if q.follow_up_of_id is None]) < len(BLUEPRINTS[interview.mode]["slots"]):
        raise ValueError("Answer all blueprint questions before completing the interview")
    report_data = _deterministic_report(session, interview)
    if provider:
        try:
            narrative, result = provider.generate_structured(system_instruction=REPORT_POLICY, prompt=json.dumps(report_data, indent=2), thinking_level=settings.gemini_interview_evaluation_thinking, response_model=InterviewReportNarrative)
            report_data["summary"] = narrative.summary
            report_data["communication_feedback"] = narrative.communication_feedback
            record_usage(session, provider, result, purpose="interview_report", thinking_level=settings.gemini_interview_evaluation_thinking)
        except ProviderError:
            pass
    now = datetime.now(timezone.utc); started = interview.started_at.replace(tzinfo=timezone.utc) if interview.started_at.tzinfo is None else interview.started_at
    interview.status = "completed"; interview.completed_at = now; interview.overall_score = report_data["overall_score"]; interview.duration_seconds = max(0, int((now - started).total_seconds()))
    session.add(interview); session.add(InterviewReport(session_id=interview.id, report_json=json.dumps(report_data))); session.commit()
    return report_data


def save_interview(session: Session, interview: InterviewSession) -> None:
    if interview.status != "active": raise ValueError("Only an active interview can be saved")
    interview.status = "saved"; session.add(interview); session.commit()


def resume_interview(session: Session, interview: InterviewSession) -> None:
    if interview.status != "saved": raise ValueError("Only a saved interview can be resumed")
    if active_interview(session): raise ValueError("Another interview is already active")
    interview.status = "active"; session.add(interview); session.commit()


def abandon_interview(session: Session, interview: InterviewSession) -> None:
    if interview.status not in {"active", "saved"}: raise ValueError("Interview cannot be ended")
    interview.status = "abandoned"; interview.completed_at = datetime.now(timezone.utc); session.add(interview); session.commit()


def report_for(session: Session, interview_id: int) -> dict:
    report = session.exec(select(InterviewReport).where(InterviewReport.session_id == interview_id)).first()
    if not report: raise ValueError("Interview report is not available")
    return json.loads(report.report_json)


def history(session: Session, curriculum_id: int | None = None) -> list[dict]:
    query = select(InterviewSession).order_by(InterviewSession.started_at.desc())
    if curriculum_id: query = query.where(InterviewSession.curriculum_id == curriculum_id)
    rows = session.exec(query).all()
    return [{"id": item.id, "mode": item.mode, "title": BLUEPRINTS.get(item.mode, {}).get("title", item.mode), "status": item.status, "started_at": item.started_at, "completed_at": item.completed_at, "overall_score": item.overall_score} for item in rows]
