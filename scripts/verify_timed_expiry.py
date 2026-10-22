"""Real elapsed-time expiry test on an existing, explicitly synthetic fixture only."""
import argparse
from datetime import datetime,timezone
import json
import os
from pathlib import Path
import subprocess
import urllib.request
from verify_launcher import powershell
from verify_independent import free_port

ROOT=Path(__file__).resolve().parents[1]


def call(url,body=None):
    request=urllib.request.Request(url,data=json.dumps(body).encode() if body is not None else None,headers={'Content-Type':'application/json'})
    with urllib.request.urlopen(request,timeout=30) as response:return json.loads(response.read())


def main():
    parser=argparse.ArgumentParser();parser.add_argument('mode',choices=['start','finish']);parser.add_argument('--state',type=Path,required=True);parser.add_argument('--fixture-root',type=Path);parser.add_argument('--playwright-module',required=True)
    args=parser.parse_args();os.environ['FORGE_VERIFY_NO_NETWORK']='1'
    if args.mode=='start':
        folder=args.fixture_root.resolve();manifest=json.loads((folder/'fixture.json').read_text(encoding='utf-8'))
        if not folder.is_relative_to(ROOT/'scratch') or not manifest.get('SYNTHETIC_TEST_DATA_ONLY'):raise RuntimeError('Only a verified synthetic fixture under scratch is permitted')
        runtime=folder/'expiry-runtime';port=free_port();launch=['-NoBrowser','-RuntimeDir',runtime,'-DatabasePath',folder/'learner.db','-SnapshotPath',folder/'snapshots','-BackupPath',folder/'backups','-PortStart',port,'-PortEnd',port,'-PreferredPort',port]
        powershell('open-forge.ps1',*launch);owner=json.loads((runtime/'forge-runtime.json').read_text(encoding='utf-8-sig'));base=owner['url'].rstrip('/')
        test=call(base+'/api/timed-tests/start',{'kind':'subject','subject':'python'})
        for position,action in [(0,'answer'),(1,'draft')]:
            item=test['questions'][position]['assessment'];assert item['kind']=='single_choice'
            call(base+f"/api/timed-tests/{test['id']}/{action}",{'position':position,'content_sha256':item['content_sha256'],'answer':['a'],'source':'','unit':''})
        powershell('close-forge.ps1','-RuntimeDir',runtime);powershell('open-forge.ps1',*launch)
        current=call(base+'/api/timed-tests/'+test['id']);assert current['deadline_at']==test['deadline_at'] and current['questions'][1]['assessment']['draft']['answer']==['a']
        state={'synthetic_only':True,'base':base,'runtime':str(runtime),'id':test['id'],'deadline_at':test['deadline_at'],'restart_preserved_deadline_and_draft':True,'status':'waiting_for_real_deadline'}
        args.state.write_text(json.dumps(state,indent=2)+'\n',encoding='utf-8')
    else:state=json.loads(args.state.read_text(encoding='utf-8'))
    if args.mode=='finish':
        deadline=datetime.fromisoformat(state['deadline_at'].replace('Z','+00:00'))
        if deadline.tzinfo is None:deadline=deadline.replace(tzinfo=timezone.utc)
        if datetime.now(timezone.utc)<deadline:raise RuntimeError('The real deadline has not elapsed; no expiry pass is claimed')
        current=call(state['base']+'/api/timed-tests/'+state['id']);report=current['report']
        assert current['status']=='completed' and report['completion_reason']=='timeout' and report['overall_score']==33.33
        assert sum(q['unanswered'] for q in report['questions'])==2
        state.update(status='passed_actual_elapsed_time',report=report)
        args.state.write_text(json.dumps(state,indent=2)+'\n',encoding='utf-8')
    env={**os.environ,'FORGE_PLAYWRIGHT_MODULE':args.playwright_module}
    try:subprocess.run(['node',str(ROOT/'scripts/audit-expiry-browser.cjs'),str(args.state),args.mode],cwd=ROOT,env=env,check=True,timeout=60)
    finally:
        if args.mode=='finish':powershell('close-forge.ps1','-RuntimeDir',state['runtime'])
    print(json.dumps({k:v for k,v in state.items() if k!='report'}))


if __name__=='__main__':main()
