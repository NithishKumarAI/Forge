import json
from pathlib import Path
import pytest
from sqlalchemy import inspect
from sqlmodel import create_engine
from app.migrations import runner
from app.services.database_backup import verify_database_backup,restore_database_backup

def version_four(path):
    engine=create_engine('sqlite:///'+path.as_posix())
    with engine.begin() as connection:
        bootstrap=json.loads(runner.v002_content_bindings.SCHEMA.read_text(encoding='utf-8'))
        for migration in runner.MIGRATIONS[:4]:
            migration.module.apply(connection)
            if migration.version==1:connection.exec_driver_sql(next(t['sql'] for t in bootstrap if t['name']=='schemamigration'))
            connection.exec_driver_sql('INSERT INTO schemamigration VALUES (?,?,?,?)',(migration.version,migration.name,migration.checksum,'2026-10-21'))
        connection.exec_driver_sql("INSERT INTO appsetting VALUES ('history','do not change')")
    return engine

def test_four_to_five_failure_atomic_upgrade_backup_restore(tmp_path,monkeypatch):
    engine=version_four(tmp_path/'before.db')
    with engine.connect() as c:before=c.exec_driver_sql('SELECT * FROM schemamigration').all()
    old_tables=set(inspect(engine).get_table_names());apply=runner.v005_assessment.apply
    def failure(c):
        c.exec_driver_sql('CREATE TABLE failed_assessment_probe (id INTEGER)')
        raise RuntimeError('synthetic interrupted migration')
    monkeypatch.setattr(runner.v005_assessment,'apply',failure)
    with pytest.raises(RuntimeError,match='interrupted'):runner.run_migrations(engine)
    assert set(inspect(engine).get_table_names())==old_tables
    with engine.connect() as c:assert c.exec_driver_sql('SELECT * FROM schemamigration').all()==before
    monkeypatch.setattr(runner.v005_assessment,'apply',apply)
    result=runner.run_migrations(engine)
    assert result['applied']==[5,6]
    backup=Path(result['backup_path']);assert verify_database_backup(backup)['schema_version']==4
    assert runner.run_migrations(engine)['applied']==[]
    with engine.connect() as c:
        assert c.exec_driver_sql('SELECT * FROM schemamigration WHERE version<=4').all()==before
        assert c.exec_driver_sql("SELECT value FROM appsetting WHERE key='history'").scalar()=='do not change'
    restore_database_backup(backup,tmp_path/'restored.db')
    restored=create_engine('sqlite:///'+(tmp_path/'restored.db').as_posix())
    with restored.connect() as c:assert c.exec_driver_sql('SELECT count(*) FROM schemamigration').scalar()==4
    restored.dispose();engine.dispose()
