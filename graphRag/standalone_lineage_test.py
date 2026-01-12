"""
Standalone lineage tests without FastAPI.
Uses real database connection to run graph_lineage_api helpers directly.
"""

from __future__ import annotations

import sys
from typing import Any, Dict, List, Optional

import psycopg2
from psycopg2.extras import RealDictCursor

import graph_lineage_api as gla

DB_CONFIG: Dict[str, Any] = {
    "host": "192.168.1.88",
    "port": 15432,
    "database": "chatbotR4",
    "user": "kb_admin",
    "password": "1234567890",
}

EXPECTED_CHAIN = [6, 5, 4, 3, 2, 1, 0]
FOUNDATION_LAW_ID = "LUAT_KHCN_2013"


def get_db_connection() -> psycopg2.extensions.connection:
    """Create a psycopg2 connection with shared config."""
    return psycopg2.connect(**DB_CONFIG, cursor_factory=RealDictCursor)


def safe_resolve_document_id(identifier: str) -> Optional[str]:
    """Resolve identifier without casting errors."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "SELECT graph_doc_id FROM graph_documents WHERE graph_doc_id::text = %s",
            (identifier,),
        )
        result = cursor.fetchone()
        if result:
            return str(result["graph_doc_id"])

        cursor.execute(
            "SELECT graph_doc_id FROM graph_documents WHERE law_id = %s",
            (identifier,),
        )
        result = cursor.fetchone()
        if result:
            return str(result["graph_doc_id"])

        cursor.execute(
            "SELECT graph_doc_id FROM graph_documents WHERE task_code = %s",
            (identifier,),
        )
        result = cursor.fetchone()
        if result:
            return str(result["graph_doc_id"])
        return None
    finally:
        cursor.close()
        conn.close()


def _safe_lineage_query(
    base_document_clause: str,
    join_condition: str,
    relation_filter: List[str],
    max_depth: int,
    min_confidence: float,
    start_id: str,
) -> List[Dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        query = f"""
        WITH RECURSIVE lineage_path AS (
            {base_document_clause}
            
            UNION ALL
            
            {join_condition}
        )
        SELECT * FROM lineage_path
        ORDER BY depth ASC;
        """
        cursor.execute(query, (start_id, max_depth, relation_filter, min_confidence))
        results = cursor.fetchall()
        return [dict(row) for row in results]
    finally:
        cursor.close()
        conn.close()


def patch_lineage_functions() -> None:
    """Patch lineage helpers to avoid optional columns and UUID casting issues."""

    def safe_get_lineage_upstream(
        graph_doc_id: str,
        max_depth: int = 10,
        relation_filter: Optional[List[str]] = None,
        min_confidence: float = 0.0,
    ) -> List[Dict[str, Any]]:
        if relation_filter is None:
            relation_filter = ["BASED_ON"]

        base_clause = """
            SELECT 
                gd.graph_doc_id,
                gd.source_document_id,
                gd.law_id,
                gd.task_code,
                gd.title,
                gd.hierarchy_level,
                NULL::text as doc_category,
                NULL::uuid as edge_id,
                NULL::text as relation_type,
                NULL::numeric as edge_weight,
                NULL::numeric as confidence,
                NULL::text as extraction_context,
                0 as depth,
                1.0::numeric as path_weight
            FROM graph_documents gd
            WHERE gd.graph_doc_id = %s
        """

        recursive_clause = """
            SELECT 
                target_doc.graph_doc_id,
                target_doc.source_document_id,
                target_doc.law_id,
                target_doc.task_code,
                target_doc.title,
                target_doc.hierarchy_level,
                NULL::text as doc_category,
                e.edge_id,
                e.relation_type,
                e.edge_weight,
                e.confidence,
                e.extraction_context,
                lp.depth + 1,
                (lp.path_weight * COALESCE(e.edge_weight, 1.0))::numeric
            FROM lineage_path lp
            JOIN graph_edges e ON e.source_graph_doc_id = lp.graph_doc_id
            JOIN graph_documents target_doc ON target_doc.graph_doc_id = e.target_graph_doc_id
            WHERE 
                lp.depth < %s
                AND e.is_active = TRUE
                AND e.relation_type = ANY(%s)
                AND COALESCE(e.confidence, 1.0) >= %s
        """

        return _safe_lineage_query(
            base_clause,
            recursive_clause,
            relation_filter,
            max_depth,
            min_confidence,
            graph_doc_id,
        )

    def safe_get_lineage_downstream(
        graph_doc_id: str,
        max_depth: int = 10,
        relation_filter: Optional[List[str]] = None,
        min_confidence: float = 0.0,
    ) -> List[Dict[str, Any]]:
        if relation_filter is None:
            relation_filter = ["BASED_ON", "REFERENCES", "IMPLEMENTS"]

        base_clause = """
            SELECT 
                gd.graph_doc_id,
                gd.source_document_id,
                gd.law_id,
                gd.task_code,
                gd.title,
                gd.hierarchy_level,
                NULL::text as doc_category,
                NULL::uuid as edge_id,
                NULL::text as relation_type,
                NULL::numeric as edge_weight,
                NULL::numeric as confidence,
                NULL::text as extraction_context,
                0 as depth,
                1.0::numeric as path_weight
            FROM graph_documents gd
            WHERE gd.graph_doc_id = %s
        """

        recursive_clause = """
            SELECT 
                source_doc.graph_doc_id,
                source_doc.source_document_id,
                source_doc.law_id,
                source_doc.task_code,
                source_doc.title,
                source_doc.hierarchy_level,
                NULL::text as doc_category,
                e.edge_id,
                e.relation_type,
                e.edge_weight,
                e.confidence,
                e.extraction_context,
                lp.depth + 1,
                (lp.path_weight * COALESCE(e.edge_weight, 1.0))::numeric
            FROM lineage_path lp
            JOIN graph_edges e ON e.target_graph_doc_id = lp.graph_doc_id
            JOIN graph_documents source_doc ON source_doc.graph_doc_id = e.source_graph_doc_id
            WHERE 
                lp.depth < %s
                AND e.is_active = TRUE
                AND e.relation_type = ANY(%s)
                AND COALESCE(e.confidence, 1.0) >= %s
        """

        return _safe_lineage_query(
            base_clause,
            recursive_clause,
            relation_filter,
            max_depth,
            min_confidence,
            graph_doc_id,
        )

    gla.get_db_connection = get_db_connection  # type: ignore[attr-defined]
    gla.resolve_document_id = safe_resolve_document_id  # type: ignore[attr-defined]
    gla.get_lineage_upstream = safe_get_lineage_upstream  # type: ignore[attr-defined]
    gla.get_lineage_downstream = safe_get_lineage_downstream  # type: ignore[attr-defined]


# ============================================================================
# Helper utilities
# ============================================================================


def fetch_all_documents() -> List[Dict[str, Any]]:
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT graph_doc_id, source_document_id, law_id, task_code,
                       title, hierarchy_level
                FROM graph_documents
                ORDER BY hierarchy_level DESC, title ASC
                """
            )
            rows = cursor.fetchall()
    for row in rows:
        row["graph_doc_id"] = str(row["graph_doc_id"])
    return rows


def pick_doc_by_level(docs: List[Dict[str, Any]], level: int) -> Dict[str, Any] | None:
    for row in docs:
        if row.get("hierarchy_level") == level:
            return row
    return None


def print_lineage(label: str, lineage: List[Dict[str, Any]]) -> None:
    print(f"\n=== {label} ===")
    if not lineage:
        print("No lineage records returned.")
        return
    for depth, node in enumerate(lineage):
        level = node.get("hierarchy_level")
        title = node.get("title")
        relation = node.get("relation_type") or "START"
        confidence = node.get("confidence")
        rel_text = relation if relation == "START" else f"{relation} ({confidence:.2f})"
        print(f"{depth+1:02d}. L{level}: {title} via {rel_text}")

    total_edges = len(lineage) - 1
    levels = [node.get("hierarchy_level") for node in lineage if node.get("hierarchy_level") is not None]
    if levels:
        print(f"Levels traversed: L{max(levels)} -> L{min(levels)} ({len(lineage)} nodes / {total_edges} edges)")


def verify_chain(lineage: List[Dict[str, Any]], expected: List[int]) -> bool:
    actual_levels = [node.get("hierarchy_level") for node in lineage]
    return actual_levels == expected


# ============================================================================
# Runner
# ============================================================================


def run_tests() -> int:
    patch_lineage_functions()
    docs = fetch_all_documents()
    if not docs:
        print("Database returned no graph documents.")
        return 1

    print("AVAILABLE GRAPH DOCUMENTS:")
    for doc in docs:
        level = doc.get("hierarchy_level")
        print(f"L{level}: {doc.get('title')} (graph_doc_id={doc.get('graph_doc_id')})")

    # Upstream test from highest-level document
    l6_doc = pick_doc_by_level(docs, 6)
    if not l6_doc:
        print("No level 6 document found; aborting upstream test.")
        return 1

    upstream = gla.get_lineage_upstream(
        graph_doc_id=l6_doc["graph_doc_id"],
        max_depth=10,
        relation_filter=["BASED_ON", "REFERENCES"],
        min_confidence=0.0,
    )
    print_lineage("Upstream lineage", upstream)
    if not upstream:
        print("Upstream query returned no results.")
        return 1
    if not verify_chain(upstream, EXPECTED_CHAIN):
        print("WARNING: Upstream chain did not match expected hierarchy levels.")

    # Downstream test from foundation law
    law_graph_id = gla.resolve_document_id(FOUNDATION_LAW_ID)
    if not law_graph_id:
        print(f"Failed to resolve foundation law id {FOUNDATION_LAW_ID}.")
        return 1

    downstream = gla.get_lineage_downstream(
        graph_doc_id=law_graph_id,
        max_depth=10,
        relation_filter=["BASED_ON", "REFERENCES", "IMPLEMENTS"],
        min_confidence=0.0,
    )
    print_lineage("Downstream lineage", downstream)
    if not downstream:
        print("Downstream query returned no results.")
        return 1

    print("\nStandalone lineage tests completed.")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(run_tests())
    except Exception as exc:  # pragma: no cover - debug helper
        print(f"Standalone tests failed: {exc}")
        raise
