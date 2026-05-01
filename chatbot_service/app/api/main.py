from __future__ import annotations

import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from .schemas import AskDTO, AskResponse

from app.rag.chain import RAGPipeline, GenerativeConfig
from app.rag.chain import build_engine

app = FastAPI(title="RAG Chatbot (LangChain + Qwen)", version="0.1.0")

origins = [
    "https://xpervia.vercel.app",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup():
    # Cấu hình mô hình sinh văn bản mặc định, tạo pipeline và giữ trong state
    gen_cfg = GenerativeConfig()
    print("[startup - cfg] Pipeline initialized")
    eng = build_engine()
    print("[startup - engine] Engine initialized")
    app.state.pipeline = RAGPipeline(gen_cfg, engine=eng, return_chunks=True)
    print("[startup - pipeline] RAG Pipeline initialized")

@app.get("/health")
async def health():
    ok = hasattr(app.state, "pipeline")
    return {"status": "ok" if ok else "not_ready"}

@app.post("/ask", response_model=AskResponse)
async def ask(dto: AskDTO) -> AskResponse:
    if not getattr(app.state, "pipeline", None):
        raise HTTPException(status_code=503, detail="Pipeline chưa sẵn sàng")

    try:
        out = await app.state.pipeline.ainvoke(
            dto.question,
            history=[h.model_dump() for h in dto.history] if dto.history else None,
            system_prompt=dto.system_prompt,
            use_simple_prompt=dto.use_simple_prompt,
        )
        # out là dict: {"answer": ..., "retrieved_chunks": ...?}
        resp = AskResponse(answer=out["answer"])
        if dto.return_chunks and "retrieved_chunks" in out:
            resp.retrieved_chunks = out["retrieved_chunks"]
        return resp

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Generation error: {e}")
