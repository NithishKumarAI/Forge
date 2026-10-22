"""Add study plan revisions and timed-session associations; history stays untouched."""
import json
from pathlib import Path

SCHEMA=Path(__file__).with_name("study_release_schema.json")
TABLES={"studyplanrevision","studyplanentry","timedtestsession","timedtestitem"}
TRIGGERS={"plan_entry_owner","plan_entry_fixed_update","plan_entry_fixed_delete",
          "timed_item_owner","timed_item_identity_fixed","timed_blueprint_fixed","timed_completed_fixed",
          "plan_identity_fixed","timed_item_no_delete","timed_session_no_delete","timed_draft_locked"}


def apply(connection):
    for table in json.loads(SCHEMA.read_text(encoding="utf-8")):
        connection.exec_driver_sql(table["sql"])
        for index in table["indexes"]:connection.exec_driver_sql(index)
    connection.exec_driver_sql("""CREATE TRIGGER plan_entry_owner BEFORE INSERT ON studyplanentry
      WHEN NOT EXISTS (SELECT 1 FROM studyplanrevision p JOIN dailyplanitem i ON i.curriculum_id=p.curriculum_id
       WHERE p.id=NEW.plan_id AND i.id=NEW.item_id AND i.plan_date=p.local_date)
      BEGIN SELECT RAISE(ABORT,'Study plan owner/date mismatch'); END""")
    for operation in ("UPDATE","DELETE"):
        connection.exec_driver_sql(f"CREATE TRIGGER plan_entry_fixed_{operation.lower()} BEFORE {operation} ON studyplanentry BEGIN SELECT RAISE(ABORT,'Study plan history is immutable'); END")
    connection.exec_driver_sql("""CREATE TRIGGER timed_item_owner BEFORE INSERT ON timedtestitem
      WHEN NOT EXISTS (SELECT 1 FROM timedtestsession t JOIN assessmentselection s ON s.curriculum_id=t.curriculum_id
        WHERE t.id=NEW.session_id AND s.id=NEW.selection_id AND s.purpose='timed' AND s.approval='approved')
      BEGIN SELECT RAISE(ABORT,'Timed item ownership mismatch'); END""")
    connection.exec_driver_sql("""CREATE TRIGGER timed_item_identity_fixed BEFORE UPDATE ON timedtestitem
      WHEN NEW.session_id IS NOT OLD.session_id OR NEW.position IS NOT OLD.position OR NEW.selection_id IS NOT OLD.selection_id
        OR NEW.weight IS NOT OLD.weight OR NEW.negative_mark IS NOT OLD.negative_mark
      BEGIN SELECT RAISE(ABORT,'Timed item identity is immutable'); END""")
    connection.exec_driver_sql("""CREATE TRIGGER timed_blueprint_fixed BEFORE UPDATE ON timedtestsession
      WHEN NEW.id IS NOT OLD.id OR NEW.curriculum_id IS NOT OLD.curriculum_id OR NEW.blueprint_json IS NOT OLD.blueprint_json
        OR NEW.started_at IS NOT OLD.started_at OR NEW.deadline_at IS NOT OLD.deadline_at
      BEGIN SELECT RAISE(ABORT,'Timed blueprint/deadline is immutable'); END""")
    connection.exec_driver_sql("""CREATE TRIGGER timed_completed_fixed BEFORE UPDATE ON timedtestsession
      WHEN OLD.status IN ('completed','abandoned') BEGIN SELECT RAISE(ABORT,'Finished timed assessment is immutable'); END""")
    connection.exec_driver_sql("""CREATE TRIGGER plan_identity_fixed BEFORE UPDATE ON studyplanrevision
      WHEN NEW.id IS NOT OLD.id OR NEW.curriculum_id IS NOT OLD.curriculum_id OR NEW.local_date IS NOT OLD.local_date
       OR NEW.timezone IS NOT OLD.timezone OR NEW.revision IS NOT OLD.revision OR NEW.target_minutes IS NOT OLD.target_minutes
       OR NEW.settings_json IS NOT OLD.settings_json OR NEW.policy_version IS NOT OLD.policy_version
       OR NEW.created_at IS NOT OLD.created_at BEGIN SELECT RAISE(ABORT,'Study plan identity is immutable'); END""")
    for table,name in [('timedtestitem','timed_item_no_delete'),('timedtestsession','timed_session_no_delete')]:
        connection.exec_driver_sql(f"CREATE TRIGGER {name} BEFORE DELETE ON {table} BEGIN SELECT RAISE(ABORT,'Timed history cannot be deleted'); END")
    connection.exec_driver_sql("""CREATE TRIGGER timed_draft_locked BEFORE UPDATE ON timedtestitem
      WHEN NEW.draft_json IS NOT OLD.draft_json AND (EXISTS (SELECT 1 FROM timedtestsession WHERE id=OLD.session_id AND status!='active')
       OR EXISTS (SELECT 1 FROM assessmentselection WHERE id=OLD.selection_id AND status!='open'))
      BEGIN SELECT RAISE(ABORT,'Submitted timed answer is locked'); END""")
