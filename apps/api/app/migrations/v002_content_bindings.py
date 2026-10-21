"""Add immutable content identities and ownership-checked associations only."""
from pathlib import Path
import json

SCHEMA = Path(__file__).with_name("content_schema.json")


def apply(connection) -> None:
    for table in json.loads(SCHEMA.read_text(encoding="utf-8")):
        if table["name"] == "schemamigration":
            continue
        connection.exec_driver_sql(table["sql"])
        for statement in table["indexes"]:
            connection.exec_driver_sql(statement)
    for table in ("contentrevision", "topiccontentbinding", "arenatopicbinding", "courseexercisebinding"):
        for operation in ("UPDATE", "DELETE"):
            connection.exec_driver_sql(f"""CREATE TRIGGER {table}_immutable_{operation.lower()}
                BEFORE {operation} ON {table}
                BEGIN SELECT RAISE(ABORT, 'Registered content/bindings are immutable'); END""")
    for table in ("topiccontentbinding", "arenatopicbinding"):
        connection.exec_driver_sql(f"""CREATE TRIGGER {table}_owner BEFORE INSERT ON {table}
            WHEN NEW.topic_id IS NOT NULL AND NOT EXISTS (
                SELECT 1 FROM topic JOIN track ON topic.track_id=track.id
                WHERE topic.id=NEW.topic_id AND track.curriculum_id=NEW.curriculum_id)
            BEGIN SELECT RAISE(ABORT, 'Binding topic belongs to another curriculum'); END""")
    connection.exec_driver_sql("""CREATE TRIGGER courseexercisebinding_owner BEFORE INSERT ON courseexercisebinding
        WHEN NOT EXISTS (SELECT 1 FROM topiccontentbinding b JOIN exercise e ON e.topic_id=b.topic_id
            JOIN topic t ON t.id=e.topic_id
            WHERE b.topic_id=NEW.topic_id AND b.content_revision_id=NEW.content_revision_id
            AND e.id=NEW.exercise_id AND e.curriculum_id=b.curriculum_id AND e.track_id=t.track_id)
        BEGIN SELECT RAISE(ABORT, 'Exercise does not belong to this content/topic/curriculum'); END""")
    for operation in ("INSERT", "UPDATE"):
        connection.exec_driver_sql(f"""CREATE TRIGGER contentsectionprogress_owner_{operation.lower()}
            BEFORE {operation} ON contentsectionprogress
            WHEN NOT EXISTS (SELECT 1 FROM topiccontentbinding WHERE topic_id=NEW.topic_id
                AND content_revision_id=NEW.content_revision_id)
            BEGIN SELECT RAISE(ABORT, 'Progress requires a bound lesson revision'); END""")
    connection.exec_driver_sql("""CREATE TRIGGER topiccontentbinding_type BEFORE INSERT ON topiccontentbinding
        WHEN NOT EXISTS (SELECT 1 FROM contentrevision WHERE id=NEW.content_revision_id AND content_type='lesson_bundle')
        BEGIN SELECT RAISE(ABORT, 'Lesson binding requires a lesson bundle'); END""")
    connection.exec_driver_sql("""CREATE TRIGGER arenatopicbinding_type BEFORE INSERT ON arenatopicbinding
        WHEN NOT EXISTS (SELECT 1 FROM contentrevision r JOIN arenaproblem p ON p.key=NEW.problem_key
            WHERE r.id=NEW.content_revision_id AND r.content_type='arena_problem'
            AND r.content_key='arena/' || p.key AND r.revision=p.version)
        BEGIN SELECT RAISE(ABORT, 'Arena binding requires the exact problem revision'); END""")
