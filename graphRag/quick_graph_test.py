"""
Quick Graph-only context tester.
Given a graph_doc_id seed it runs graph lineage expansion only and prints ranked context docs.
"""

from __future__ import annotations

import argparse
import sys
import types
from contextlib import contextmanager
from typing import Any, Dict, List, Tuple

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

import graph_lineage_api as gla
import standalone_lineage_test as lineage_helpers

# Ensure lineage helpers use patched DB accessors before loading API
lineage_helpers.patch_lineage_functions()

# Mock src.* packages required by graph_enhanced_rag_api
src_module = types.ModuleType("src")
src_module.__path__ = []
sys.modules.setdefault("src", src_module)

api_module = types.ModuleType("src.api")
api_module.__path__ = []
sys.modules["src.api"] = api_module
sys.modules["src.api.graph_lineage_api"] = gla

core_module = types.ModuleType("src.core")
core_module.__path__ = []
sys.modules["src.core"] = core_module

search_module = types.ModuleType("src.core.search")
search_module.__path__ = []
sys.modules["src.core.search"] = search_module


class _PlaceholderSemanticEngine:
    """Minimal stub so graph_enhanced_rag_api can import."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        self._docs: List[Dict[str, Any]] = []

    def search(self, query: str, top_k: int = 3, **kwargs: Any) -> List[Dict[str, Any]]:
        return []


semantic_module = types.ModuleType("src.core.search.semantic_engine")
semantic_module.SemanticEngine = _PlaceholderSemanticEngine
sys.modules["src.core.search.semantic_engine"] = semantic_module

import graph_enhanced_rag_api as gra

DEFAULT_RELATIONS = ["BASED_ON", "REFERENCES", "IMPLEMENTS"]
DIRECTION_CHOICES = ("auto", "upstream", "downstream")


def resolve_graph_doc_id(identifier: str) -> str:
    graph_doc_id = lineage_helpers.safe_resolve_document_id(identifier)
    if not graph_doc_id:
        raise ValueError(f"Could not resolve graph_doc_id for '{identifier}'")
    return graph_doc_id


def fetch_seed_document(identifier: str) -> Dict[str, Any]:
    graph_doc_id = resolve_graph_doc_id(identifier)
    query = """
        SELECT
            graph_doc_id,
            source_document_id,
            COALESCE(source_document_id::text, graph_doc_id::text) AS document_id_fallback,
            title,
            hierarchy_level,
            law_id,
            task_code
        FROM graph_documents
        WHERE graph_doc_id = %s
    """
    with lineage_helpers.get_db_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(query, (graph_doc_id,))
            row = cursor.fetchone()
            if not row:
                raise ValueError(f"graph_doc_id {graph_doc_id} not found in graph_documents")

    return {
        "document_id": row.get("document_id_fallback"),
        "graph_doc_id": str(row["graph_doc_id"]),
        "law_id": row.get("law_id"),
        "title": row.get("title") or f"Document {graph_doc_id}",
        "hierarchy_level": row.get("hierarchy_level"),
        "task_code": row.get("task_code"),
        "similarity_score": 1.0,
        "source_type": "seed",
        "graph_distance": 0,
    }


@contextmanager
def _temporary_lineage_resolver(resolver):
    original = gra.get_lineage_upstream
    gra.get_lineage_upstream = resolver
    try:
        yield
    finally:
        gra.get_lineage_upstream = original


def _run_expansion(
    initial_doc: Dict[str, Any],
    *,
    max_hops: int,
    expand_per_doc: int,
    relation_types: List[str],
    min_confidence: float,
    max_docs: int,
    resolver,
) -> List[Dict[str, Any]]:
    with _temporary_lineage_resolver(resolver):
        docs = gra.expand_context_with_graph(
            initial_docs=[initial_doc],
            max_hops=max_hops,
            expand_per_doc=expand_per_doc,
            relation_types=relation_types,
            min_confidence=min_confidence,
        )
    docs.sort(key=lambda doc: doc["relevance_score"], reverse=True)
    return docs[:max_docs]


def _has_graph_expansion(docs: List[Dict[str, Any]]) -> bool:
    return any((doc.get("graph_distance") or 0) > 0 for doc in docs)


def expand_graph_only(
    identifier: str,
    *,
    max_hops: int,
    expand_per_doc: int,
    relation_types: List[str],
    min_confidence: float,
    max_docs: int,
    direction: str,
) -> Tuple[List[Dict[str, Any]], str]:
    initial_doc = fetch_seed_document(identifier)

    if direction == "downstream":
        docs = _run_expansion(
            initial_doc,
            max_hops=max_hops,
            expand_per_doc=expand_per_doc,
            relation_types=relation_types,
            min_confidence=min_confidence,
            max_docs=max_docs,
            resolver=gla.get_lineage_downstream,
        )
        return docs, "downstream"

    # upstream or auto default
    docs = _run_expansion(
        initial_doc,
        max_hops=max_hops,
        expand_per_doc=expand_per_doc,
        relation_types=relation_types,
        min_confidence=min_confidence,
        max_docs=max_docs,
        resolver=gla.get_lineage_upstream,
    )
    chosen = "upstream"

    if direction == "auto" and not _has_graph_expansion(docs):
        downstream_docs = _run_expansion(
            initial_doc,
            max_hops=max_hops,
            expand_per_doc=expand_per_doc,
            relation_types=relation_types,
            min_confidence=min_confidence,
            max_docs=max_docs,
            resolver=gla.get_lineage_downstream,
        )
        if _has_graph_expansion(downstream_docs):
            docs = downstream_docs
            chosen = "downstream"
    return docs, chosen


def format_doc(doc: Dict[str, Any], idx: int) -> str:
    level = doc.get("hierarchy_level")
    relation = doc.get("edge_relation")
    confidence = doc.get("edge_confidence")
    distance = doc.get("graph_distance")
    if not distance:
        rel_text = "seed"
    elif confidence is not None:
        rel_text = f"{relation or 'REL'} ({confidence:.2f})"
    else:
        rel_text = relation or "REL"
    score = doc.get("relevance_score") or 0.0
    return (
        f"{idx:02d}. L{level} {doc.get('title')} "
        f"[score={score:.3f}, dist={distance}, rel={rel_text}]"
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Graph-only expansion tester")
    parser.add_argument("identifier", help="Seed graph_doc_id / law_id / task_code")
    parser.add_argument("--max-hops", type=int, default=5, help="Maximum lineage depth")
    parser.add_argument("--expand-per-doc", type=int, default=8, help="How many related docs to keep per hop")
    parser.add_argument(
        "--relations",
        nargs="*",
        default=None,
        help="Relation types to traverse (default: based on DEFAULT_RELATIONS)",
    )
    parser.add_argument("--min-confidence", type=float, default=0.6, help="Edge confidence filter")
    parser.add_argument("--max-docs", type=int, default=15, help="Max documents to print")
    parser.add_argument(
        "--direction",
        choices=DIRECTION_CHOICES,
        default="auto",
        help="Which lineage direction to traverse (auto tries upstream then downstream)",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    relations = args.relations or DEFAULT_RELATIONS
    docs, used_direction = expand_graph_only(
        args.identifier,
        max_hops=args.max_hops,
        expand_per_doc=args.expand_per_doc,
        relation_types=relations,
        min_confidence=args.min_confidence,
        max_docs=args.max_docs,
        direction=args.direction,
    )

    if not docs:
        print("No documents returned from graph expansion.")
        return

    print(
        f"Seed {args.identifier} produced {len(docs)} docs "
        f"(direction={used_direction}, max_hops={args.max_hops}, expand_per_doc={args.expand_per_doc}, relations={relations})"
    )
    for idx, doc in enumerate(docs, 1):
        print(format_doc(doc, idx))


if __name__ == "__main__":
    main()
