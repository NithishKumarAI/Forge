"""Compare an immutable HEAD archive with an explicit engineering-only overlay."""
import io
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import zipfile

ROOT=Path(__file__).resolve().parents[1]


def main():
    target=Path(tempfile.mkdtemp(prefix='engineering-overlay-',dir=ROOT/'scratch/independent-audit'))
    archive=subprocess.check_output(['git','archive','--format=zip','HEAD'],cwd=ROOT)
    with zipfile.ZipFile(io.BytesIO(archive)) as files:
        for name in files.namelist():
            if not (target/name).resolve().is_relative_to(target.resolve()):raise RuntimeError('Unsafe archive path')
        files.extractall(target)
    env={**os.environ,'FORGE_DATABASE_URL':'sqlite:///'+(target/'smoke.db').as_posix(),'FORGE_CONTENT_SNAPSHOT_PATH':str(target/'snapshots'),'FORGE_DATABASE_BACKUP_PATH':str(target/'backups')}
    probe="from app.main import create_app; import json; s=create_app().openapi(); print(json.dumps({'timed_start':'/api/timed-tests/start' in s['paths'],'planner_regenerate':'/api/planner/regenerate' in s['paths']}))"
    before=subprocess.run([sys.executable,'-c',probe],cwd=target/'apps/api',env=env,text=True,capture_output=True,check=True)
    committed=json.loads(before.stdout)
    assert not committed['timed_start'] and not committed['planner_regenerate']
    paths=subprocess.check_output(['git','diff','--name-only','HEAD','--','apps/api','scripts'],cwd=ROOT,text=True).splitlines()
    paths+=subprocess.check_output(['git','ls-files','--others','--exclude-standard','apps/api/app','apps/api/tests','data/timed-test-blueprints'],cwd=ROOT,text=True).splitlines()
    paths+=['apps/api/scripts/content_checks/subject_accuracy.py','scripts/forge_server.py','scripts/launcher-common.ps1','scripts/offline_verify_guard.py']
    paths=sorted(set(p for p in paths if p!='apps/api/tests/test_placement_content.py' and not p.startswith('data/content-approvals/')))
    for name in paths:
        source=ROOT/name;destination=target/name;destination.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(source,destination)
    smoke='''from app.main import create_app
from fastapi.testclient import TestClient
import json
app=create_app()
with TestClient(app) as client:
    assert client.get('/health').status_code==200
    assert client.get('/api/dashboard').status_code==200
    plan=client.post('/api/planner/regenerate').json()
    assert plan['target_minutes']==300 and plan['unallocated_minutes']==300
    assert client.get('/api/planner/settings').json()['study_timezone']=='Asia/Kolkata'
    assert client.get('/api/timed-tests/blueprints').status_code==200
    assert client.post('/api/timed-tests/start',json={'kind':'subject','subject':'python'}).status_code==409
    assert client.post('/api/timed-tests/start',json={'kind':'subject','subject':'python','level':True}).status_code==422
    assert client.get('/api/planner/today',headers={'Origin':'https://untrusted.example'}).status_code==403
print(json.dumps({'startup':True,'dashboard':True,'planner_contract':True,'timed_contract':True,'strict_types':True,'origin_boundary':True,'candidate_files_added':0}))
'''
    after=subprocess.run([sys.executable,'-c',smoke],cwd=target/'apps/api',env=env,text=True,capture_output=True,check=True)
    result={'committed_head':committed,'engineering_overlay':json.loads(after.stdout),'explicit_overlay_paths':paths,'secrets_or_learner_data_added':False,
            'unreviewed_content_added':False,'git_checkout_modified':False,'method':'git archive plus explicit copies into a new disposable directory; no branch reset/staging/commit/push'}
    (ROOT/'docs/forge-v1/audit-evidence/engineering-overlay.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result['engineering_overlay']))


if __name__=='__main__':main()
