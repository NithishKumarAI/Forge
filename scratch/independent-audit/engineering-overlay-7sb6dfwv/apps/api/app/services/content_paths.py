"""Paths in registry manifests are POSIX-relative; links/junctions are not trusted."""
from pathlib import Path, PureWindowsPath


class ContentPathError(ValueError):
    pass


def validate_relative_path(value: str) -> str:
    if (not value or "\\" in value or ":" in value or "\x00" in value
            or Path(value).is_absolute() or PureWindowsPath(value).drive
            or any(part in {"", ".", ".."} for part in value.split("/"))):
        raise ContentPathError(f"Expected a safe relative content path: {value!r}")
    return value


def reject_links(path: Path) -> None:
    for part in (path, *path.parents):
        if part.is_symlink() or (hasattr(part, "is_junction") and part.is_junction()):
            raise ContentPathError(f"Symlink/junction is not allowed in content/storage path: {part}")


def safe_path(root: Path, relative: str, *, must_exist: bool = True) -> Path:
    validate_relative_path(relative)
    root = root.absolute()
    candidate = root / relative
    reject_links(candidate)
    if not candidate.resolve().is_relative_to(root.resolve()):
        raise ContentPathError("Content path escapes its configured root")
    if must_exist and not candidate.is_file():
        raise ContentPathError(f"Content file is missing: {candidate}")
    return candidate
