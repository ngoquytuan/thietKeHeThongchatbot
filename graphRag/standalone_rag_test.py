"""
Standalone Graph RAG test without FastAPI or SemanticEngine dependency.
Creates a dummy SemanticEngine and runs graph_enhanced_rag_api directly.
"""

from __future__ import annotations

import asyncio
import types
import sys
from typing import Any, Dict, List

import psycopg2
from psycopg2.extras import RealDictCursor

import graph_lineage_api as gla
import standalone_lineage_test as lineage_helpers

# Ensure graph_lineage_api uses safe DB helpers
lineage_helpers.patch_lineage_functions()

DB_CONFIG = lineage_helpers.DB_CONFIG

# ---------------------------------------------------------------------------
# Mock src.* packages expected by graph_enhanced_rag_api
# ---------------------------------------------------------------------------

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


class DummySemanticEngine:
    """Minimal SemanticEngine replacement that returns graph documents."""

    def __init__(self) -> None:
        self._documents = self._load_documents()

    @staticmethod
    def _load_documents() -> List[Dict[str, Any]]:
        with lineage_helpers.get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT graph_doc_id,
                           COALESCE(source_document_id::text, graph_doc_id::text) AS document_id,
                           title,
                           hierarchy_level
                    FROM graph_documents
                    ORDER BY hierarchy_level DESC, title ASC
                    """
                )
                rows = cursor.fetchall()
        documents: List[Dict[str, Any]] = []
        base_score = 0.95
        for idx, row in enumerate(rows):
            documents.append(
                {
                    "document_id": row["document_id"],
                    "graph_doc_id": str(row["graph_doc_id"]),
                    "title": row["title"],
                    "hierarchy_level": row["hierarchy_level"],
                    "doc_category": None,
                    "content": f"Stub content for {row['title']}",
                    "similarity_score": round(base_score - idx * 0.05, 2),
                }
            )
        return documents

    def search(self, query: str, top_k: int = 3, **kwargs: Any) -> List[Dict[str, Any]]:  # kwargs keep parity
        return self._documents[:top_k]


semantic_module = types.ModuleType("src.core.search.semantic_engine")
semantic_module.SemanticEngine = DummySemanticEngine
sys.modules["src.core.search.semantic_engine"] = semantic_module


# ---------------------------------------------------------------------------
# Import API module now that dependencies exist
# ---------------------------------------------------------------------------

import graph_enhanced_rag_api as gra  # noqa: E402  pylint: disable=wrong-import-position


# Patch psycopg2.connect usage within graph_enhanced_rag_api
real_connect = psycopg2.connect

def patched_connect(*args: Any, **kwargs: Any):
    kwargs.update(DB_CONFIG)
    kwargs.setdefault("cursor_factory", RealDictCursor)
    return real_connect(*args, **kwargs)

gra.psycopg2.connect = patched_connect  # type: ignore[attr-defined]


async def run_graph_rag_demo() -> gra.GraphRAGResponse:
    request = gra.GraphRAGRequest(
        query="Tại sao Báo cáo ĐTCT Q1/2025 phải tuân thủ Luật KHCN?",
        top_k=3,
        expand_graph=True,
        max_hops=3,
        expand_per_doc=3,
        include_lineage=True,
    )
    return await gra.graph_enhanced_rag(request)


def print_response(response: gra.GraphRAGResponse) -> None:
    print(f"Query: {response.query}")
    print(f"Context docs: {response.total_documents} (semantic={response.semantic_matches}, graph={response.graph_expanded})")
    for idx, doc in enumerate(response.context_documents, start=1):
        print(
            f"{idx:02d}. [{doc.source_type}] L{doc.hierarchy_level} "
            f"{doc.title} (score={doc.relevance_score:.3f}, graph_dist={doc.graph_distance})"
        )
    if response.lineage_paths:
        print("\nLineage paths:")
        for path in response.lineage_paths:
            titles = " -> ".join(node["title"] for node in path.path)
            print(f"- {path.title}: {titles}")
    if response.graph_stats:
        print("\nGraph stats:")
        for key, value in response.graph_stats.items():
            print(f"  {key}: {value}")
    print(f"Processing time: {response.processing_time_ms:.2f} ms")


if __name__ == "__main__":
    rag_response = asyncio.run(run_graph_rag_demo())
    print_response(rag_response)
