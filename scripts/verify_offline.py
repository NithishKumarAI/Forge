"""Disposable, locally network-denied browser verification; never normal runtime."""
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


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--playwright-module',default=os.getenv('FORGE_PLAYWRIGHT_MODULE'))
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    output=args.output.resolve();output.mkdir(parents=True,exist_ok=True)
    root=Path(tempfile.mkdtemp(prefix='phase5-offline-',dir=ROOT/'scratch')).resolve()
    if not root.is_relative_to(ROOT/'scratch'):raise RuntimeError('Verification requires isolated scratch')
    environment={**os.environ,'FORGE_VERIFY_NO_NETWORK':'1'}
    if args.playwright_module:environment['FORGE_PLAYWRIGHT_MODULE']=args.playwright_module
    subprocess.run([sys.executable,str(ROOT/'scripts/prepare_browser_fixture.py'),'--database',str(root/'content/learner.db')],cwd=ROOT,env=environment,check=True)
    origins={};runtimes=[]
    try:
        os.environ['FORGE_VERIFY_NO_NETWORK']='1'
        for name in ['fresh','content']:
            folder=root/name;runtime=folder/'runtime';runtimes.append(runtime)
            with socket.socket() as probe:
                probe.bind(('127.0.0.1',0));port=probe.getsockname()[1]
            powershell('open-forge.ps1','-NoBrowser','-RuntimeDir',runtime,'-DatabasePath',folder/'learner.db',
                       '-SnapshotPath',folder/'snapshots','-BackupPath',folder/'backups','-PortStart',port,'-PortEnd',port,'-PreferredPort',port)
            state=json.loads((runtime/'forge-runtime.json').read_text(encoding='utf-8-sig'))
            origins[name]=state['url'].rstrip('/')
        config={'fixture':str(root/'content/fixture.json'),'contentOrigin':origins['content'],'freshOrigin':origins['fresh'],
                'images':str(output),'report':str(output/'browser-report.json')}
        configuration=root/'browser-config.json';configuration.write_text(json.dumps(config),encoding='utf-8')
        print('Browser fixtures:',root,flush=True)
        result=subprocess.run(['node',str(ROOT/'scripts/verify-browser.cjs'),str(configuration)],cwd=ROOT,env=environment,timeout=900)
        if result.returncode:raise RuntimeError('Browser verification failed; retained fixtures: '+str(root))
    finally:
        for runtime in runtimes:powershell('close-forge.ps1','-RuntimeDir',runtime,expected=None)


if __name__=='__main__':main()
