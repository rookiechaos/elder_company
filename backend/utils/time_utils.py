"""UTC datetime helpers (replacement for deprecated datetime.utcnow)."""

from datetime import datetime, timezone


def utc_now() -> datetime:
    """Return current UTC time as naive datetime (drop-in for datetime.utcnow())."""
    return datetime.now(timezone.utc).replace(tzinfo=None)
