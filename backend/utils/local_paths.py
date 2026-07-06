"""
Local-only paths under do-not-upload/ (excluded from git / GitHub).
"""

from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent.parent
DO_NOT_UPLOAD = _REPO_ROOT / "do-not-upload"

LOCAL_SUBDIRS = (
    "data",
    "logs",
    "env",
    "storage/images",
    "storage/videos",
    "storage/audio",
    "cache/optimized_images",
    "cache/pytest",
    "coverage",
)


def ensure_local_dirs() -> None:
    """Create do-not-upload subdirectories if missing."""
    for rel in LOCAL_SUBDIRS:
        (DO_NOT_UPLOAD / rel).mkdir(parents=True, exist_ok=True)


def local_path(*parts: str) -> Path:
    """Return a path under do-not-upload/, creating parent dirs."""
    target = DO_NOT_UPLOAD.joinpath(*parts)
    target.parent.mkdir(parents=True, exist_ok=True)
    return target


def default_database_url() -> str:
    ensure_local_dirs()
    return f"sqlite:///{local_path('data', 'elder_company.db').resolve()}"


def default_log_file() -> str:
    ensure_local_dirs()
    return str(local_path("logs", "app.log"))


def default_error_log_file() -> str:
    ensure_local_dirs()
    return str(local_path("logs", "error.log"))


def default_storage_dir() -> str:
    ensure_local_dirs()
    return str(local_path("storage"))


def env_file_path() -> Path:
    ensure_local_dirs()
    return local_path("env", ".env")
