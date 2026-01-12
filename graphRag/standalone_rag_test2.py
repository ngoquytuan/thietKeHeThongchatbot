"""
Standalone Graph RAG test without FastAPI or SemanticEngine dependency.
Creates a dummy SemanticEngine and runs graph_enhanced_rag_api directly.
"""

from __future__ import annotations

import asyncio
import re
import types
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from typing import Any, Dict, List, Tuple

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


def _tokenize(text: str) -> List[str]:
    text = (text or "").lower()
    # keep Vietnamese letters, numbers
    text = re.sub(r"[^\w\sÀ-Ỵà-ỵ]", " ", text)
    toks = [t for t in text.split() if len(t) >= 2]
    return toks


def _simple_overlap_score(query: str, title: str, content: str) -> float:
    q = set(_tokenize(query))
    if not q:
        return 0.0
    d = _tokenize(title) + _tokenize(content)
    if not d:
        return 0.0
    overlap = sum(1 for t in d if t in q)
    # normalize (cap)
    return min(1.0, overlap / max(6, len(q)))


class DummySemanticEngine:
    """
    Minimal SemanticEngine replacement that returns graph documents,
    but with a basic scoring by query-token overlap to avoid 'random top_k'.
    """

    def __init__(self) -> None:
        self._documents = self._load_documents()

    @staticmethod
    def _load_documents() -> List[Dict[str, Any]]:
        with lineage_helpers.get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT
                        graph_doc_id,
                        source_document_id,
                        COALESCE(source_document_id::text, graph_doc_id::text) AS document_id_fallback,
                        title,
                        hierarchy_level,
                        law_id
                    FROM graph_documents
                    ORDER BY hierarchy_level DESC, title ASC
                    """
                )
                rows = cursor.fetchall()

        docs: List[Dict[str, Any]] = []
        for row in rows:
            # IMPORTANT: document_id should be the UUID from source_document_id if exists
            document_id = (row.get("source_document_id") or row.get("document_id_fallback"))
            title = row["title"]
            docs.append(
                {
                    "document_id": str(document_id) if document_id is not None else None,
                    "graph_doc_id": str(row["graph_doc_id"]),
                    "law_id": row.get("law_id"),
                    "title": title,
                    "hierarchy_level": row.get("hierarchy_level"),
                    "doc_category": None,
                    # keep stub content, but make it slightly more useful for overlap scoring
                    "chunk_text": None,
                    "content": f"{title}. Văn bản liên quan đến: {row.get('law_id') or ''}",
                    "similarity_score": 0.0,  # filled at search-time
                }
            )
        return docs

    def search(self, query: str, top_k: int = 3, **kwargs: Any) -> List[Dict[str, Any]]:
        scored: List[Tuple[float, Dict[str, Any]]] = []
        for d in self._documents:
            s = _simple_overlap_score(query, d.get("title", ""), d.get("content", ""))
            # small bonus if query mentions "luật" and doc has law_id
            if "luật" in query.lower() and d.get("law_id"):
                s = min(1.0, s + 0.10)
            dd = dict(d)
            dd["similarity_score"] = round(s, 3)
            scored.append((s, dd))

        scored.sort(key=lambda x: x[0], reverse=True)

        # fallback: if everything is 0, just return highest-level docs to allow lineage expansion
        top = [dd for s, dd in scored if s > 0][:top_k]
        if len(top) < top_k:
            # pad with remaining docs (stable)
            remainder = [dd for s, dd in scored if dd not in top]
            top += remainder[: (top_k - len(top))]
        return top[:top_k]


semantic_module = types.ModuleType("src.core.search.semantic_engine")
semantic_module.SemanticEngine = DummySemanticEngine
sys.modules["src.core.search.semantic_engine"] = semantic_module


# ---------------------------------------------------------------------------
# Import API module now that dependencies exist
# ---------------------------------------------------------------------------

import graph_enhanced_rag_api as gra  # noqa: E402  pylint: disable=wrong-import-position


# Patch psycopg2.connect usage within graph_enhanced_rag_api
_real_connect = psycopg2.connect


def patched_connect(*args: Any, **kwargs: Any):
    kwargs.update(DB_CONFIG)
    kwargs.setdefault("cursor_factory", RealDictCursor)
    return _real_connect(*args, **kwargs)


gra.psycopg2.connect = patched_connect  # type: ignore[attr-defined]


async def run_graph_rag_demo() -> gra.GraphRAGResponse:
    request = gra.GraphRAGRequest(
        query="Tại sao Báo cáo ĐTCT Q1/2025 phải tuân thủ Luật KHCN?",
        top_k=3,
        expand_graph=True,
        max_hops=5,           # tăng nhẹ để đủ đi tới L0 trong chain dài
        expand_per_doc=6,     # tăng để lấy được nhiều node trong lineage[1:]
        include_lineage=True,

        # KEY FIX: cho phép lineage đi qua REFERENCES/IMPLEMENTS thay vì chỉ BASED_ON
        relation_types=["BASED_ON", "REFERENCES", "IMPLEMENTS"],

        # optional: lọc confidence để khỏi lấy edge rác
        min_confidence=0.6,
    )
    return await gra.graph_enhanced_rag(request)


def print_response(response: gra.GraphRAGResponse) -> None:
    print(f"Query: {response.query}")
    print(
        f"Context docs: {response.total_documents} "
        f"(semantic={response.semantic_matches}, graph={response.graph_expanded})"
    )
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
