from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Literal, Optional
import asyncio
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine
from langchain.schema import BaseMessage, HumanMessage, AIMessage
from langchain_huggingface import ChatHuggingFace

from app import config
from app.rag.embedding.embedder import embed_query
from app.rag.retrieval.search.semantic_retrieval import semantic_retrieve
from app.rag.retrieval.search.lexical_retrieval import lexical_retrieve
from app.rag.retrieval.hybrid_retrieval import hybrid_retrieve
from app.rag.generation.generative import generate_answer


# History storage (in-memory demo). Swap with Redis/DB for production.
_HISTORY: Dict[str, List[BaseMessage]] = {}

# History helpers
def get_history(session_id: str) -> List[BaseMessage]:
    return _HISTORY.get(session_id, [])

# Append a human/AI turn to history
def append_history(session_id: str, human: str, ai: str) -> None:
    msgs = _HISTORY.setdefault(session_id, [])
    msgs.append(HumanMessage(content=human))
    msgs.append(AIMessage(content=ai))

# Config dataclass for retrieval parameters
@dataclass
class RetrievalParams:
    strategy: Literal["semantic", "lexical", "hybrid"] = "hybrid"
    top_k: int = 8  # final top_k for hybrid; for semantic/lexical it's the same
    # Hybrid-specific knobs
    top_k_semantic: int = 12
    top_k_lexical: int = 20
    alpha: float = 0.6  # weight for semantic score when fusing
    # Optional filters
    course_id: Optional[int] = None
    doc_types: Optional[List[str]] = None
    lang: Optional[str] = None
    ts_config: str = "simple"


# Retrieval module
async def retrieve_context(
    engine: AsyncEngine,
    query_text: str,
    query_embedding: List[float],
    params: RetrievalParams,
) -> List[Any]:
    if params.strategy == "semantic":
        chunks = await semantic_retrieve(
            engine,
            query_embedding=query_embedding,
            top_k=params.top_k,
            course_id=params.course_id,
            doc_types=params.doc_types,
            lang=params.lang,
        )
        return chunks

    if params.strategy == "lexical":
        chunks = await lexical_retrieve(
            engine,
            query_text=query_text,
            top_k=params.top_k,
            config=params.ts_config,
            course_id=params.course_id,
            doc_types=params.doc_types,
            lang=params.lang,
        )
        return chunks

    # Hybrid (default)
    chunks = await hybrid_retrieve(
        engine,
        query_embedding=query_embedding,
        query_text=query_text,
        top_k_semantic=params.top_k_semantic,
        top_k_lexical=params.top_k_lexical,
        top_k_final=params.top_k,
        alpha=params.alpha,
        course_id=params.course_id,
        doc_types=params.doc_types,
        lang=params.lang,
        ts_config=params.ts_config,
    )
    return chunks

# Main chat entrypoint
async def chat_once(
    session_id: str,
    question: str,
    engine: Optional[AsyncEngine] = None,
    retrieval: Optional[RetrievalParams] = None,
    chat: Optional[ChatHuggingFace] = None,
) -> Dict[str, Any]:
    """
    Run one full RAG turn:
      - Load history for session_id
      - Embed the query
      - Retrieve context (semantic/lexical/hybrid)
      - Generate final answer with Arcee-VyLinh
      - Persist history

    Returns a dict with: {"answer", "chunks", "history"}
    """
    # 1) Prepare
    retrieval = retrieval or RetrievalParams()
    engine_owned = False
    if engine is None:
        engine = create_async_engine(config.DATABASE_URL_ASYNC, pool_pre_ping=True)
        engine_owned = True

    try:
        # 2) Load history (LangChain messages)
        history_msgs = get_history(session_id)

        # 3) Embed the user question (ensure Python list of float)
        q_embed = embed_query(question)
        if hasattr(q_embed, "tolist"):
            q_embed = q_embed.tolist()

        # 4) Retrieve context
        chunks = await retrieve_context(
            engine,
            query_text=question,
            query_embedding=q_embed,
            params=retrieval,
        )

        # 5) Generate the final answer
        answer = generate_answer(
            chat=chat,  # build default ChatHuggingFace under the hood
            question=question,
            retrieved_chunks=chunks,
            history=history_msgs,
        )

        # 6) Persist history
        append_history(session_id, question, answer)

        # 7) Return payload
        # Convert history to serializable tuples for API layer
        serial_history = [(m.type, m.content) for m in get_history(session_id)]
        return {
            "answer": answer,
            "chunks": [
                {
                    "id": getattr(c, "id", None) or (c.get("id") if isinstance(c, dict) else None),
                    "chunk_uid": getattr(c, "chunk_uid", None) or (c.get("chunk_uid") if isinstance(c, dict) else None),
                    "doc_type": getattr(c, "doc_type", None) or (c.get("doc_type") if isinstance(c, dict) else None),
                    "score": getattr(c, "score_final", None)
                              or getattr(c, "score", None)
                              or (c.get("score") if isinstance(c, dict) else None),
                    "preview": (getattr(c, "content", "") or (c.get("content") if isinstance(c, dict) else ""))[:240],
                }
                for c in chunks
            ],
            "history": serial_history,
        }

    finally:
        if engine_owned:
            await engine.dispose()


# Convenience: tiny CLI for ad-hoc testing
async def _demo():
    resp = await chat_once(
        session_id="demo",
        question="Khóa học Python cơ bản gồm mấy chương và học những gì?",
        retrieval=RetrievalParams(strategy="hybrid", top_k=6),
    )
    print("\n=== ANSWER ===\n", resp["answer"])  # noqa: T201
    print("\n=== CHUNKS (preview) ===")  # noqa: T201
    for c in resp["chunks"]:
        print("-", c)  # noqa: T201


if __name__ == "__main__":
    asyncio.run(_demo())
