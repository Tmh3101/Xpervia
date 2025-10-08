from __future__ import annotations
"""
FastAPI entrypoint for Xpervia Chatbot (RAG) — ready for Colab or server.

Usage (local/Colab):
  uvicorn app.api.main:app --host 0.0.0.0 --port 8000 --workers 1

Environment:
  - DATABASE_URL_ASYNC  (postgresql+asyncpg://...)
  - API_KEY             (optional; if set, requests must include X-API-Key header)

Endpoints:
  - GET  /health
  - POST /v1/chat               -> run one RAG turn (stores history in memory)
  - POST /v1/history/clear      -> clear history for a session

Notes:
  - This file reuses the orchestration in app.rag.chain
  - For production, replace in-memory history with Redis/DB in chain.py

"""

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

import os
import uvicorn
from contextlib import asynccontextmanager
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, Depends, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

from app import config
from app.rag.chain import chat_once, RetrievalParams, _HISTORY
from app.rag.generation.model import build_chat_model

print("Config loaded. DATABASE_URL_ASYNC:", config.DATABASE_URL_ASYNC)


API_KEY_ENV = os.getenv("API_KEY", "")


async def require_auth(x_api_key: Optional[str] = Header(default=None)) -> None:
    """Simple header auth. If API_KEY is not set, auth is disabled."""
    if not API_KEY_ENV:
        return
    if not x_api_key or x_api_key != API_KEY_ENV:
        raise HTTPException(status_code=401, detail="Unauthorized")


class ChatRequest(BaseModel):
    session_id: str = Field(..., description="Session ID để lưu history")
    question: str
    strategy: str = Field("hybrid", pattern="^(semantic|lexical|hybrid)$")
    top_k: int = Field(8, ge=1, le=50)
    top_k_semantic: int = Field(12, ge=1, le=100)
    top_k_lexical: int = Field(20, ge=1, le=100)
    alpha: float = Field(0.6, ge=0.0, le=1.0, description="Trọng số semantic khi fuse trong hybrid")
    course_id: Optional[int] = None
    doc_types: Optional[List[str]] = None
    lang: Optional[str] = None
    ts_config: str = Field("simple", description="Postgres text search config: simple/english/... ")


class ChatResponse(BaseModel):
    answer: str
    chunks: List[Dict[str, Any]]
    history: List[List[str]]


class ClearHistoryRequest(BaseModel):
    session_id: str


# Lifespan: manage DB engine
engine: AsyncEngine | None = None


@asynccontextmanager
async def lifespan(_: FastAPI):
    global engine
    engine = create_async_engine(config.DATABASE_URL_ASYNC, pool_pre_ping=True)
    try:
        yield
    finally:
        if engine:
            await engine.dispose()

# FastAPI app
app = FastAPI(title="Xpervia Chatbot API (RAG)", version="1.0", lifespan=lifespan)

# CORS (allow all by default; tighten in production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check API - simple GET to verify service is up and running
@app.get("/health")
async def health() -> Dict[str, Any]:
    return {"ok": True}

# Chat API - main RAG endpoint
@app.post("/v1/chat", response_model=ChatResponse)
async def chat_route(payload: ChatRequest, _: None = Depends(require_auth)) -> ChatResponse:
    if engine is None:
        raise HTTPException(status_code=500, detail="Engine not initialized")

    params = RetrievalParams(
        strategy=payload.strategy,
        top_k=payload.top_k,
        top_k_semantic=payload.top_k_semantic,
        top_k_lexical=payload.top_k_lexical,
        alpha=payload.alpha,
        course_id=payload.course_id,
        doc_types=payload.doc_types,
        lang=payload.lang,
        ts_config=payload.ts_config,
    )

    result = await chat_once(
        session_id=payload.session_id,
        question=payload.question,
        engine=engine,
        retrieval=params,
        chat=chat,  # pre-built ChatHuggingFace model
    )
    return ChatResponse(**result)

# Clear history API - clear in-memory history for a session
@app.post("/v1/history/clear")
async def clear_history(payload: ClearHistoryRequest, _: None = Depends(require_auth)) -> Dict[str, Any]:
    _HISTORY.pop(payload.session_id, None)
    return {"ok": True, "session_id": payload.session_id}

# Pre-build a ChatHuggingFace model to speed up first request
chat = build_chat_model()

# For local testing - run at url: http://localhost:8000
if __name__ == "__main__":
    print(f"Loaded model: {config.LLM_MODEL}")
    print("Starting server at http://localhost:8000")
    uvicorn.run("app.api.main:app", host="localhost", port=8000, reload=False)
    print("Server stopped")
