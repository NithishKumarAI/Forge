"""Synthetic legacy learner data; no access to the learner's actual database."""
import json
from datetime import datetime, timezone, timedelta

from sqlmodel import Session, select
from fsrs import Card

from app import models as m
from app.config import settings
from app.migrations.v001_legacy_schema import SCHEMA
from app.services.curriculum import seed_default_curriculum

LEGACY_TABLES = [item["name"] for item in json.loads(SCHEMA.read_text())]


def rows(engine, tables=LEGACY_TABLES):
    with engine.connect() as connection:
        return {table: [tuple(row) for row in connection.exec_driver_sql(f'SELECT * FROM "{table}"')]
                for table in tables}


def seed_history(engine):
    with Session(engine) as session:
        old = seed_default_curriculum(session, settings.curriculum_path)
        new = seed_default_curriculum(session, settings.curriculum_v2_path)
        track = session.exec(select(m.Track).where(m.Track.curriculum_id == old.id, m.Track.slug == "python")).one()
        topic = session.exec(select(m.Topic).where(m.Topic.track_id == track.id, m.Topic.slug == "syntax-data-types")).one()
        new_track = session.exec(select(m.Track).where(m.Track.curriculum_id == new.id, m.Track.slug == "python")).one()
        new_topic = session.exec(select(m.Topic).where(m.Topic.track_id == new_track.id, m.Topic.slug == "foundations")).one()
        now = datetime(2026, 1, 2, 12, tzinfo=timezone.utc)
        state = session.get(m.LearnerTopicState, topic.id)
        state.mastery_score, state.attempts, state.confidence, state.status = 63, 2, "medium", "working"
        state.next_review_at = now + timedelta(days=2)
        session.add(state)
        session.add(m.TopicMigrationMap(old_topic_id=topic.id, new_topic_id=new_topic.id, mapping_key="historical lineage"))
        setting = session.get(m.AppSetting, "active_curriculum_id")
        setting.value = str(old.id)
        session.add(setting)
        session.add(m.AppSetting(key="daily_study_target", value="360"))
        session.add(m.CurriculumGenerationMetadata(curriculum_id=old.id, goal="legacy goal", source_requirements="saved input"))
        lesson = json.loads((settings.course_content_path / "python/syntax-data-types/lesson.json").read_text())
        item = json.loads((settings.course_content_path / "python/syntax-data-types/exercises.json").read_text())[0]
        session.add(m.CourseLesson(curriculum_id=old.id, topic_id=topic.id, content_version=lesson["version"],
                                   title="Historical metadata title", source_path="historical-path.json", content_hash="historical-hash"))
        exercise = m.Exercise(curriculum_id=old.id, track_id=track.id, topic_id=topic.id, source="course_pack",
                              title=item["title"], prompt_markdown=item["prompt_markdown"], exercise_type=item["exercise_type"],
                              difficulty=item["difficulty"], generator_version=f"course-pack:{lesson['version']}:{item['key']}",
                              content_json=json.dumps({"key":item["key"],"hints":item.get("hints",[]),"content":item["content"]},indent=2))
        stale = m.Exercise(curriculum_id=old.id, track_id=track.id, topic_id=topic.id, source="course_pack",
                           title="Stale historical item", prompt_markdown="Preserve this old session question.",
                           exercise_type="multiple_choice", difficulty="working", content_json='{"key":"old","hints":[],"content":{"choices":["A","B"],"correct_index":0,"explanation":"Old."}}')
        learning = m.LearningSession(topic_id=topic.id, mode="practice", started_at=now)
        session.add_all([exercise, stale, learning]);session.flush()
        session.add(m.PracticeSessionExercise(session_id=learning.id,exercise_id=exercise.id,order_index=0))
        session.add(m.PracticeHintUse(session_id=learning.id,exercise_id=exercise.id,count=1))
        for status, score in [("complete", 80), ("pending", 0)]:
            attempt = m.Attempt(topic_id=topic.id,attempt_type="practice",score=score,passed=status=="complete",created_at=now)
            session.add(attempt);session.flush()
            session.add(m.ExerciseAttemptDetail(attempt_id=attempt.id,exercise_id=exercise.id,session_id=learning.id,
                answer="historical answer",hints_used_count=1,feedback="old feedback",grading_source="gemini_rubric" if score else "pending_gemini",evaluation_status=status))
            if status == "complete":
                session.add(m.MasteryEvidenceEvent(topic_id=topic.id,event_type="practice",source_attempt_id=attempt.id,
                    score=80,evidence_weight=.6,assisted=True,created_at=now,metadata_json='{"exercise_type":"multiple_choice"}'))
                session.add(m.ReviewEvent(topic_id=topic.id,session_id=learning.id,attempt_id=attempt.id,score=80,
                    fsrs_rating=3,reviewed_at=now,next_due_at=now+timedelta(days=2),metadata_json='{"historical":true}'))
        card = Card();card.due = now+timedelta(days=2)
        session.add(m.ReviewState(topic_id=topic.id,due_at=card.due,state_json=json.dumps({"fsrs_schema_version":1,"card":json.loads(card.to_json())})))
        session.add(m.DailyPlanItem(curriculum_id=old.id,topic_id=topic.id,plan_date="2026-01-02",item_type="practice",reason="saved reason",estimated_minutes=30,status="completed"))
        session.add(m.LessonSectionProgress(topic_id=topic.id,section_slug=lesson["sections"][0]["slug"],completed=True,completed_at=now))
        session.add(m.ChatMessage(session_id=learning.id,topic_id=topic.id,role="user",content="saved chat",chat_type="doubt"))
        session.add(m.TutorSessionState(session_id=learning.id,lesson_version="1.0.0",section_slug="old-section"))
        session.add(m.Mistake(topic_id=topic.id,category="boundary",description="Saved mistake",occurrence_count=3))
        session.add(m.ModelUsageEvent(provider="gemini",model="historical-model",purpose="tutor",thinking_level="low",input_tokens=10,output_tokens=4))
        transfer = m.LearningSession(topic_id=topic.id,mode="transfer",started_at=now)
        session.add(transfer);session.flush()
        session.add(m.TransferCheck(topic_id=topic.id,exercise_id=exercise.id,session_id=transfer.id,assisted=True))
        problem = json.loads((settings.problem_bank_path / "python/python-normalize-name.json").read_text())
        session.add(m.ArenaProblem(key=problem["key"],track="python",title=problem["title"],difficulty=problem["difficulty"],
                                  source_path="python/python-normalize-name.json",content_hash="old metadata hash",version=problem["version"]))
        session.flush()
        session.add(m.ArenaAttempt(problem_key=problem["key"],track="python",submitted_source="old source",score=100,passed=True,result_json='{"old":true}'))
        session.add(m.ArenaHintUse(problem_key=problem["key"],count=1))
        session.add(m.MasteryEvidenceEvent(topic_id=topic.id,event_type="arena",score=100,evidence_weight=.7,metadata_json='{"problem_key":"python-normalize-name"}'))
        interview = m.InterviewSession(curriculum_id=old.id,mode="quick",status="completed",overall_score=72,started_at=now,completed_at=now+timedelta(minutes=20))
        session.add(interview);session.flush()
        question = m.InterviewQuestion(session_id=interview.id,section="python",competency="saved competency",question_type="technical_short_answer",prompt_markdown="Saved question",topic_id=topic.id,rubric_json='{"saved":"rubric"}')
        session.add(question);session.flush()
        session.add(m.InterviewResponse(question_id=question.id,response_text="Saved response",score=72,evaluation_json='{"saved":true}'))
        session.add(m.InterviewReport(session_id=interview.id,report_json='{"label":"historical report","score":72}'))
        session.commit()
        return {"old_id": old.id,"new_id":new.id,"topic_id":topic.id,"exercise_id":exercise.id,"stale_id":stale.id}
