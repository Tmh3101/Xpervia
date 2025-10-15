from __future__ import annotations
import re
from typing import List, Optional, Dict, Any
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine
from .retrived_schema import RetrievedChunk

def _extract_keywords(q: str, min_len: int = 3, max_keywords: int = 8) -> List[str]:
    toks = re.findall(r"\w+", q, flags=re.UNICODE)
    kws = []
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
    config: str = "simple",  # PostgreSQL text search config (e.g., 'simple', 'english')
    course_id: Optional[int] = None,
    doc_types: Optional[List[str]] = None,
    lang: Optional[str] = None,
) -> List[RetrievedChunk]:
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

    rows = []
    phrase = _normalize_phrase(query_text)
    params["phrase_like"] = f"%{phrase}%"
    keywords = _extract_keywords(query_text)
    if keywords:
        or_clauses = []
        for i, kw in enumerate(keywords):
            pname = f"kw{i}"
            params[pname] = f"%{kw}%"
            or_clauses.append(f"c.content ILIKE :{pname}")
            or_clauses.append(f"coalesce(c.metadata->>'title','') ILIKE :{pname}")
        or_sql = " OR ".join(or_clauses)
        alt_sql = f"""
            SELECT
                c.id, c.chunk_uid, c.course_id, c.doc_type, c.lang, c.content,
                0.0 AS score, c.metadata
            FROM public.rag_chunks c
            WHERE {where_sql}
                AND ({or_sql})
            ORDER BY course_id, id DESC
            LIMIT :limit
        """
        try:
            async with engine.connect() as conn:
                res = await conn.execute(text(alt_sql), params)
                rows = [dict(r) for r in res.mappings().all()]
            print(f"[LEXICAL] Keyword ILIKE retrieved {len(rows)} rows; keywords: {keywords}")
        except Exception as e:
            print(f"[LEXICAL] Keyword ILIKE failed: {e}")

        # heuristic scoring: count keyword occurrences, boost title matches    
        try:
            if rows:
                kw_set = keywords
                counts = []
                for r in rows:
                    content = (r.get("content") or "") or ""
                    meta = r.get("metadata") or {}
                    title = ""
                    if isinstance(meta, dict):
                        title = (meta.get("title") or "") or ""
                    content_l = content.lower()
                    title_l = title.lower()
                    cnt = 0
                    for kw in kw_set:
                        cnt += content_l.count(kw)
                        cnt += title_l.count(kw) * 3
                    phrase_found = phrase.lower() in content_l or phrase.lower() in title_l
                    score_raw = cnt + (10 if phrase_found else 0)
                    r["_computed_count"] = score_raw
                    counts.append(score_raw)
                max_count = max(counts) if counts else 1.0
                for r in rows:
                    raw = r.get("_computed_count", 0.0)
                    norm = (raw / max_count) if max_count > 0 else 0.0
                    r["score"] = float(max(0.01, norm))
                print(f"[LEXICAL] Computed keyword scores: {[r['score'] for r in rows]}")
        except Exception as e:
            print(f"[LEXICAL] Keyword scoring failed (non-fatal): {e}")
    print(f"[LEXICAL] Final retrieved raw rows: {len(rows)}")

    # Normalize + dedupe by course_id (prefer highest score per course)
    dedup: Dict[Any, Dict[str, Any]] = {}
    for r in rows:
        cid = r["course_id"]
        sc = float(r.get("score", 0.0) or 0.0)
        if cid not in dedup or sc > dedup[cid]["score"]:
            dedup[cid] = {
                "id": r["id"],
                "chunk_uid": r["chunk_uid"],
                "course_id": r["course_id"],
                "doc_type": r["doc_type"],
                "lang": r["lang"],
                "content": r["content"],
                "score": sc,
                "metadata": r["metadata"],
            }

    results = sorted(dedup.values(), key=lambda x: x["score"], reverse=True)[:top_k]

    # Log discovered course titles when available
    print(f"[LEXICAL] Courses results: {[ (r.get('metadata') and (r['metadata'].get('title') if isinstance(r['metadata'], dict) else None)) for r in results ]}")
    print(f"[LEXICAL] Scores: {[r['score'] for r in results]}")
    return [
        RetrievedChunk(
            id=r["id"],
            chunk_uid=r["chunk_uid"],
            course_id=r["course_id"],
            doc_type=r["doc_type"],
            lang=r["lang"],
            content=r["content"],
            score=float(r["score"]),
            metadata=r["metadata"],
        )
        for r in results
    ]