from __future__ import annotations
from typing import List, Optional, Dict, Any
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine
from .retrived_schema import RetrievedChunk

def _embedding_to_string(embedding: List[float]) -> str:
    # produce Postgres vector literal compatible string if using text param approach
    return "[" + ",".join(f"{v:.6f}" for v in embedding) + "]"

async def semantic_retrieve(
    engine: AsyncEngine,
    query_embedding: List[float],
    top_k: int = 8,
    min_score: Optional[float] = None,
    course_id: Optional[int] = None,
    doc_types: Optional[List[str]] = None,
    lang: Optional[str] = None,
) -> List[RetrievedChunk]:
    """
    Semantic retrieval against public.rag_docs.embedding (vector).
    Returns list of RetrievedChunk (uses text column).
    """
    filters = ["1=1"]
    params: Dict[str, Any] = {"qvec": _embedding_to_string(query_embedding), "limit": top_k}

    if course_id is not None:
        filters.append("course_id = :course_id")
        params["course_id"] = course_id
    if lang is not None:
        filters.append("lang = :lang")
        params["lang"] = lang
    if doc_types:
        filters.append("doc_type = ANY(:doc_types)")
        params["doc_types"] = doc_types

    where_sql = " AND ".join(filters)

    sql = f"""
        SELECT
            id,
            course_id,
            doc_type,
            lang,
            text,
            (1 - (embedding <=> :qvec)) AS score,
            meta
        FROM public.rag_docs
        WHERE {where_sql}
        ORDER BY embedding <=> :qvec ASC
        LIMIT :limit
    """

    rows = []
    async with engine.connect() as conn:
        res = await conn.execute(text(sql), params)
        # materialize to dicts
        rows = [dict(r) for r in res.mappings().all()]

    out: List[RetrievedChunk] = []
    for r in rows:
        score = float(r.get("score") or 0.0)
        if (min_score is None) or (score >= min_score):
            out.append(
                RetrievedChunk(
                    id=r["id"],
                    course_id=r["course_id"],
                    doc_type=r["doc_type"],
                    lang=r.get("lang"),
                    text=r.get("text") or "",
                    score=score,
                    meta=r.get("meta") or {},
                )
            )
    return out
