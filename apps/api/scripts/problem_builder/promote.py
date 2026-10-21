"""Promotion consumes reviewed archives; historical accepted files never move."""
from pathlib import Path
from scripts.content_checks.publish import publish_package, read


def promote(track, key, *, package_path: Path | None = None, session=None):
    if package_path is None or session is None:
        raise ValueError("Promotion requires exact candidate validation, human review and an explicit release/database; use scripts.content_checks.publish")
    if any(e["candidate"]["content_key"] != f"arena/{key}" for e in read(package_path)["entries"]):
        raise ValueError("Release does not match the requested content")
    return publish_package(package_path, session)


if __name__ == "__main__":
    raise SystemExit("Use python -m scripts.content_checks.publish --help. Accepted files are immutable.")
