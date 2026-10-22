import ast
from pathlib import Path
import os
import subprocess
import sys
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from app.routers.practice import router

ROOT=Path(__file__).resolve().parents[1]

def test_runtime_has_no_provider_or_authoring_imports():
    for path in (ROOT/'app').rglob('*.py'):
        tree=ast.parse(path.read_text(encoding='utf-8'))
        for node in ast.walk(tree):
            if isinstance(node,(ast.Import,ast.ImportFrom)):
                names=[a.name for a in node.names] if isinstance(node,ast.Import) else [node.module or '']
                assert not any('providers' in name or name.startswith(('google','scripts.')) for name in names),path
    assert 'google-genai' not in (ROOT/'requirements.txt').read_text()
    assert 'GEMINI' not in (ROOT/'.env.example').read_text()

def test_application_import_without_optional_sdk_or_provider(tmp_path):
    code='''import sys,importlib.abc,socket
original_connect=socket.socket.connect
def local_only(sock,address):
 if isinstance(address,tuple) and address[0] not in ("127.0.0.1","localhost","::1"):raise AssertionError("External network forbidden")
 return original_connect(sock,address)
socket.socket.connect=local_only
class Block(importlib.abc.MetaPathFinder):
 def find_spec(self,fullname,path=None,target=None):
  if fullname.startswith(("google", "app.providers", "scripts.authoring")):raise AssertionError("Forbidden model import: "+fullname)
sys.meta_path.insert(0,Block())
from app.main import app
from fastapi.testclient import TestClient
assert not any("/api/ai" in r.path or "/api/tutor" in r.path or "/api/doubt" in r.path for r in app.routes)
with TestClient(app) as client:
 assert client.get("/health").json()=={"status":"ok"}
 assert client.get("/api/editions").status_code==200
 assert client.get("/api/dashboard").status_code==200
print("Provider-free runtime imported")
'''
    result=subprocess.run([sys.executable,'-c',code],cwd=ROOT,env={**os.environ,'FORGE_DATABASE_URL':'sqlite:///'+(tmp_path/'no-sdk.db').as_posix(),
        'FORGE_CONTENT_SNAPSHOT_PATH':str(tmp_path/'snapshots'),'FORGE_DATABASE_BACKUP_PATH':str(tmp_path/'backups')},capture_output=True,text=True,timeout=30)
    assert result.returncode==0,result.stdout+result.stderr

@pytest.mark.parametrize('path',['/api/practice/exercises/1/reference-validation','/api/practice/exercises/1/submission-tests'])
def test_developer_answer_endpoints_retired(path):
    app=FastAPI();app.include_router(router)
    with TestClient(app) as client:assert client.get(path).status_code==410
