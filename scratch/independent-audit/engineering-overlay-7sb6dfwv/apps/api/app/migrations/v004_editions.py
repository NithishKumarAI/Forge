"""Add edition bindings and draft-editable, confirmed-immutable placements."""
import json
from pathlib import Path

SCHEMA = Path(__file__).with_name("editions_schema.json")
TABLES = ("editioncurriculumbinding", "topicplacement")
TRIGGERS = {"topicplacement_owner", "topicplacement_owner_update", "edition_binding_identity", "edition_binding_identity_update"}
TRIGGERS |= {f"{table}_confirmed_{op}" for table in TABLES for op in ("insert", "update", "delete")}
TRIGGERS |= {f"edition_graph_{table}_{op}" for table in ("topic", "track", "topicprerequisite") for op in ("insert", "update", "delete")}
TRIGGERS.add("edition_curriculum_fixed")
TRIGGERS |= {"edition_prerequisite_owner_insert", "edition_prerequisite_owner_update"}


def apply(connection):
    for table in json.loads(SCHEMA.read_text(encoding="utf-8")):
        connection.exec_driver_sql(table["sql"])
        for statement in table["indexes"]: connection.exec_driver_sql(statement)
    subjects = "'quantitative-aptitude','logical-reasoning','verbal-english','python','sql-postgresql','dsa','system-design','ai-fundamentals','interview-communication'"
    for op in ("INSERT", "UPDATE"):
        name = "topicplacement_owner" if op == "INSERT" else "topicplacement_owner_update"
        connection.exec_driver_sql(f"""CREATE TRIGGER {name} BEFORE {op} ON topicplacement
            WHEN typeof(NEW.level)!='integer' OR NEW.level<1 OR NEW.level>5 OR NEW.order_index<0 OR NEW.subject_key NOT IN ({subjects})
            OR (NEW.edition_key='placement-foundations' AND NEW.level>3)
            OR NOT EXISTS (SELECT 1 FROM topic t JOIN track tr ON tr.id=t.track_id
                JOIN editioncurriculumbinding b ON b.curriculum_id=tr.curriculum_id
                WHERE t.id=NEW.topic_id AND tr.curriculum_id=NEW.curriculum_id AND b.edition_key=NEW.edition_key AND tr.slug=NEW.subject_key)
            BEGIN SELECT RAISE(ABORT,'Invalid topic subject/level/curriculum placement'); END""")
    connection.exec_driver_sql("""CREATE TRIGGER edition_binding_identity BEFORE INSERT ON editioncurriculumbinding
        WHEN NEW.edition_key NOT IN ('placement-foundations','advanced-engineering')
        BEGIN SELECT RAISE(ABORT,'Unknown product edition'); END""")
    connection.exec_driver_sql("""CREATE TRIGGER edition_binding_identity_update BEFORE UPDATE ON editioncurriculumbinding
        WHEN NEW.edition_key IS NOT OLD.edition_key OR NEW.curriculum_id IS NOT OLD.curriculum_id
        BEGIN SELECT RAISE(ABORT,'Edition binding identity is immutable'); END""")
    for table in TABLES:
        for op in ("INSERT", "UPDATE", "DELETE"):
            aliases = ("NEW",) if op == "INSERT" else ("OLD",) if op == "DELETE" else ("OLD", "NEW")
            condition = " OR ".join(f"EXISTS (SELECT 1 FROM curriculum WHERE id={a}.curriculum_id AND status='confirmed')" for a in aliases)
            connection.exec_driver_sql(f"""CREATE TRIGGER {table}_confirmed_{op.lower()} BEFORE {op} ON {table}
                WHEN {condition} BEGIN SELECT RAISE(ABORT,'Confirmed edition metadata is immutable'); END""")
    for table in ("topic", "track", "topicprerequisite"):
        for op in ("INSERT", "UPDATE", "DELETE"):
            aliases = ("NEW",) if op == "INSERT" else ("OLD",) if op == "DELETE" else ("OLD", "NEW")
            checks = []
            for a in aliases:
                cid = f"{a}.curriculum_id" if table == "track" else f"(SELECT curriculum_id FROM track WHERE id={a}.track_id)" if table == "topic" else f"(SELECT tr.curriculum_id FROM topic t JOIN track tr ON tr.id=t.track_id WHERE t.id={a}.topic_id)"
                checks.append(f"EXISTS (SELECT 1 FROM curriculum c JOIN editioncurriculumbinding b ON b.curriculum_id=c.id WHERE c.id={cid} AND c.status='confirmed')")
            connection.exec_driver_sql(f"""CREATE TRIGGER edition_graph_{table}_{op.lower()} BEFORE {op} ON {table}
                WHEN {' OR '.join(checks)} BEGIN SELECT RAISE(ABORT,'Confirmed edition graph is immutable'); END""")
    connection.exec_driver_sql("""CREATE TRIGGER edition_curriculum_fixed BEFORE UPDATE ON curriculum
        WHEN OLD.status='confirmed' AND EXISTS (SELECT 1 FROM editioncurriculumbinding WHERE curriculum_id=OLD.id)
        AND (NEW.name IS NOT OLD.name OR NEW.description IS NOT OLD.description OR NEW.version IS NOT OLD.version
            OR NEW.source_type IS NOT OLD.source_type OR NEW.status IS NOT OLD.status)
        BEGIN SELECT RAISE(ABORT,'Confirmed edition curriculum is immutable'); END""")
    for op in ("INSERT", "UPDATE"):
        connection.exec_driver_sql(f"""CREATE TRIGGER edition_prerequisite_owner_{op.lower()} BEFORE {op} ON topicprerequisite
            WHEN EXISTS (SELECT 1 FROM topic t JOIN track tr ON tr.id=t.track_id
                JOIN editioncurriculumbinding b ON b.curriculum_id=tr.curriculum_id WHERE t.id=NEW.topic_id)
            AND NOT EXISTS (SELECT 1 FROM topic t JOIN track tr ON tr.id=t.track_id
                JOIN topic p ON p.id=NEW.prerequisite_topic_id JOIN track pr ON pr.id=p.track_id
                WHERE t.id=NEW.topic_id AND tr.curriculum_id=pr.curriculum_id)
            BEGIN SELECT RAISE(ABORT,'Edition prerequisites must belong to the same curriculum'); END""")
