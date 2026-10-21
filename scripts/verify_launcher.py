import json
import os
import socket
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
RUNTIME_FILE = REPO_ROOT / ".runtime" / "forge-runtime.json"


def is_port_in_use(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(("127.0.0.1", port)) == 0


def main():
    print("=== Phase 1: Clean initial state ===")
    if RUNTIME_FILE.exists():
        subprocess.run(
            ["powershell.exe", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(REPO_ROOT / "scripts" / "close-forge.ps1")],
            check=True,
        )
    assert not RUNTIME_FILE.exists(), "Runtime file should not exist initially"

    print("=== Phase 2: Launch Forge via open-forge.ps1 ===")
    res = subprocess.run(
        ["powershell.exe", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(REPO_ROOT / "scripts" / "open-forge.ps1"), "-NoBrowser"],
        close_fds=True,
    )
    assert res.returncode == 0, f"open-forge.ps1 failed with exit code {res.returncode}"
    assert RUNTIME_FILE.exists(), "Runtime file must exist after startup"

    state = json.loads(RUNTIME_FILE.read_text(encoding="utf-8-sig"))
    pid = state["pid"]
    port = state["port"]
    url = state["url"]
    print(f"Recorded state: PID={pid}, Port={port}, URL={url}")

    assert port == 18101, f"Expected preferred port 18101, got {port}"

    print("=== Phase 3: Verify HTTP Endpoints ===")
    # 1. Health
    with urllib.request.urlopen(f"http://127.0.0.1:{port}/health") as r:
        health_data = json.loads(r.read())
        assert health_data["status"] == "ok", f"Health status was {health_data}"
        print("  [OK] /health returned 200 ok")

    # 2. SPA Root
    with urllib.request.urlopen(f"http://127.0.0.1:{port}/") as r:
        html = r.read().decode("utf-8")
        assert "<div id=\"root\">" in html or "<html" in html.lower(), "Root didn't return HTML"
        print("  [OK] / returned 200 HTML")

    # 3. SPA Fallback
    with urllib.request.urlopen(f"http://127.0.0.1:{port}/arena") as r:
        arena_html = r.read().decode("utf-8")
        assert "<div id=\"root\">" in arena_html or "<html" in arena_html.lower(), "Fallback didn't return HTML"
        print("  [OK] /arena returned 200 HTML (SPA fallback)")

    # 4. API Endpoint
    with urllib.request.urlopen(f"http://127.0.0.1:{port}/api/dashboard") as r:
        dash_data = json.loads(r.read())
        assert "tracks" in dash_data, "Dashboard missing tracks"
        print(f"  [OK] /api/dashboard returned 200 with {len(dash_data['tracks'])} tracks")

    # 5. Nonexistent API Route (must return 404, never index.html)
    try:
        urllib.request.urlopen(f"http://127.0.0.1:{port}/api/nonexistent_xyz")
        assert False, "Should have raised 404"
    except urllib.error.HTTPError as e:
        assert e.code == 404
        err_body = json.loads(e.read())
        assert err_body["detail"] == "API route not found"
        print("  [OK] /api/nonexistent_xyz returned 404 'API route not found'")

    print("=== Phase 4: Test Double-Launch Protection ===")
    res_second = subprocess.run(
        ["powershell.exe", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(REPO_ROOT / "scripts" / "open-forge.ps1"), "-NoBrowser"],
        close_fds=True,
    )
    assert res_second.returncode == 0
    state_after = json.loads(RUNTIME_FILE.read_text(encoding="utf-8-sig"))
    assert state_after["pid"] == pid, "PID should not have changed"
    print("  [OK] Double launch successfully detected and avoided duplicate instance")

    print("=== Phase 5: Test Shutdown via close-forge.ps1 ===")
    res_close = subprocess.run(
        ["powershell.exe", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(REPO_ROOT / "scripts" / "close-forge.ps1")],
        close_fds=True,
    )
    assert res_close.returncode == 0
    assert not RUNTIME_FILE.exists(), "Runtime file should be deleted after close"
    time.sleep(1)
    assert not is_port_in_use(port), f"Port {port} should be released"
    print("  [OK] Forge shut down and port released")

    print("=== Phase 6: Test Idempotent Close ===")
    res_close_again = subprocess.run(
        ["powershell.exe", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(REPO_ROOT / "scripts" / "close-forge.ps1")],
        close_fds=True,
    )
    assert res_close_again.returncode == 0
    print("  [OK] Second close handled cleanly")

    print("\nALL RUNTIME VERIFICATIONS PASSED SUCCESSFULLY!")


if __name__ == "__main__":
    main()
