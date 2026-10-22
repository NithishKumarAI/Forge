from pathlib import Path
from fastapi.testclient import TestClient

from app.config import settings
from app.main import app


def test_serve_root_and_spa_fallback() -> None:
    client = TestClient(app)

    # 1. Root returns index.html if dist exists
    res = client.get("/")
    if (settings.frontend_dist_path / "index.html").is_file():
        assert res.status_code == 200
        assert "html" in res.headers.get("content-type", "").lower()
    else:
        assert res.status_code == 200
        assert "Frontend build not found" in res.json().get("message", "")

    # 2. SPA routes return index.html
    res_spa = client.get("/arena")
    if (settings.frontend_dist_path / "index.html").is_file():
        assert res_spa.status_code == 200
        assert "html" in res_spa.headers.get("content-type", "").lower()

    # 3. Nonexistent API routes return 404 with API route not found, NOT index.html
    res_api_404 = client.get("/api/definitely_not_a_valid_route")
    assert res_api_404.status_code == 404
    assert res_api_404.json() == {"detail": "API route not found"}

    # 4. Health endpoint works and is not intercepted by SPA catch-all
    res_health = client.get("/health")
    assert res_health.status_code == 200
    assert res_health.json() == {"status": "ok"}


def test_missing_dist_fallback(monkeypatch, tmp_path: Path) -> None:
    empty_dist = tmp_path / "empty_dist"
    empty_dist.mkdir()
    monkeypatch.setattr(settings, "frontend_dist_path", empty_dist)

    client = TestClient(app)
    res_root = client.get("/")
    assert res_root.status_code == 200
    assert "Frontend build not found" in res_root.json().get("message", "")

    res_spa = client.get("/some-spa-route")
    assert res_spa.status_code == 404
    assert res_spa.json() == {"detail": "Frontend build not found"}
