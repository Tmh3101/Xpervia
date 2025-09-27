from __future__ import annotations
from typing import List, Optional, Dict, Any
from sqlalchemy import text
from sqlalchemy.engine import Engine
from .retrived_schema import RetrievedChunk

async def lexical_retrieve(
    engine: Engine,
    query_text: str,
    top_k: int = 20,
    config: str = "simple",  # PostgreSQL text search config (e.g., 'simple', 'english')
    course_id: Optional[int] = None,
    doc_types: Optional[List[str]] = None,
    lang: Optional[str] = None,
) -> List[RetrievedChunk]:
    filters = ["1=1"]
    params: Dict[str, Any] = {"q": query_text, "limit": top_k, "cfg": config}

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

    # On-the-fly tsvector; for production create a computed column and a GIN index
    sql = f"""
        WITH q AS (
            SELECT plainto_tsquery(:cfg, :q) AS tsq
        )
        SELECT
            c.id,
            c.chunk_uid,
            c.course_id,
            c.doc_type,
            c.lang,
            c.content,
            ts_rank_cd(to_tsvector(:cfg, c.content), (SELECT tsq FROM q)) AS score,
            c.metadata
        FROM public.rag_chunks c, q
        WHERE {where_sql}
          AND to_tsvector(:cfg, c.content) @@ q.tsq
        ORDER BY score DESC
        LIMIT :limit
    """

    rows = []
    async with engine.connect() as conn:
        res = await conn.execute(text(sql), params)
        rows = res.mappings().all()

    return [
        RetrievedChunk(
            id=r["id"],
            chunk_uid=r["chunk_uid"],
            course_id=r["course_id"],
            doc_type=r["doc_type"],
            lang=r["lang"],
            content=r["content"],
            score=float(r["score"]) if r["score"] is not None else 0.0,
            metadata=r["metadata"],
        )
        for r in rows
    ]