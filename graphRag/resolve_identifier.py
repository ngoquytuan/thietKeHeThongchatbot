"""Identifier resolution helper for GraphRAG endpoints.

Implements the strategy described in resolve_identifier.md so clients can call
GET /api/graph/resolve?identifier=... and receive a canonical center node.
"""

from __future__ import annotations

import argparse
import json
import sys
import uuid
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

import standalone_lineage_test as lineage_helpers

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

NODE_FIELDS = (
    "graph_doc_id",
    "source_document_id",
    "title",
    "hierarchy_level",
    "law_id",
    "document_number",
    "task_code",
)

TEXT_MATCH_PRIORITY = ("law_id", "document_number", "task_code")

_AVAILABLE_COLUMNS: Optional[set[str]] = None
_BASE_SELECT_CACHE: Optional[str] = None


@dataclass
class ResolveResult:
    """Normalized payload returned by resolve_identifier."""

    status: str  # found | conflict | not_found
    match_type: Optional[str]
    confidence: float
    center: Optional[Dict[str, Any]]
    candidates: List[Dict[str, Any]]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "status": self.status,
            "match_type": self.match_type,
            "confidence": self.confidence,
            "center": self.center,
            "candidates": self.candidates,
        }


def resolve_identifier(identifier: str, *, max_candidates: int = 5) -> ResolveResult:
    """Resolve any supported identifier into a canonical graph node."""

    if not isinstance(identifier, str):
        raise ValueError("identifier must be a string")
    trimmed = identifier.strip()
    if not trimmed:
        raise ValueError("identifier must not be empty")
    if max_candidates < 1:
        raise ValueError("max_candidates must be >= 1")

    parsed_uuid = _try_parse_uuid(trimmed)
    with lineage_helpers.get_db_connection() as conn:
        with conn.cursor() as cursor:
            _ensure_column_metadata(cursor)
            if parsed_uuid:
                return _resolve_uuid(cursor, str(parsed_uuid), max_candidates)
            return _resolve_text(cursor, trimmed, max_candidates)


def _try_parse_uuid(identifier: str) -> Optional[uuid.UUID]:
    try:
        return uuid.UUID(identifier)
    except (ValueError, AttributeError, TypeError):
        return None


def _ensure_column_metadata(cursor) -> None:
    """Populate cached column info for graph_documents."""

    global _AVAILABLE_COLUMNS, _BASE_SELECT_CACHE
    if _AVAILABLE_COLUMNS is not None and _BASE_SELECT_CACHE is not None:
        return

    cursor.execute(
        """
        SELECT column_name
        FROM information_schema.columns
        WHERE table_schema = current_schema()
          AND table_name = 'graph_documents'
        """
    )
    rows = cursor.fetchall()
    columns: set[str] = set()
    for row in rows:
        if isinstance(row, dict):
            columns.add(row.get("column_name"))
        else:
            columns.add(row[0])
    _AVAILABLE_COLUMNS = {col for col in columns if col}

    select_parts = [
        "graph_doc_id::text AS graph_doc_id",
        "source_document_id::text AS source_document_id",
        "title",
        "hierarchy_level",
        "law_id",
        _column_or_null("document_number", cast="text"),
        "task_code",
    ]
    _BASE_SELECT_CACHE = "SELECT\n    " + ",\n    ".join(select_parts) + "\nFROM graph_documents"


def _column_or_null(column: str, *, cast: Optional[str] = None) -> str:
    if _AVAILABLE_COLUMNS and column in _AVAILABLE_COLUMNS:
        return column
    null_expr = "NULL"
    if cast:
        null_expr += f"::{cast}"
    return f"{null_expr} AS {column}"


def _resolve_uuid(cursor, identifier: str, max_candidates: int) -> ResolveResult:
    graph_matches = _fetch_by_column(cursor, "graph_doc_id", identifier, limit=2)
    if graph_matches:
        return _rows_to_result(graph_matches, identifier, match_type="graph_doc_id")

    source_matches = _fetch_by_column(cursor, "source_document_id", identifier, limit=max(2, max_candidates))
    if source_matches:
        return _rows_to_result(source_matches, identifier, match_type="source_document_id")

    return ResolveResult(status="not_found", match_type=None, confidence=0.0, center=None, candidates=[])


def _resolve_text(cursor, identifier: str, max_candidates: int) -> ResolveResult:
    rows = _fetch_text_matches(cursor, identifier, limit=max_candidates)
    if not rows:
        return ResolveResult(status="not_found", match_type=None, confidence=0.0, center=None, candidates=[])

    match_type = _infer_match_type(rows[0], identifier)
    if len(rows) == 1:
        return ResolveResult(
            status="found",
            match_type=match_type,
            confidence=1.0,
            center=_project_row(rows[0]),
            candidates=[],
        )

    candidates = [_project_candidate(row, identifier) for row in rows]
    return ResolveResult(
        status="conflict",
        match_type=match_type,
        confidence=0.0,
        center=None,
        candidates=candidates,
    )


def _base_select() -> str:
    if not _BASE_SELECT_CACHE:
        raise RuntimeError("Column metadata not initialized")
    return _BASE_SELECT_CACHE


def _fetch_by_column(cursor, column: str, value: str, *, limit: int) -> List[Dict[str, Any]]:
    query = f"{_base_select()}\nWHERE {column} = %s\nLIMIT {limit}"
    cursor.execute(query, (value,))
    return cursor.fetchall()


def _fetch_text_matches(cursor, identifier: str, *, limit: int) -> List[Dict[str, Any]]:
    searchable_columns = [col for col in TEXT_MATCH_PRIORITY if _AVAILABLE_COLUMNS is None or col in _AVAILABLE_COLUMNS]
    if not searchable_columns:
        raise RuntimeError("graph_documents table lacks searchable identifier columns")

    where_clauses = [f"{col} = %s" for col in searchable_columns]
    order_clauses = [f"WHEN {col} = %s THEN {idx + 1}" for idx, col in enumerate(searchable_columns)]

    where_sql = " OR ".join(where_clauses)
    order_sql = "\n        ".join(order_clauses)

    query = (
        f"{_base_select()}\n"
        f"WHERE {where_sql}\n"
        "ORDER BY\n"
        "    CASE\n"
        f"        {order_sql}\n"
        "        ELSE 9\n"
        "    END,\n"
        "    hierarchy_level ASC\n"
        f"LIMIT {max(1, limit)}\n"
    )
    params = [identifier] * len(searchable_columns) * 2
    cursor.execute(query, tuple(params))
    return cursor.fetchall()


def _rows_to_result(rows: List[Dict[str, Any]], identifier: str, *, match_type: str) -> ResolveResult:
    if len(rows) == 1:
        return ResolveResult(
            status="found",
            match_type=match_type,
            confidence=1.0,
            center=_project_row(rows[0]),
            candidates=[],
        )

    candidates = [_project_candidate(row, identifier, forced_match_type=match_type) for row in rows]
    return ResolveResult(
        status="conflict",
        match_type=match_type,
        confidence=0.0,
        center=None,
        candidates=candidates,
    )


def _project_row(row: Dict[str, Any]) -> Dict[str, Any]:
    return {field: row.get(field) for field in NODE_FIELDS}


def _project_candidate(row: Dict[str, Any], identifier: str, *, forced_match_type: Optional[str] = None) -> Dict[str, Any]:
    projected = _project_row(row)
    projected["match_type"] = forced_match_type or _infer_match_type(row, identifier)
    return projected


def _infer_match_type(row: Dict[str, Any], identifier: str) -> str:
    for field in ("graph_doc_id", "source_document_id", "law_id", "document_number", "task_code"):
        value = row.get(field)
        if value is None:
            continue
        if isinstance(value, str) and value == identifier:
            return field
    return "unknown"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Resolve a graph identifier into a graph_doc_id")
    parser.add_argument("identifier", help="graph_doc_id / source_document_id / law_id / document_number / task_code")
    parser.add_argument("--max-candidates", type=int, default=5, help="Maximum candidates to return when ambiguous")
    parser.add_argument("--json", action="store_true", help="Output JSON instead of human-readable text")
    parser.add_argument("--allow-conflict", action="store_true", help="Exit with code 0 even when multiple matches are found")
    return parser.parse_args()


def _print_result(result: ResolveResult, *, as_json: bool) -> None:
    if as_json:
        print(json.dumps(result.to_dict(), ensure_ascii=False, indent=2))
        return

    print(f"status={result.status} match_type={result.match_type} confidence={result.confidence}")
    if result.center:
        print("center:")
        for field in NODE_FIELDS:
            print(f"  {field}: {result.center.get(field)}")
    if result.candidates:
        print("candidates:")
        for idx, candidate in enumerate(result.candidates, 1):
            match_type = candidate.get("match_type")
            print(f"  {idx:02d}. match_type={match_type}")
            for field in NODE_FIELDS:
                print(f"        {field}: {candidate.get(field)}")


def main() -> int:
    args = parse_args()
    try:
        result = resolve_identifier(args.identifier, max_candidates=args.max_candidates)
    except ValueError as exc:
        print(f"Invalid input: {exc}", file=sys.stderr)
        return 2

    _print_result(result, as_json=args.json)

    if result.status == "found":
        return 0
    if result.status == "conflict":
        return 0 if args.allow_conflict else 3
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
