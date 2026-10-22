"""Isolated launcher verification. Never reads/closes the normal .runtime state."""
import argparse
import json
import os
from pathlib import Path
import socket
import subprocess
import sys
import tempfile
import time
import urllib.request

REPO_ROOT=Path(__file__).resolve().parents[1]


def powershell(script,*args,expected=0):
    # Background descendants can inherit anonymous pipe handles on Windows.
    # Real temporary files avoid waiting for pipe EOF after PowerShell has exited.
    with tempfile.TemporaryFile(mode='w+',encoding='utf-8') as out, tempfile.TemporaryFile(mode='w+',encoding='utf-8') as err:
        result=subprocess.run(['powershell.exe','-NoProfile','-ExecutionPolicy','Bypass','-File',str(REPO_ROOT/'scripts'/script),*map(str,args)],cwd=REPO_ROOT,stdout=out,stderr=err,text=True,timeout=90)
        out.seek(0);err.seek(0);result.stdout=out.read();result.stderr=err.read()
    if expected is not None and result.returncode!=expected:raise AssertionError(result.stdout+result.stderr)
    return result


def get(url):
    with urllib.request.urlopen(url,timeout=5) as response:return json.loads(response.read())


def port_range():
    for _ in range(40):
        first=socket.socket();first.bind(('127.0.0.1',0));port=first.getsockname()[1]
        if port>65532:first.close();continue
        probes=[]
        try:
            for value in [port+1,port+2]:
                probe=socket.socket();probes.append(probe);probe.bind(('127.0.0.1',value))
            first.listen();return first,port
        except OSError:first.close()
        finally:
            for probe in probes:probe.close()
    raise RuntimeError('No disposable port range found')


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--report',type=Path);args=parser.parse_args()
    if os.name!='nt':raise RuntimeError('The launcher harness requires Windows')
    (REPO_ROOT/'scratch').mkdir(exist_ok=True)
    checks=[]
    with tempfile.TemporaryDirectory(prefix='phase5-launcher-harness-',dir=REPO_ROOT/'scratch') as directory:
        root=Path(directory).resolve();runtime=root/'runtime';runtime.mkdir();database=root/'learner.db';state_file=runtime/'forge-runtime.json'
        sentinel=subprocess.Popen([sys.executable,'-c','import time; time.sleep(600)'],creationflags=subprocess.CREATE_NO_WINDOW)
        collision,port=port_range();owned=None
        launch=['-NoBrowser','-RuntimeDir',runtime,'-DatabasePath',database,'-PortStart',port,'-PortEnd',port+2,'-PreferredPort',port]
        try:
            # This state is intentionally corrupt; it must not target any process.
            state_file.write_text('invalid json',encoding='utf-8')
            powershell('open-forge.ps1',*launch)
            owned=json.loads(state_file.read_text(encoding='utf-8-sig'))
            assert owned['port']!=port
            assert owned['runtime_dir']==str(runtime) and owned['version']==2
            assert get(owned['url']+'__forge/identity')['owner']==owned['owner']
            checks.extend(['corrupt state quarantined','occupied preferred port skipped','owned identity health matched','fresh isolated initialization'])
            assert get(owned['url']+'health')=={'status':'ok'}
            plan=get(owned['url']+'api/planner/today')
            powershell('open-forge.ps1',*launch)
            assert json.loads(state_file.read_text())['pid']==owned['pid'];checks.append('duplicate launch reused exact owned process')
            for field,replacement in [('pid',sentinel.pid),('creation_filetime',str(int(owned['creation_filetime'])+1)),('executable',str(root/'unrelated.exe')),('command_sha256','0'*64),('owner','f'*32),('runtime_dir',str(root/'other'))]:
                tampered={**owned,field:replacement};state_file.write_text(json.dumps(tampered),encoding='utf-8')
                powershell('close-forge.ps1','-RuntimeDir',runtime)
                assert sentinel.poll() is None,'Unrelated sentinel process was terminated'
                assert get(owned['url']+'__forge/identity')['owner']==owned['owner'],'Unverifiable process was incorrectly stopped'
                state_file.write_text(json.dumps(owned),encoding='utf-8');checks.append('refused tampered '+field)
            powershell('close-forge.ps1','-RuntimeDir',runtime)
            assert not state_file.exists();powershell('close-forge.ps1','-RuntimeDir',runtime)
            assert sentinel.poll() is None;checks.extend(['verified shutdown','idempotent close','unrelated sentinel preserved'])
            # A restart must resume the persisted plan instead of fabricating a new day.
            powershell('open-forge.ps1',*launch);owned=json.loads(state_file.read_text())
            assert get(owned['url']+'api/planner/today')['id']==plan['id'];checks.append('restart resumed persisted study plan')
            powershell('close-forge.ps1','-RuntimeDir',runtime)
            state_file.write_text(json.dumps(owned),encoding='utf-8');powershell('close-forge.ps1','-RuntimeDir',runtime)
            checks.append('dead process state quarantined without PID termination')
            missing=root/'missing-build';missing.mkdir()
            result=powershell('open-forge.ps1','-NoBrowser','-RuntimeDir',root/'missing-runtime','-DatabasePath',root/'missing.db','-FrontendDist',missing,expected=None)
            assert result.returncode!=0 and 'build is missing' in result.stderr;checks.append('missing build rejected before launch')
            failed=root/'failed-runtime';bad_database=root/'directory-not-database';bad_database.mkdir()
            result=powershell('open-forge.ps1','-NoBrowser','-RuntimeDir',failed,'-DatabasePath',bad_database,'-PortStart',port+1,'-PortEnd',port+2,'-PreferredPort',port+1,expected=None)
            assert result.returncode!=0 and not (failed/'forge-runtime.json').exists();checks.append('failed startup cleaned owned runtime state')
            assert sentinel.poll() is None
        finally:
            # Restore only our exact originally observed owner before cleanup. Every
            # close call uses an isolated explicit RuntimeDir, never normal Forge.
            if owned:
                try:
                    get(owned['url']+'__forge/identity')
                except Exception:pass
                else:state_file.write_text(json.dumps(owned),encoding='utf-8')
            powershell('close-forge.ps1','-RuntimeDir',runtime,expected=None)
            collision.close();sentinel.terminate();sentinel.wait(timeout=5)
    report={'checks':checks,'passed':len(checks),'normal_runtime_accessed':False,'normal_database_accessed':False}
    if args.report:args.report.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(report,indent=2))


if __name__=='__main__':main()
