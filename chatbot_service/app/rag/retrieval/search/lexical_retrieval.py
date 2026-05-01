from __future__ import annotations
import re
from typing import List, Optional, Dict, Any
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine
from .retrived_schema import RetrievedChunk

def _extract_keywords(q: str, min_len: int = 3, max_keywords: int = 8) -> List[str]:
    toks = re.findall(r"\w+", q, flags=re.UNICODE)
    kws: List[str] = []
    for t in toks:
        tl = t.strip().lower()
        if not tl or len(tl) < min_len:
            continue
        if tl.isdigit():
            continue
        kws.append(tl)
        if len(kws) >= max_keywords:
            break
    return kws

def _normalize_phrase(q: str) -> str:
    return re.sub(r"\s+", " ", q.strip())

async def lexical_retrieve(
    engine: AsyncEngine,
    query_text: str,
    top_k: int = 20,
    config: str = "simple",
    course_id: Optional[int] = None,
    doc_types: Optional[List[str]] = None,
    lang: Optional[str] = None,
) -> List[RetrievedChunk]:
    """
    Lexical retrieval on public.rag_docs using text search, title/meta and keyword ILIKE fallback.
    Returns RetrievedChunk objects with .text and .meta fields.
    """
    if not query_text or not isinstance(query_text, str) or not query_text.strip():
        return []

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

    rows: List[Dict[str, Any]] = []
    phrase = _normalize_phrase(query_text)
    params["phrase_like"] = f"%{phrase}%"
    keywords = _extract_keywords(query_text)

    # Phrase/title match first (meta->>'title' or text)
    phrase_sql = f"""
        SELECT
            id, course_id, doc_type, lang, text,
            100.0 AS score, meta
        FROM public.rag_docs
        WHERE {where_sql}
          AND (
                lower(coalesce(meta->>'title','')) ILIKE lower(:phrase_like)
                OR lower(text) ILIKE lower(:phrase_like)
              )
        ORDER BY course_id, id DESC
        LIMIT :limit
    """
    try:
        async with engine.connect() as conn:
            res = await conn.execute(text(phrase_sql), params)
            rows = [dict(r) for r in res.mappings().all()]
    except Exception:
        rows = []

    # Fulltext if none found
    if not rows:
        ft_sql = f"""
            WITH q AS (
                SELECT plainto_tsquery(:cfg, :q) AS tsq
            )
            SELECT
                id, course_id, doc_type, lang, text,
                ts_rank_cd(to_tsvector(:cfg, text), (SELECT tsq FROM q)) AS score,
                meta
            FROM public.rag_docs, q
            WHERE {where_sql}
              AND to_tsvector(:cfg, text) @@ q.tsq
            ORDER BY score DESC
            LIMIT :limit
        """
        try:
            async with engine.connect() as conn:
                res = await conn.execute(text(ft_sql), params)
                rows = [dict(r) for r in res.mappings().all()]
        except Exception:
            rows = []

    # Keyword fallback
    if not rows and keywords:
        or_clauses = []
        for i, kw in enumerate(keywords):
            pname = f"kw{i}"
            params[pname] = f"%{kw}%"
            or_clauses.append(f"text ILIKE :{pname}")
            or_clauses.append(f"coalesce(meta->>'title','') ILIKE :{pname}")
        or_sql = " OR ".join(or_clauses)
        alt_sql = f"""
            SELECT
                id, course_id, doc_type, lang, text,
                0.0 AS score, meta
            FROM public.rag_docs
            WHERE {where_sql}
              AND ({or_sql})
            ORDER BY course_id, id DESC
            LIMIT :limit
        """
        try:
            async with engine.connect() as conn:
                res = await conn.execute(text(alt_sql), params)
                rows = [dict(r) for r in res.mappings().all()]
        except Exception:
            rows = []

    # Heuristic scoring (count keywords in text + title boost)
    if rows:
        kw_set = keywords
        counts = []
        for r in rows:
            text_field = (r.get("text") or "") or ""
            meta = r.get("meta") or {}
            title = ""
            if isinstance(meta, dict):
                title = (meta.get("title") or "") or ""
            text_l = text_field.lower()
            title_l = title.lower()
            cnt = 0
            for kw in kw_set:
                cnt += text_l.count(kw)
                cnt += title_l.count(kw) * 3
            phrase_found = phrase.lower() in text_l or phrase.lower() in title_l
            score_raw = cnt + (10 if phrase_found else 0)
            r["_computed_count"] = score_raw
            counts.append(score_raw)
        max_count = max(counts) if counts else 1.0
        for r in rows:
            raw = r.get("_computed_count", 0.0)
            norm = (raw / max_count) if max_count > 0 else 0.0
            r["score"] = float(max(0.01, norm))

    # dedupe by course_id (keep best score per course) and build results
    dedup: Dict[Any, Dict[str, Any]] = {}
    for r in rows:
        cid = r["course_id"]
        sc = float(r.get("score", 0.0) or 0.0)
        if cid not in dedup or sc > dedup[cid]["score"]:
            dedup[cid] = {
                "id": r["id"],
                "course_id": r["course_id"],
                "doc_type": r["doc_type"],
                "lang": r.get("lang"),
                "text": r["text"],
                "score": sc,
                "meta": r.get("meta"),
            }

    results = sorted(dedup.values(), key=lambda x: x["score"], reverse=True)[:top_k]

    return [
        RetrievedChunk(
            id=r["id"],
            course_id=r["course_id"],
            doc_type=r["doc_type"],
            lang=r.get("lang"),
            text=r["text"],
            score=float(r["score"]),
            meta=r.get("meta") or {},
        )
        for r in results
    ]