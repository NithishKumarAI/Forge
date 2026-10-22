"""Owned loopback launcher entry point; never launches a model or learner code."""
import argparse
import ctypes
from ctypes import wintypes
from datetime import datetime,timezone
import hashlib
import json
import os
from pathlib import Path
import re
import socket
import sys


def process_identity():
    kernel=ctypes.WinDLL('kernel32',use_last_error=True)
    kernel.GetCurrentProcess.restype=wintypes.HANDLE
    times=[wintypes.FILETIME() for _ in range(4)]
    kernel.GetProcessTimes.argtypes=[wintypes.HANDLE]+[ctypes.POINTER(wintypes.FILETIME)]*4
    if not kernel.GetProcessTimes(kernel.GetCurrentProcess(),*[ctypes.byref(t) for t in times]):raise ctypes.WinError(ctypes.get_last_error())
    kernel.GetCommandLineW.restype=wintypes.LPWSTR
    executable=ctypes.create_unicode_buffer(32768)
    if not kernel.GetModuleFileNameW(None,executable,len(executable)):raise ctypes.WinError()
    return {'creation_filetime':str((times[0].dwHighDateTime<<32)|times[0].dwLowDateTime),'executable':executable.value,
            'command_sha256':hashlib.sha256(kernel.GetCommandLineW().encode('utf-8')).hexdigest()}


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--owner',required=True);parser.add_argument('--runtime-dir',required=True);parser.add_argument('--port',type=int,required=True)
    args=parser.parse_args()
    if os.name!='nt' or not re.fullmatch('[0-9a-f]{32}',args.owner):raise ValueError('Windows launcher ownership token required')
    root=Path(__file__).resolve().parents[1];runtime=Path(args.runtime_dir).resolve()
    verify_network=os.environ.get('FORGE_VERIFY_NO_NETWORK')=='1'
    if verify_network:
        from offline_verify_guard import install
        install()
    listener=socket.socket(socket.AF_INET,socket.SOCK_STREAM);listener.setsockopt(socket.SOL_SOCKET,socket.SO_EXCLUSIVEADDRUSE,1)
    listener.bind(('127.0.0.1',args.port));listener.listen(128)
    state={'version':2,'pid':os.getpid(),'owner':args.owner,'runtime_dir':str(runtime),'repo_root':str(root),'port':args.port,
           'url':f'http://127.0.0.1:{args.port}/','started_at':datetime.now(timezone.utc).isoformat(),'verification_network_denial':verify_network,**process_identity()}
    temporary=runtime/(args.owner+'.tmp')
    with temporary.open('x',encoding='utf-8') as file:
        json.dump(state,file,indent=2);file.flush();os.fsync(file.fileno())
    os.replace(temporary,runtime/'forge-runtime.json')
    sys.path.insert(0,str(root/'apps/api'));os.chdir(root/'apps/api')
    from app.main import app
    @app.get('/__forge/identity',include_in_schema=False)
    def identity():return {'owner':args.owner,'pid':os.getpid(),'runtime_dir':str(runtime)}
    # The production SPA fallback is registered by app.main. The exact launcher
    # identity route must precede that catch-all, or it would return index.html.
    app.router.routes.insert(0,app.router.routes.pop())
    import uvicorn
    try:uvicorn.Server(uvicorn.Config(app,host='127.0.0.1',port=args.port,log_level='warning')).run(sockets=[listener])
    finally:listener.close()


if __name__=='__main__':main()
