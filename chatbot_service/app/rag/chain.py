from __future__ import annotations

import asyncio
import os
from typing import Any, Dict, List, Optional, TypedDict
from sqlalchemy.exc import InvalidRequestError
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine
from langchain_core.runnables import RunnableLambda, RunnablePassthrough

from app.rag.hyde.hypothetical import generate_hypothetical
from app.core.model.model import GenerativeConfig, load_model_and_tokenizer, build_chat_model
from app.rag.embedding.embedder import embed_query
from app.rag.retrieval.hybrid_retrieval import hybrid_retrieve
from app.rag.generative.answer_generation import generate_answer
from app import config

class ChatTurn(TypedDict, total=False):
    role: str
    content: str

class ChainInput(TypedDict, total=False):
    question: str
    history: Optional[List[ChatTurn]]
    system_prompt: Optional[str]
    use_simple_prompt: bool

class ChainOutput(TypedDict, total=False):
    answer: str

def build_engine() -> AsyncEngine:
    """
    Create AsyncEngine using config.DATABASE_URL_ASYNC

    Ensures:
      - URL uses asyncpg (postgresql+asyncpg://)
      - asyncpg is importable
    """
    url = getattr(config, "DATABASE_URL_ASYNC", None) or os.getenv("DATABASE_URL_ASYNC") or os.getenv("DATABASE_URL")
    if not url:
        raise RuntimeError("DATABASE URL not set. Please set DATABASE_URL_ASYNC or DATABASE_URL env var.")

    if url.startswith("postgresql://") and "+asyncpg" not in url:
        url = url.replace("postgresql://", "postgresql+asyncpg://", 1)

    try:
        # check async driver available
        import asyncpg  # noqa: F401
    except Exception as e:
        raise RuntimeError("asyncpg not installed. Please `pip install asyncpg`. Import error: " + str(e))

    try:
        engine = create_async_engine(url, pool_pre_ping=True)
        return engine
    except InvalidRequestError as e:
        raise RuntimeError(
            "Failed to create async engine. Make sure DATABASE URL uses asyncpg (postgresql+asyncpg://) "
            "and asyncpg is installed. Original: " + str(e)
        )
    except Exception as e:
        raise RuntimeError("Unable to create async engine: " + str(e))


def make_rag_chain(
    engine: Optional[AsyncEngine],
    chat_model_config: GenerativeConfig,
    return_chunks: bool = False
):
    """
    Tạo một LCEL chain. Chain nhận `ChainInput` và trả về `ChainOutput`.
    """
    eng = engine or build_engine()

    if getattr(config, "IS_COLAB_LLM", False):
        chat, tokenizer, model = None, None, None
        print("[CHAIN] IS_COLAB_LLM=True -> skipping local model build (chat=None).")
    else:
        chat = build_chat_model(chat_model_config)
        print("[CHAIN] Local chat model built at startup.")

    # def _do_hypothetical(inp: ChainInput) -> str:
    #     print('[CHAIN] Doing hypothetical')
    #     hyde_res = generate_hypothetical(
    #         query=inp["question"]
    #     )
    #     print("[HYPOTHETICAL] Generated hypothetical answer.")
    #     return {
    #         "question": inp["question"],
    #         "hypo_draft": hyde_res["draft"],
    #         "history": inp.get("history"),
    #         "system_prompt": inp.get("system_prompt"),
    #         "use_simple_prompt": inp.get("use_simple_prompt", False)
    #     }

    # def _do_embed(ctx: Dict[str, Any]) -> Dict[str, Any]:
    #     emb_res = embed_query(ctx["hypo_draft"])
    #     print("[EMBEDDING] Embedding question:", ctx["hypo_draft"])
    #     ctx["hypo_emb"] = emb_res
    #     return ctx

    # async def _do_retrieve(ctx: Dict[str, Any]) -> Dict[str, Any]:
    #     # hybrid_retrieve is now async
    #     chunks = await hybrid_retrieve(
    #         eng,
    #         query_embedding=ctx["hypo_emb"],
    #         query_text=ctx["hypo_draft"],
    #     )
    #     ctx["retrieved_chunks"] = chunks
    #     print(f"[RETRIEVED] Retrieved {len(chunks)} chunks")
    #     return ctx

    def _do_embed(inp: ChainInput) -> Dict[str, Any]:
        emb_res = embed_query(inp["question"])
        print("[EMBEDDING] Embedding question:", inp["question"])
        inp["question_emb"] = emb_res
        return inp
    
    async def _do_retrieve(ctx: Dict[str, Any]) -> Dict[str, Any]:
        # hybrid_retrieve is now async
        chunks = await hybrid_retrieve(
            eng,
            query_embedding=ctx["question_emb"],
            query_text=ctx["question"],
        )
        ctx["retrieved_chunks"] = chunks
        print(f"[RETRIEVED] Retrieved {len(chunks)} chunks")
        return ctx

    def _do_generate(ctx: Dict[str, Any]) -> Dict[str, Any]:
        ans = generate_answer(
            chat=chat,
            question=ctx["question"],
            retrieved_chunks=ctx["retrieved_chunks"],
            history=ctx.get("history"),
            system_prompt=ctx.get("system_prompt"),
            use_simple_prompt=ctx.get("use_simple_prompt", False),
            chat_model_config=chat_model_config,
        )

        print("[GENERATE] Generated answer:", ans)

        # generate_answer used to return a plain string but now may return a dict
        # with shape {"answer": str, "resources": [ids...]}. Normalize here
        # so downstream (and API Pydantic models) always receive a string for
        # the `answer` field.
        out: Dict[str, Any] = {}
        if isinstance(ans, dict):
            out["answer"] = ans.get("answer", "")
            # pass resources through if provided (frontend can consume it)
            if "resources" in ans:
                out["resources"] = ans.get("resources", [])
        else:
            out["answer"] = str(ans or "")
        if return_chunks:
            out["retrieved_chunks"] = ctx["retrieved_chunks"]
        return out

    # 5) ---- Lắp pipeline bằng LCEL ----
    # Mẹo: Dùng RunnablePassthrough để giữ nguyên payload, hoặc RunnableParallel để chia nhánh song song nếu cần.
    identity = RunnablePassthrough()
    chain = (
        identity
        # | RunnableLambda(_do_hypothetical)
        | RunnableLambda(_do_embed)
        | RunnableLambda(_do_retrieve)
        | RunnableLambda(_do_generate)
        #     | StrOutputParser() # chuẩn hoá về string nếu bạn muốn — ở đây ta trả JSON-like -> giữ nguyên
    )
    return chain

class RAGPipeline:
    def __init__(self, chat_model_config: GenerativeConfig, engine: Optional[AsyncEngine] = None, return_chunks: bool = False):
        self.engine = engine or build_engine()
        self.chain = make_rag_chain(self.engine, chat_model_config, return_chunks=return_chunks)

    async def ainvoke(self, question: str, *, history: Optional[List[dict]] = None,
                      system_prompt: Optional[str] = None, use_simple_prompt: bool = False) -> Dict[str, Any]:
        payload = {
            "question": question,
            "history": history,
            "system_prompt": system_prompt,
            "use_simple_prompt": use_simple_prompt,
        }
        return await self.chain.ainvoke(payload)

    def invoke(self, question: str, *, history: Optional[List[dict]] = None,
               system_prompt: Optional[str] = None, use_simple_prompt: bool = False) -> Dict[str, Any]:
        return asyncio.run(self.ainvoke(question, history=history, system_prompt=system_prompt, use_simple_prompt=use_simple_prompt))
