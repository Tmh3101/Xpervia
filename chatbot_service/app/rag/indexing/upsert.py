from __future__ import annotations

import hashlib
import tiktoken
from typing import Any, Dict, List, Optional
from datetime import datetime, timezone
from langchain_core.documents import Document
from sqlalchemy.ext.asyncio import AsyncEngine
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy import delete

from app.core.schemas import rag_chunks
from app.rag.embedding.embedder import embed_documents
from app.rag.indexing.chunker import chunk_documents

def _utcnow():
    return datetime.now(timezone.utc)

# Tạo khoá ổn định cho từng chunk: sha256(f"{course_id}|{doc_type}|{chunk_index}|{title}|sha16(content)}")
def _generate_chunk_uid(course_id: Optional[int], doc_type: str, content: str, metadata: Dict[str, Any]) -> str:
    idx = str(metadata.get("chunk_index", ""))
    title = str(metadata.get("title", ""))
    h_content = hashlib.sha256(content.encode("utf-8")).hexdigest()[:16]
    raw = f"{course_id}|{doc_type}|{idx}|{title}|{h_content}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()

# Ước lượng số token trong content (không chính xác tuyệt đối, nhưng nhanh)
def _count_tokens_approx(s: str) -> int:
    if not s:
        return 0
    
    try:
        enc = tiktoken.get_encoding("cl100k_base")
        return len(enc.encode(s))
    except Exception:
        import re
        return max(1, len(re.findall(r"\w+|[^\w\s]", s)))

# Lưu các chunks đã có embedding vào CSDL
async def save_chunks_with_embeddings(
    engine: AsyncEngine,
    docs: List[Document],
    default_lang: str = "vi",
    compute_tokens: bool = True,
    batch_size: int = 500,
) -> int:
    if not docs:
        return 0
    
    # Tạo chunks
    chunks = chunk_documents(docs)
    print(f"Chunked {len(docs)} documents into {len(chunks)} chunks.")
    if not chunks:
        return 0
    
    # Tạo embedding
    embs = embed_documents(chunks)
    print(f"Embedded {len(chunks)} chunks into vectors.")
    
    if len(chunks) != len(embs):
        raise ValueError(f"Length mismatch: chunks={len(chunks)} vs embs={len(embs)}")

    total = 0
    now = _utcnow()
    records = []

    print(f"Preparing {len(chunks)} records to upsert into rag_chunks table...")

    # đóng gói bản ghi
    for doc, vec in zip(chunks, embs):
        print(f"Processing chunk: {doc.metadata.get('title')}")
        md: Dict[str, Any] = dict(doc.metadata or {})
        course_id = md.get("course_id")
        doc_type = md.get("doc_type", "course_overview")
        content = doc.page_content or ""

        uid = _generate_chunk_uid(course_id, doc_type, content, md)
        records.append({
            "chunk_uid": uid,
            "chunk_index": md.get("chunk_index"),
            "total_chunks": md.get("total_chunks"),
            "course_id": md.get("course_id"),
            "doc_type": md.get("doc_type", "course_overview"),
            "lang": md.get("lang", default_lang),
            "content": content,
            "content_tokens": _count_tokens_approx(content) if compute_tokens else None,
            "embedding": vec,
            "metadata": md,
            "created_at": now,
            "updated_at": now,
        })

    print(f"Prepared {len(records)} records to upsert into rag_chunks table.")

    # chèn theo lô - tránh chèn quá nhiều một lần
    for i in range(0, len(records), batch_size):
        batch = records[i:i+batch_size]
        stmt = insert(rag_chunks).values(batch) # Không dùng on_conflict_do_update vì đã có rồi thì thôi
        async with engine.begin() as conn:
            await conn.execute(stmt)
        total += len(batch)
    return total

# Upsert các chunks (khi đã có embedding) - dùng ON CONFLICT để tránh trùng lặp
async def upsert_chunks(engine: AsyncEngine, rows: List[Dict[str, Any]], batch_size: int = 500) -> int:
    if not rows:
        return 0

    # Chuẩn bị & format dữ liệu
    now = _utcnow()
    prepared = []
    for r in rows:
        md = dict(r.get("metadata") or {})
        uid = _generate_chunk_uid(r.get("course_id"), r.get("doc_type"), r.get("content"), md)
        prepared.append({
            "chunk_uid": uid,
            "chunk_index": md.get("chunk_index"),
            "total_chunks": md.get("total_chunks"),
            "course_id": md.get("course_id"),
            "doc_type": md.get("doc_type"),
            "lang": md.get("lang", "vi"),
            "content": md.get("content"),
            "content_tokens": md.get("content_tokens"),
            "embedding": r.get("embedding"),
            "metadata": md,
            "created_at": now,
            "updated_at": now,
        })

    # upsert theo lô - tránh upsert quá nhiều một lần
    total = 0
    for i in range(0, len(prepared), batch_size):
        batch = prepared[i:i+batch_size]
        stmt = insert(rag_chunks).values(batch)
        stmt = stmt.on_conflict_do_update(
            index_elements=["chunk_uid"],
            set_={
                "course_id": stmt.excluded.course_id,
                "chunk_index": stmt.excluded.chunk_index,
                "total_chunks": stmt.excluded.total_chunks,
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

# Xoá các chunks theo khoá học hoặc loại document
async def delete_by_course(engine: AsyncEngine, course_id: int) -> int:
    """Xoá tất cả chunks của một khoá học (để reindex sạch)."""
    async with engine.begin() as conn:
        res = await conn.execute(delete(rag_chunks).where(rag_chunks.c.course_id == course_id))
        return res.rowcount or 0

# Xoá các chunks theo loại document
async def delete_by_doc_type(engine: AsyncEngine, doc_type: str) -> int:
    """Xoá tất cả chunks của một loại document (để reindex sạch)."""
    async with engine.begin() as conn:
        res = await conn.execute(delete(rag_chunks).where(rag_chunks.c.doc_type == doc_type))
        return res.rowcount or 0