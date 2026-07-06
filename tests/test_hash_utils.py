"""Tests for deterministic query hashing."""

from utils.hash_utils import query_statement_hash


def test_query_statement_hash_is_stable():
    sql = "SELECT * FROM users WHERE id = ?"
    assert query_statement_hash(sql) == query_statement_hash(sql)
    assert len(query_statement_hash(sql)) == 64


def test_query_statement_hash_differs_for_different_statements():
    a = query_statement_hash("SELECT 1")
    b = query_statement_hash("SELECT 2")
    assert a != b


def test_query_statement_hash_normalizes_whitespace():
    assert query_statement_hash("  SELECT 1  ") == query_statement_hash("SELECT 1")
