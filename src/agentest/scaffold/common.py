import shutil
from pathlib import Path
from re import fullmatch

SAFE_ID_PATTERN = r"^[A-Za-z0-9._-]+$"


class ScaffoldError(ValueError):
    """Raised when an asset cannot be created safely."""


def validate_id(value: str, label: str) -> str:
    if not value or fullmatch(SAFE_ID_PATTERN, value) is None:
        raise ScaffoldError(
            f"{label} ID must be a non-empty directory-safe value matching {SAFE_ID_PATTERN}"
        )
    return value


def require_directory(path: Path, label: str) -> None:
    if not path.is_dir():
        raise ScaffoldError(f"{label} does not exist: {path}")


def write_new_file(path: Path, content: str) -> None:
    if path.exists():
        raise ScaffoldError(f"File already exists and will not be overwritten: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def remove_created_tree(path: Path) -> None:
    """Roll back a tree that the current scaffold operation created."""
    if path.is_dir():
        shutil.rmtree(path)
