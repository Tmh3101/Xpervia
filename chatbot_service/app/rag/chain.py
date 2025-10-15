from __future__ import annotations

import asyncio
from typing import Any, Dict, List, Optional, TypedDict
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine
from langchain_core.runnables import RunnableLambda, RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

from app.rag.generative.model import build_chat_model, GenerativeConfig
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
    return create_async_engine(config.DATABASE_URL_ASYNC, pool_pre_ping=True)

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
        chat = None
        print("[CHAIN] IS_COLAB_LLM=True -> skipping local model build (chat=None).")
    else:
        chat = build_chat_model(chat_model_config)
        print("[CHAIN] Local chat model built at startup.")

    def _do_embed(inp: ChainInput) -> Dict[str, Any]:
        question = inp["question"]
        print("[EMBEDDING] Embedding question:", question)

        emb_res = embed_query(question)
        return {
            "question": question,
            "query_emb": emb_res,
            "query_text": question,
            "history": inp.get("history"),
            "system_prompt": inp.get("system_prompt"),
            "use_simple_prompt": inp.get("use_simple_prompt", False)
        }

    async def _do_retrieve(ctx: Dict[str, Any]) -> Dict[str, Any]:
        chunks = await hybrid_retrieve(
            eng,
            query_embedding=ctx["query_emb"],
            query_text=ctx["query_text"],
        )
        ctx["retrieved_chunks"] = chunks
        print(f"[RETRIEVED] Retrieved {len(chunks)} chunks")
        return ctx

    async def _do_generate(ctx: Dict[str, Any]) -> ChainOutput:
        ans = generate_answer(
            chat=chat,
            question=ctx["question"],
            retrieved_chunks=ctx["retrieved_chunks"],
            history=ctx.get("history"),
            system_prompt=ctx.get("system_prompt"),
            use_simple_prompt=ctx.get("use_simple_prompt", False),
            chat_model_config=chat_model_config,
        )

        out: ChainOutput = {"answer": ans}
        if return_chunks:
            out["retrieved_chunks"] = ctx["retrieved_chunks"]  # type: ignore
        return out

    # 5) ---- Lắp pipeline bằng LCEL ----
    # Mẹo: Dùng RunnablePassthrough để giữ nguyên payload, hoặc RunnableParallel để chia nhánh song song nếu cần.
    identity = RunnablePassthrough()
    chain = (
        identity
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

    async def ainvoke(self, question: str, *, history: Optional[List[ChatTurn]] = None,
                      system_prompt: Optional[str] = None, use_simple_prompt: bool = False) -> ChainOutput:
        payload: ChainInput = {
            "question": question,
            "history": history,
            "system_prompt": system_prompt,
            "use_simple_prompt": use_simple_prompt,
        }
        return await self.chain.ainvoke(payload)

    def invoke(self, question: str, *, history: Optional[List[ChatTurn]] = None,
               system_prompt: Optional[str] = None, use_simple_prompt: bool = False) -> ChainOutput:
        return asyncio.run(self.ainvoke(question, history=history, system_prompt=system_prompt, use_simple_prompt=use_simple_prompt))
