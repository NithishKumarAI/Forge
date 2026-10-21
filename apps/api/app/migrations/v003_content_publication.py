"""Append-only validation, human review, releases and exact new attempt identity."""
import json
from pathlib import Path

SCHEMA = Path(__file__).with_name("publication_schema.json")
TABLES = ("contentvalidationreport", "contentreviewrecord", "approvedcontentrelease",
          "contentreleaseentry", "contentreleaseevent", "arenaattemptcontent")
TRIGGERS = {f"{t}_immutable_{op}" for t in TABLES for op in ("update", "delete")} | {
    "contentreleaseentry_approval", "contentreleaseentry_owner", "contentreleaseevent_status", "arenaattemptcontent_identity"}


def apply(connection):
    for table in json.loads(SCHEMA.read_text(encoding="utf-8")):
        connection.exec_driver_sql(table["sql"])
        for sql in table["indexes"]:
            connection.exec_driver_sql(sql)
    for table in TABLES:
        for operation in ("UPDATE", "DELETE"):
            connection.exec_driver_sql(f"""CREATE TRIGGER {table}_immutable_{operation.lower()}
                BEFORE {operation} ON {table}
                BEGIN SELECT RAISE(ABORT, 'Publication records are append-only'); END""")
    connection.exec_driver_sql("""CREATE TRIGGER contentreleaseentry_approval BEFORE INSERT ON contentreleaseentry
        WHEN NOT EXISTS (SELECT 1 FROM contentrevision c JOIN contentvalidationreport v ON v.payload_sha256=c.sha256
            JOIN contentreviewrecord r ON r.validation_sha256=v.sha256
            WHERE c.id=NEW.content_revision_id AND v.sha256=NEW.validation_sha256
            AND r.sha256=NEW.review_sha256 AND r.outcome='approved')
        BEGIN SELECT RAISE(ABORT, 'Release requires exact validated and reviewed digest'); END""")
    connection.exec_driver_sql("""CREATE TRIGGER contentreleaseentry_owner BEFORE INSERT ON contentreleaseentry
        WHEN NOT EXISTS (SELECT 1 FROM topic t JOIN track tr ON tr.id=t.track_id
            WHERE t.id=NEW.topic_id AND tr.curriculum_id=NEW.curriculum_id)
        BEGIN SELECT RAISE(ABORT, 'Release target belongs to another curriculum'); END""")
    connection.exec_driver_sql("""CREATE TRIGGER contentreleaseevent_status BEFORE INSERT ON contentreleaseevent
        WHEN NEW.status NOT IN ('published','activated','revoked','superseded') OR NOT EXISTS (
            SELECT 1 FROM contentreleaseentry WHERE release_id=NEW.release_id)
        BEGIN SELECT RAISE(ABORT, 'Invalid/empty release transition'); END""")
    connection.exec_driver_sql("""CREATE TRIGGER arenaattemptcontent_identity BEFORE INSERT ON arenaattemptcontent
        WHEN NOT EXISTS (SELECT 1 FROM arenaattempt a JOIN contentrevision c ON c.content_key='arena/' || a.problem_key
            WHERE a.id=NEW.attempt_id AND c.id=NEW.content_revision_id AND c.content_type='arena_problem')
        BEGIN SELECT RAISE(ABORT, 'Arena attempt must reference its exact problem identity'); END""")
