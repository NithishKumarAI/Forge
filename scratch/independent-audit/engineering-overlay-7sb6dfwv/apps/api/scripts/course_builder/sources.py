import json
from pathlib import Path
from urllib.parse import urlparse
from app.config import settings

def load_manifest(path: Path = settings.course_sources_path) -> dict:
    data=json.loads(path.read_text(encoding="utf-8"))
    for track, sources in data.items():
        for source in sources:
            if urlparse(source["base_url"]).scheme != "https": raise ValueError("Course sources must use HTTPS")
            if not source.get("allowed_paths"): raise ValueError("Every source needs explicit allowed_paths")
            if any(not path.startswith("/") or ".." in path or "\\" in path for path in source["allowed_paths"]):
                raise ValueError("Source paths must be absolute URL scopes without traversal")
            if urlparse(source["base_url"]).username or urlparse(source["base_url"]).port not in (None,443):
                raise ValueError("Source authentication/custom ports are forbidden")
    return data
