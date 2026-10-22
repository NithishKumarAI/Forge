from pathlib import Path
import sqlite3
import pytest

from fastapi.testclient import TestClient
from sqlmodel import Session, select

from app import models as m
from app.migrations import run_migrations
from app.services.course import load_lesson_for_topic, progress, sync_course_pack
from app.services.arena import sync_problem_bank
from app.services.curriculum_migration import migrate_default_v2
from app.config import settings
from tests.phase1_fixtures import LEGACY_TABLES, rows, seed_history
from tests.test_database_migrations import legacy_database


def assert_preserved(before, after):
    for table in before:
        for row in before[table]:
            if table == "arenaproblem":
                # Only the final, derived mapped_topic_id cache may change on this legacy table.
                assert any(candidate[:-1] == row[:-1] for candidate in after[table]), table
            else:
                assert row in after[table], (table, row)


@pytest.mark.parametrize("selection", ["v1", "v2", "custom"])
def test_upgrade_startup_preserves_every_legacy_row_and_selection(tmp_path, monkeypatch, selection):
    import app.main as main
    from app.database import get_session
    engine = legacy_database(tmp_path / "legacy.db")
    ids = seed_history(engine)
    selected_id = ids["old_id"]
    if selection != "v1":
        with Session(engine) as session:
            if selection == "custom":
                custom = m.Curriculum(name="User selected custom",version=7,source_type="custom",status="confirmed")
                session.add(custom);session.flush()
                selected_id = custom.id
            else:
                selected_id = ids["new_id"]
            setting = session.get(m.AppSetting,"active_curriculum_id")
            setting.value = str(selected_id);session.add(setting);session.commit()
    before = rows(engine)
    monkeypatch.setattr(main, "engine", engine)
    monkeypatch.setattr(main, "create_db_and_tables", lambda: run_migrations(engine))
    app = main.create_app()

    def sessions():
        with Session(engine) as session:
            yield session

    app.dependency_overrides[get_session] = sessions
    for _ in range(2):
        with TestClient(app) as client:
            assert client.get("/health").json() == {"status":"ok"}
            assert client.get("/api/dashboard").status_code == 200
            result = client.get(f"/api/course/topics/{ids['topic_id']}")
            assert result.status_code == 200
            assert result.json()["progress"]["completed_sections"] == 1
        assert_preserved(before, rows(engine))
        with Session(engine) as session:
            assert session.get(m.AppSetting,"active_curriculum_id").value == str(selected_id)
            assert session.get(m.LearnerTopicState,ids["topic_id"]).mastery_score == 63
            links = session.exec(select(m.CourseExerciseBinding).where(m.CourseExerciseBinding.topic_id==ids["topic_id"])).all()
            assert ids["exercise_id"] in {row.exercise_id for row in links}
            assert ids["stale_id"] not in {row.exercise_id for row in links}
    backup = next(settings.database_backup_path.glob("*.sqlite3"))
    with sqlite3.connect(backup) as connection:
        assert connection.execute("SELECT COUNT(*) FROM attempt").fetchone()[0] == 2
    engine.dispose()


def test_lineage_helper_never_copies_scores_or_changes_selection(tmp_path):
    engine = legacy_database(tmp_path / "legacy.db")
    ids = seed_history(engine)
    before = rows(engine)
    with Session(engine) as session:
        migrate_default_v2(session,session.get(m.Curriculum,ids["old_id"]),session.get(m.Curriculum,ids["new_id"]),settings.curriculum_migration_path)
    after = rows(engine)
    for table in ("learnertopicstate","appsetting","masteryevidenceevent","attempt","reviewstate"):
        assert before[table] == after[table]
    engine.dispose()


def test_fresh_application_startup_and_offline_learning_workflow(tmp_path, monkeypatch):
    import app.main as main
    from app.database import get_session
    from sqlmodel import create_engine
    engine = create_engine(f"sqlite:///{(tmp_path/'fresh-app.db').as_posix()}")
    monkeypatch.setattr(main,"engine",engine)
    monkeypatch.setattr(main,"create_db_and_tables",lambda:run_migrations(engine))
    app = main.create_app()

    def sessions():
        with Session(engine) as session:
            yield session

    app.dependency_overrides[get_session] = sessions
    with TestClient(app) as client:
        assert client.get("/health").status_code == 200
        assert client.get("/").status_code == 200
        with Session(engine) as session:
            selected = int(session.get(m.AppSetting,"active_curriculum_id").value)
            assert session.get(m.Curriculum,selected).version == 2
            topic = session.exec(select(m.Topic).join(m.Track).where(m.Track.curriculum_id==selected,
                m.Track.slug=="python",m.Topic.slug=="foundations")).one()
            topic_id = topic.id
            assert len(session.exec(select(m.Topic)).all()) == 257
            assert len(session.exec(select(m.CourseLesson)).all()) == 94
            assert len(session.exec(select(m.Exercise)).all()) == 700
        lesson = client.get(f"/api/course/topics/{topic_id}").json()
        assert lesson["lesson"]["topic_slug"] == "syntax-data-types"
        assert lesson["progress"]["completed_sections"] == 0
        practice = client.post("/api/assessment/start",json={"topic_id":topic_id,"purpose":"practice"})
        assert practice.status_code == 200 and practice.json()["approval"] == "legacy_unverified"
        assert client.get(f"/api/assessment/{practice.json()['id']}").json()["id"] == practice.json()["id"]
        assert client.get("/api/arena/problems/python-normalize-name").json()["mapping_status"] == "bound"
        assert client.get(f"/api/course/search?q=booleans&topic_id={topic_id}").json()
    engine.dispose()
