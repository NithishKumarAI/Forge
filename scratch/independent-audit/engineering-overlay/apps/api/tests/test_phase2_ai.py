"""Retired model routes have deterministic replacements, without deleting their stored history."""
from fastapi.testclient import TestClient
from app.main import create_app

def test_runtime_exposes_no_model_tutor_doubt_cost_or_generation_routes():
    app=create_app()
    routes={route.path for route in app.routes}
    assert not any(path.startswith(('/api/ai','/api/tutor','/api/doubt')) for path in routes)
    assert '/api/curricula/generate-preview' not in routes
    assert '/api/guidance/search' in routes and '/api/assessment/start' in routes
    assert '/api/curricula/drafts' in routes and '/api/editions/curricula/{curriculum_id}/confirm' in routes
