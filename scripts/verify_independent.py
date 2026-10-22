"""Independent real-browser audit on dedicated 24000–24049 loopback ports."""
import argparse
import json
import os
from pathlib import Path
import socket
import subprocess
import sys
import tempfile

from verify_launcher import powershell

ROOT=Path(__file__).resolve().parents[1]


def free_port():
    for port in range(24000,24050):
        with socket.socket() as probe:
            try:probe.bind(('127.0.0.1',port));return port
            except OSError:pass
    raise RuntimeError('Dedicated independent-audit port range occupied')


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--playwright-module',required=True);parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args();output=args.output.resolve();output.mkdir(parents=True,exist_ok=True)
    root=Path(tempfile.mkdtemp(prefix='independent-browser-',dir=ROOT/'scratch')).resolve()
    environment={**os.environ,'FORGE_VERIFY_NO_NETWORK':'1','FORGE_PLAYWRIGHT_MODULE':args.playwright_module}
    subprocess.run([sys.executable,str(ROOT/'scripts/prepare_browser_fixture.py'),'--database',str(root/'content/learner.db')],env=environment,cwd=ROOT,check=True)
    # An unversioned synthetic legacy DB proves upgrade through the real launcher.
    sys.path.insert(0,str(ROOT/'apps/api'))
    from tests.test_database_migrations import legacy_database
    legacy=root/'legacy/learner.db';legacy.parent.mkdir();engine=legacy_database(legacy)
    with engine.begin() as c:c.exec_driver_sql("INSERT INTO appsetting VALUES ('independent_legacy_sentinel','SYNTHETIC ONLY preserved')")
    engine.dispose()
    runtimes=[];origins={}
    try:
        os.environ['FORGE_VERIFY_NO_NETWORK']='1'
        for name in ['fresh','content','legacy']:
            folder=root/name;runtime=folder/'runtime';runtimes.append(runtime);port=free_port()
            powershell('open-forge.ps1','-NoBrowser','-RuntimeDir',runtime,'-DatabasePath',folder/'learner.db',
                '-SnapshotPath',folder/'snapshots','-BackupPath',folder/'backups','-PortStart',port,'-PortEnd',port,'-PreferredPort',port)
            state=json.loads((runtime/'forge-runtime.json').read_text(encoding='utf-8-sig'));assert state['verification_network_denial']
            origins[name]=state['url'].rstrip('/')
        config={'fixture':str(root/'content/fixture.json'),'freshOrigin':origins['fresh'],'contentOrigin':origins['content'],'legacyOrigin':origins['legacy'],
                'images':str(output),'report':str(output/'browser-report.json'),'output':str(output),'census':str(output/'content-census.json')}
        configuration=root/'browser-config.json';configuration.write_text(json.dumps(config),encoding='utf-8')
        print('Synthetic audit fixtures:',root,flush=True)
        for script in ['verify-browser.cjs','audit-browser.cjs']:
            subprocess.run(['node',str(ROOT/'scripts'/script),str(configuration)],cwd=ROOT,env=environment,check=True,timeout=900)
        import sqlite3
        from app.services.database_backup import verify_database_backup,restore_database_backup
        with sqlite3.connect(legacy.as_uri()+'?mode=ro',uri=True) as c:
            assert c.execute("SELECT value FROM appsetting WHERE key='independent_legacy_sentinel'").fetchone()[0]=='SYNTHETIC ONLY preserved'
            assert c.execute('SELECT count(*) FROM schemamigration').fetchone()[0]==6
        backup=next((root/'legacy/backups').glob('*.sqlite3'));metadata=verify_database_backup(backup)
        restored=restore_database_backup(backup,root/'restored.db')
        with sqlite3.connect(restored.as_uri()+'?mode=ro',uri=True) as c:
            assert c.execute("SELECT value FROM appsetting WHERE key='independent_legacy_sentinel'").fetchone()[0]=='SYNTHETIC ONLY preserved'
            assert not c.execute("SELECT name FROM sqlite_master WHERE name='schemamigration'").fetchall()
        (output/'browser-upgrade-backup.json').write_text(json.dumps({'schema_after':6,'backup_schema':metadata['schema_version'],'restored_sentinel':True,'synthetic_only':True,'normal_database_accessed':False},indent=2)+'\n',encoding='utf-8')
    finally:
        for runtime in runtimes:powershell('close-forge.ps1','-RuntimeDir',runtime,expected=None)


if __name__=='__main__':main()
