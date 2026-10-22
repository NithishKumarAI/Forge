from pathlib import Path
import pytest
from sqlalchemy import inspect
from sqlmodel import create_engine
from app.migrations import runner
from app.services.database_backup import verify_database_backup,restore_database_backup
from tests.test_assessment_migrations import version_four


def test_version_five_upgrade_failure_backup_restore_and_frozen_history(tmp_path,monkeypatch):
    engine=version_four(tmp_path/'before.db')
    migration=runner.MIGRATIONS[4]
    with engine.begin() as c:
        migration.module.apply(c)
        c.exec_driver_sql('INSERT INTO schemamigration VALUES (?,?,?,?)',(5,migration.name,migration.checksum,'2026-10-22'))
    with engine.connect() as c:
        ledger=c.exec_driver_sql('SELECT * FROM schemamigration').all()
        old=c.exec_driver_sql('SELECT * FROM appsetting').all()
    tables=set(inspect(engine).get_table_names());apply=runner.v006_study_release.apply
    def failure(c):
        c.exec_driver_sql('CREATE TABLE partial_study_probe(id INTEGER)')
        raise RuntimeError('Synthetic interrupted schema six')
    monkeypatch.setattr(runner.v006_study_release,'apply',failure)
    with pytest.raises(RuntimeError):runner.run_migrations(engine)
    assert set(inspect(engine).get_table_names())==tables
    monkeypatch.setattr(runner.v006_study_release,'apply',apply)
    result=runner.run_migrations(engine)
    assert result['applied']==[6] and verify_database_backup(Path(result['backup_path']))['schema_version']==5
    with engine.connect() as c:
        assert c.exec_driver_sql('SELECT * FROM schemamigration WHERE version<=5').all()==ledger
        assert c.exec_driver_sql('SELECT * FROM appsetting').all()==old
    assert runner.run_migrations(engine)['applied']==[]
    restore_database_backup(Path(result['backup_path']),tmp_path/'restored.db')
    restored=create_engine('sqlite:///'+(tmp_path/'restored.db').as_posix())
    with restored.connect() as c:assert c.exec_driver_sql('SELECT * FROM schemamigration').all()==ledger
    restored.dispose();engine.dispose()
