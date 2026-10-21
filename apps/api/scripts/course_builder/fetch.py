"""Explicit development URLs only; redirects are requests requiring fresh authorization."""
import base64
import hashlib
import ipaddress
import json
import socket
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urljoin, urlsplit, unquote
from urllib.robotparser import RobotFileParser
import httpx
from app.services.content_publication import write_immutable
from app.services.content_registry import digest
from app.services.content_paths import safe_path

USER_AGENT = "ForgeCourseBuilder/2.0 (+local educational compiler)"
MAX_BYTES = 2 * 1024 * 1024
MAX_REDIRECTS = 5


def robots_allows(url, robots_text):
    parser = RobotFileParser()
    parser.set_url(url)
    parser.parse(robots_text.splitlines())
    return parser.can_fetch(USER_AGENT, url)


def validate_scope(url, source, *, robots=False):
    parsed = urlsplit(url)
    base = urlsplit(source["base_url"])
    if source.get("category") == "reference_only" or not source.get("enabled", True):
        raise PermissionError("Disabled/reference-only source cannot be fetched")
    if (parsed.scheme != "https" or parsed.hostname != base.hostname or parsed.username or parsed.password
            or parsed.port not in (None, 443) or parsed.fragment or parsed.query):
        raise ValueError("URL is outside the approved HTTPS host scope")
    decoded = parsed.path
    for _ in range(3): decoded = unquote(decoded)
    if decoded != parsed.path or "\\" in decoded or any(x in {".", ".."} for x in decoded.split("/")):
        raise ValueError("Encoded/ambiguous source paths are forbidden")
    paths = ["/robots.txt"] if robots else source["allowed_paths"]
    if not any(decoded == path.rstrip("/") or decoded.startswith(path if path.endswith("/") else path + "/") for path in paths):
        raise ValueError("URL is outside the registered source path scope")
    if source.get("allowed_urls") and not robots and url not in source["allowed_urls"]:
        raise ValueError("URL is not explicitly registered")
    return parsed


def public_addresses(host):
    try: answers = socket.getaddrinfo(host, 443, type=socket.SOCK_STREAM)
    except OSError as error: raise ValueError("Source DNS resolution failed") from error
    addresses = sorted({answer[4][0] for answer in answers})
    if not addresses or any(not ipaddress.ip_address(ip).is_global for ip in addresses):
        raise ValueError("Local/private/reserved source destinations are forbidden")
    return addresses


class PinnedTransport(httpx.HTTPTransport):
    """Connect to a checked IP while retaining original TLS SNI and HTTP Host."""
    def handle_request(self, request):
        host = request.url.host
        addresses = public_addresses(host)
        request.extensions["sni_hostname"] = host
        request.headers["Host"] = host
        request.url = request.url.copy_with(host=addresses[0])
        return super().handle_request(request)


def _download(url, source, *, client=None, robots_text=None, robots=False):
    owner = client is None
    if client is not None and not isinstance(client._transport, httpx.MockTransport):
        raise ValueError("Injected source clients must use MockTransport; production requires pinned DNS")
    if owner:
        client = httpx.Client(timeout=20, headers={"User-Agent": USER_AGENT}, follow_redirects=False, transport=PinnedTransport(), trust_env=False)
    chain = []
    try:
        for step in range(MAX_REDIRECTS + 1):
            parsed = validate_scope(url, source, robots=robots)
            public_addresses(parsed.hostname)
            if not robots and (robots_text is None or not robots_allows(url, robots_text)):
                raise PermissionError("A successful robots policy allowing this URL is required")
            with client.stream("GET", url, follow_redirects=False) as response:
                if not owner:
                    validate_scope(str(response.url), source, robots=robots)
                # Pinned transport changes the transport URL only. Authorization remains
                # on the explicit logical URL and every Location is revalidated.
                chain.append(url)
                if response.is_redirect:
                    if step == MAX_REDIRECTS or "location" not in response.headers:
                        raise ValueError("Redirect count exceeded or missing Location")
                    url = urljoin(url, response.headers["location"])
                    continue
                response.raise_for_status()
                chunks, size = [], 0
                for chunk in response.iter_bytes():
                    size += len(chunk)
                    if size > MAX_BYTES: raise ValueError("Source response exceeds bounded size")
                    chunks.append(chunk)
                return b"".join(chunks), response.encoding or "utf-8", url, chain, response.status_code
    finally:
        if owner: client.close()


def fetch_robots(url, source, *, client=None):
    parsed = validate_scope(url, source)
    origin = f"https://{parsed.hostname}"
    raw, encoding, _, _, _ = _download(origin + "/robots.txt", source, client=client, robots=True)
    return raw.decode(encoding, errors="replace")


def fetch_url(url, source, cache_dir: Path, *, client=None, robots_text=None):
    validate_scope(url, source)
    public_addresses(urlsplit(url).hostname)
    if robots_text is None:
        robots_text = fetch_robots(url, source, client=client)
    if not robots_allows(url, robots_text): raise PermissionError("robots.txt disallows this URL")
    identity = digest({"url": url, "source": source, "cache_version": 2})
    target = safe_path(cache_dir, identity + ".json", must_exist=False)
    if target.exists():
        record = json.loads(target.read_text(encoding="utf-8"))
        raw = base64.b64decode(record["bytes_base64"], validate=True)
        if (record["source_identity"] != digest(source) or record["source_id"] != source["id"] or record["url"] != url
                or record["content_hash"] != hashlib.sha256(raw).hexdigest()
                or record["html"] != raw.decode(record["encoding"], errors="replace")):
            raise ValueError("Source cache integrity/identity mismatch")
        for destination in record["redirect_chain"]:
            validate_scope(destination, source)
            public_addresses(urlsplit(destination).hostname)
            if not robots_allows(destination, robots_text): raise PermissionError("Cached redirect violates robots")
        validate_scope(record["final_url"], source)
        if not record["redirect_chain"] or record["redirect_chain"][-1] != record["final_url"]:
            raise ValueError("Source cache final destination mismatch")
        return record
    raw, encoding, final, chain, status = _download(url, source, client=client, robots_text=robots_text)
    record = {"url": url, "final_url": final, "redirect_chain": chain, "source_identity": digest(source),
        "retrieved_at": datetime.now(timezone.utc).isoformat(), "source_id": source["id"], "http_status": status,
        "encoding": encoding, "content_hash": hashlib.sha256(raw).hexdigest(),
        "bytes_base64": base64.b64encode(raw).decode(), "html": raw.decode(encoding, errors="replace")}
    write_immutable(target, record)
    return record
