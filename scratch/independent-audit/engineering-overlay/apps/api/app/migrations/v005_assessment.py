"""Add version-aware selection/attempt provenance without rewriting historical rows."""
import json
from pathlib import Path

SCHEMA = Path(__file__).with_name("assessment_schema.json")
TABLES = ("assessmentselection", "evidencecredit", "evidencepolicyrecord", "assessmenthelpevent")
TRIGGERS = {"assessment_snapshot_fixed", "assessment_completed_fixed", "credit_fixed_update", "credit_fixed_delete", "static_interview_blueprint_fixed"}
TRIGGERS |= {"assessment_owner", "evidence_credit_owner"}
TRIGGERS |= {"assessment_no_delete","help_fixed_update","help_fixed_delete","policy_fixed_update","policy_fixed_delete"}


def apply(connection):
    for table in json.loads(SCHEMA.read_text(encoding="utf-8")):
        connection.exec_driver_sql(table["sql"])
        for index in table["indexes"]:
            connection.exec_driver_sql(index)
    connection.exec_driver_sql("""CREATE TRIGGER assessment_owner BEFORE INSERT ON assessmentselection
        WHEN (NEW.topic_id IS NOT NULL AND NOT EXISTS (SELECT 1 FROM topic t JOIN track tr ON tr.id=t.track_id
            JOIN learningsession ls ON ls.topic_id=t.id WHERE t.id=NEW.topic_id AND tr.curriculum_id=NEW.curriculum_id AND ls.id=NEW.session_id))
        OR (NEW.topic_id IS NULL AND NOT (NEW.purpose='interview' AND NEW.approval='reflection_only' AND COALESCE(json_extract(NEW.snapshot_json,'$.kind'),'')='reflection'
            AND EXISTS (SELECT 1 FROM learningsession WHERE id=NEW.session_id AND topic_id IS NULL AND mode='interview')))
        OR (NEW.content_revision_id IS NOT NULL AND NOT EXISTS (SELECT 1 FROM contentrevision WHERE id=NEW.content_revision_id AND sha256=NEW.content_sha256))
        OR json_extract(NEW.snapshot_json,'$.key') IS NOT NEW.item_key OR json_extract(NEW.snapshot_json,'$.family') IS NOT NEW.family
        BEGIN SELECT RAISE(ABORT,'Assessment ownership/content identity mismatch'); END""")
    connection.exec_driver_sql("""CREATE TRIGGER evidence_credit_owner BEFORE INSERT ON evidencecredit
        WHEN NOT EXISTS (SELECT 1 FROM assessmentselection s JOIN masteryevidenceevent e ON e.topic_id=s.topic_id
            WHERE s.id=NEW.selection_id AND s.topic_id=NEW.topic_id AND s.family=NEW.family AND e.id=NEW.event_id
            AND e.source_attempt_id=s.attempt_id)
        BEGIN SELECT RAISE(ABORT,'Evidence credit ownership mismatch'); END""")
    fields = ("id", "session_id", "curriculum_id", "topic_id", "content_revision_id", "content_sha256",
              "item_key", "family", "purpose", "approval", "snapshot_json", "policy_version", "judge_version", "created_at")
    changed = " OR ".join(f"NEW.{f} IS NOT OLD.{f}" for f in fields)
    connection.exec_driver_sql(f"CREATE TRIGGER assessment_snapshot_fixed BEFORE UPDATE ON assessmentselection WHEN {changed} BEGIN SELECT RAISE(ABORT,'Assessment identity/snapshot is immutable'); END")
    connection.exec_driver_sql("CREATE TRIGGER assessment_completed_fixed BEFORE UPDATE ON assessmentselection WHEN OLD.status!='open' BEGIN SELECT RAISE(ABORT,'Completed assessment is immutable'); END")
    connection.exec_driver_sql("""CREATE TRIGGER static_interview_blueprint_fixed BEFORE UPDATE ON interviewsession
        WHEN json_extract(OLD.metadata_json,'$.engine')='static/1' AND NEW.metadata_json IS NOT OLD.metadata_json
        BEGIN SELECT RAISE(ABORT,'Static interview blueprint snapshot is immutable'); END""")
    for op in ("UPDATE", "DELETE"):
        connection.exec_driver_sql(f"CREATE TRIGGER credit_fixed_{op.lower()} BEFORE {op} ON evidencecredit BEGIN SELECT RAISE(ABORT,'Evidence credit is immutable'); END")
        for table,prefix in (("assessmenthelpevent","help"),("evidencepolicyrecord","policy")):
            connection.exec_driver_sql(f"CREATE TRIGGER {prefix}_fixed_{op.lower()} BEFORE {op} ON {table} BEGIN SELECT RAISE(ABORT,'Assessment history is append-only'); END")
    connection.exec_driver_sql("CREATE TRIGGER assessment_no_delete BEFORE DELETE ON assessmentselection BEGIN SELECT RAISE(ABORT,'Assessment exposure history is immutable'); END")
