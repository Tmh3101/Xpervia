from __future__ import annotations

import hashlib
import tiktoken
from app import config
from typing import Any, Dict, List, Optional
from datetime import datetime, timezone
from langchain_core.documents import Document
from sqlalchemy import (
    Table, Column, BigInteger, Integer, Text,
    String, JSON, DateTime, MetaData
)
from sqlalchemy.ext.asyncio import AsyncEngine
from pgvector.sqlalchemy import Vector
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy import delete

metadata = MetaData(schema="public") # sử dụng schema public
rag_chunks = Table(
    "rag_chunks",
    metadata,
    Column("id", BigInteger, primary_key=True, autoincrement=True),
    Column("chunk_uid", String(64), nullable=False, unique=True), # sha256 stable key, kết hợp course_id, doc_type, chunk_index, title, sha16(content)
    Column("course_id", BigInteger, nullable=True), # khoá học gốc (nếu có)
    Column("doc_type", String(64), nullable=False), # loại document: course_overview, pricing, popularity
    Column("lang", String(8), nullable=False, default="vi"), # ngôn ngữ của content
    Column("content", Text, nullable=False), # nội dung text đã render
    Column("content_tokens", Integer, nullable=True), # số token ước lượng trong content
    Column("embedding", Vector(config.EMBED_DIM), nullable=False), # vector nhúng
    Column("metadata", JSON, nullable=False, server_default="{}"), # metadata gốc (course_id, doc_type, title, chunk_index, total_chunks, ...)
    Column("created_at", DateTime(timezone=True), nullable=False), # thời điểm tạo bản ghi
    Column("updated_at", DateTime(timezone=True), nullable=False), # thời điểm cập nhật bản ghi
)

def _utcnow():
    return datetime.now(timezone.utc)

def _chunk_uid(course_id: Optional[int], doc_type: str, content: str, metadata: Dict[str, Any]) -> str:
    """
    Tạo khoá ổn định cho từng chunk:
    sha256(f"{course_id}|{doc_type}|{chunk_index}|{title}|sha16(content)}")
    """
    idx = str(metadata.get("chunk_index", ""))
    title = str(metadata.get("title", ""))
    h_content = hashlib.sha256(content.encode("utf-8")).hexdigest()[:16]
    raw = f"{course_id}|{doc_type}|{idx}|{title}|{h_content}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()

def _count_tokens_approx(s: str) -> int:
    if not s:
        return 0
    
    try:
        enc = tiktoken.get_encoding("cl100k_base")
        return len(enc.encode(s))
    except Exception:
        import re
        return max(1, len(re.findall(r"\w+|[^\w\s]", s)))

async def save_chunks_with_embeddings(
    engine: AsyncEngine,
    chunks: List[Document],
    embs: List[List[float]],
    *,
    default_lang: str = "vi",
    compute_tokens: bool = True,
    batch_size: int = 500,
) -> int:
    if not chunks:
        return 0
    
    if len(chunks) != len(embs):
        raise ValueError(f"Length mismatch: chunks={len(chunks)} vs embs={len(embs)}")

    total = 0
    now = _utcnow()
    records = []

    # đóng gói bản ghi
    for doc, vec in zip(chunks, embs):
        md: Dict[str, Any] = dict(doc.metadata or {})
        course_id = md.get("course_id")
        doc_type = md.get("doc_type", "course_overview")
        lang = md.get("lang", default_lang)
        content = doc.page_content or ""
        tokens = _count_tokens_approx(content) if compute_tokens else None

        uid = _chunk_uid(course_id, doc_type, content, md)
        records.append({
            "chunk_uid": uid,
            "course_id": course_id,
            "doc_type": doc_type,
            "lang": lang,
            "content": content,
            "content_tokens": tokens,
            "embedding": vec,
            "metadata": md,
            "created_at": now,
            "updated_at": now,
        })

    # chèn theo lô
    for i in range(0, len(records), batch_size):
        batch = records[i:i+batch_size]
        stmt = insert(rag_chunks).values(batch)   # chỉ INSERT, không on_conflict
        async with engine.begin() as conn:
            await conn.execute(stmt)
        total += len(batch)

    return total

async def upsert_chunks(engine: AsyncEngine, rows: List[Dict[str, Any]], batch_size: int = 500) -> int:
    if not rows:
        return 0

    now = _utcnow()
    prepared = []
    for r in rows:
        md = dict(r.get("metadata") or {})
        uid = _chunk_uid(r.get("course_id"), r.get("doc_type"), r.get("content"), md)
        prepared.append({
            "chunk_uid": uid,
            "course_id": r.get("course_id"),
            "doc_type": r.get("doc_type"),
            "lang": r.get("lang", "vi"),
            "content": r.get("content"),
            "content_tokens": r.get("content_tokens"),
            "embedding": r.get("embedding"),
            "metadata": md,
            "created_at": now,
            "updated_at": now,
        })

    total = 0
    for i in range(0, len(prepared), batch_size):
        batch = prepared[i:i+batch_size]
        stmt = insert(rag_chunks).values(batch)
        stmt = stmt.on_conflict_do_update(
            index_elements=["chunk_uid"],
            set_={
                "course_id": stmt.excluded.course_id,
                "doc_type": stmt.excluded.doc_type,
                "lang": stmt.excluded.lang,
                "content": stmt.excluded.content,
                "content_tokens": stmt.excluded.content_tokens,
                "embedding": stmt.excluded.embedding,
                "metadata": stmt.excluded.metadata,
                "updated_at": stmt.excluded.updated_at,
            },
        )
        async with engine.begin() as conn:
            res = await conn.execute(stmt)
        total += len(batch)
    return total


async def delete_by_course(engine: AsyncEngine, course_id: int) -> int:
    """Xoá tất cả chunks của một khoá học (để reindex sạch)."""
    async with engine.begin() as conn:
        res = await conn.execute(delete(rag_chunks).where(rag_chunks.c.course_id == course_id))
        return res.rowcount or 0

async def delete_by_doc_type(engine: AsyncEngine, doc_type: str) -> int:
    """Xoá tất cả chunks của một loại document (để reindex sạch)."""
    async with engine.begin() as conn:
        res = await conn.execute(delete(rag_chunks).where(rag_chunks.c.doc_type == doc_type))
        return res.rowcount or 0