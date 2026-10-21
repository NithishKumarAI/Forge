"""Freeze the pre-Phase-1 schema: initialize fresh DBs or verify unversioned ones."""
from pathlib import Path
import json

SCHEMA = Path(__file__).with_name("legacy_schema.json")


def apply(connection) -> None:
    for table in json.loads(SCHEMA.read_text(encoding="utf-8")):
        connection.exec_driver_sql(table["sql"].replace("CREATE TABLE ", "CREATE TABLE IF NOT EXISTS ", 1))
        for statement in table["indexes"]:
            connection.exec_driver_sql(statement.replace("INDEX ", "INDEX IF NOT EXISTS ", 1))
