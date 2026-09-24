import hashlib, json
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse
from urllib.robotparser import RobotFileParser
import httpx

USER_AGENT="ForgeCourseBuilder/1.0 (+local educational compiler)"

def robots_allows(url: str, robots_text: str) -> bool:
    parser=RobotFileParser(); parser.set_url(url); parser.parse(robots_text.splitlines())
    return parser.can_fetch(USER_AGENT,url)

def fetch_url(url:str, source:dict, cache_dir:Path, *, client:httpx.Client|None=None, robots_text:str|None=None) -> dict:
    parsed=urlparse(url)
    if source.get("category") == "reference_only" or not source.get("enabled", True):
        raise PermissionError(f"Reference-only source '{source.get('id')}' cannot be fetched or scraped as a copyable corpus.")
    if parsed.scheme != "https" or not any(parsed.path.startswith(p) for p in source["allowed_paths"]): raise ValueError("URL is outside the registered source scope")
    if robots_text is not None and not robots_allows(url,robots_text): raise PermissionError("robots.txt disallows this URL")
    key=hashlib.sha256(url.encode()).hexdigest(); target=cache_dir/f"{key}.json"
    if target.exists(): return json.loads(target.read_text(encoding="utf-8"))
    owner=False
    if client is None: client=httpx.Client(timeout=20,headers={"User-Agent":USER_AGENT},follow_redirects=True); owner=True
    try: response=client.get(url); response.raise_for_status()
    finally:
        if owner: client.close()
    record={"url":url,"retrieved_at":datetime.now(timezone.utc).isoformat(),"content_hash":hashlib.sha256(response.content).hexdigest(),"source_id":source["id"],"http_status":response.status_code,"html":response.text}
    cache_dir.mkdir(parents=True,exist_ok=True); target.write_text(json.dumps(record),encoding="utf-8"); return record
