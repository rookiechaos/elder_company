"""Deterministic hashing utilities."""

import hashlib


def query_statement_hash(statement: str) -> str:
    """Stable SHA-256 hex digest for a SQL statement (process-safe lookup key)."""
    normalized = (statement or "").strip()
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()
