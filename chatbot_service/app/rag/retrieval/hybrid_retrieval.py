from __future__ import annotations
from typing import List, Optional, Any, Dict
from sqlalchemy.ext.asyncio import AsyncEngine
from .search.retrived_schema import HybridRetrieved
from .search.semantic_retrieval import semantic_retrieve
from .search.lexical_retrieval import lexical_retrieve

def _minmax_norm(values: List[float]) -> List[float]:
    if not values:
        return values
    vmin, vmax = min(values), max(values)
    if vmax == vmin:
        return [1.0 for _ in values]
    return [(v - vmin) / (vmax - vmin) for v in values]

async def hybrid_retrieve(
    engine: AsyncEngine,
    query_embedding: List[float],
    query_text: str,
    top_k_semantic: int = 2,
    top_k_lexical: int = 2,
    top_k_final: int = 3,
    alpha: float = 0.6,
    min_semantic: Optional[float] = None,
    course_id: Optional[int] = None,
    doc_types: Optional[List[str]] = None,
    lang: Optional[str] = None,
    ts_config: str = "simple",
) -> List[HybridRetrieved]:
    """
    Hybrid retrieval using updated rag_docs schema.
    """
    sem = await semantic_retrieve(
        engine,
        query_embedding=query_embedding,
        top_k=top_k_semantic,
        min_score=min_semantic,
        course_id=course_id,
        doc_types=doc_types,
        lang=lang,
    )
    
    lex = await lexical_retrieve(
        engine,
        query_text=query_text,
        top_k=top_k_lexical,
        config=ts_config,
        course_id=course_id,
        doc_types=doc_types,
        lang=lang,
    )

    print(f"[hybrid_retrieve] got {len(sem)} semantic, {len(lex)} lexical")

    sem_scores = _minmax_norm([x.score for x in sem]) or []
    lex_scores = _minmax_norm([x.score for x in lex]) or []

    sem_by_id: Dict[int, tuple] = {x.id: (x, sem_scores[i] if sem_scores else 0.0) for i, x in enumerate(sem)}
    lex_by_id: Dict[int, tuple] = {x.id: (x, lex_scores[i] if lex_scores else 0.0) for i, x in enumerate(lex)}

    union_ids = set(sem_by_id) | set(lex_by_id)
    fused: List[HybridRetrieved] = []

    for _id in union_ids:
        s_obj, s_norm = sem_by_id.get(_id, (None, 0.0))
        l_obj, l_norm = lex_by_id.get(_id, (None, 0.0))
        base = s_obj or l_obj
        if base is None:
            continue
        score_final = alpha * s_norm + (1 - alpha) * l_norm
        fused.append(
            HybridRetrieved(
                id=base.id,
                course_id=base.course_id,
                doc_type=base.doc_type,
                lang=base.lang,
                content=(base.text if hasattr(base, "text") else getattr(base, "content", "")),
                score_semantic=float(s_obj.score) if s_obj else 0.0,
                score_lexical=float(l_obj.score) if l_obj else 0.0,
                score_final=score_final,
                metadata=base.meta if hasattr(base, "meta") else getattr(base, "metadata", {}),
            )
        )

    fused.sort(key=lambda x: x.score_final, reverse=True)
    return fused[:top_k_final]