from __future__ import annotations

import sys
import argparse
import asyncio
from pathlib import Path
from datetime import datetime
from typing import Optional, Sequence, List
from langchain_core.documents import Document
from sqlalchemy.ext.asyncio import create_async_engine

sys.path.append(str(Path(__file__).resolve().parent.parent))

from app import config
from app.rag.indexing.sources import SQLCourseOverviewEnrichedLoader
from app.rag.indexing.chunker import chunk_documents
from app.rag.indexing.embedder import embed_documents
from app.rag.indexing.upsert import save_chunks_with_embeddings

def _parse_args():
    p = argparse.ArgumentParser(description="Preview course_overview chunks from DB.")
    p.add_argument("--since", help="ISO datetime filter for incremental (e.g. 2025-09-01T00:00:00Z)", default=None)
    p.add_argument("--course-ids", help="Comma-separated course_id(s) to include", default=None)
    p.add_argument("--no-token", action="store_true", help="Use Recursive splitter instead of token-based")
    p.add_argument("--limit", type=int, default=9999, help="Max documents to preview (after load, before chunk)")
    return p.parse_args()

def _parse_since(s: Optional[str]) -> Optional[datetime]:
    if not s:
        return None
    # very loose parse: expect ISO-like "YYYY-MM-DDTHH:MM:SSZ" or "YYYY-MM-DD"
    try:
        if "T" in s:
            s = s.replace("Z", "+00:00")
            return datetime.fromisoformat(s)
        return datetime.fromisoformat(s + "T00:00:00+00:00")
    except Exception:
        raise SystemExit(f"Invalid --since value: {s}")

def _parse_ids(s: Optional[str]) -> Optional[Sequence[int]]:
    if not s:
        return None
    try:
        return [int(x.strip()) for x in s.split(",") if x.strip()]
    except Exception:
        raise SystemExit(f"Invalid --course-ids value: {s}")

async def main():
    args = _parse_args()
    since = _parse_since(args.since)
    course_ids = _parse_ids(args.course_ids)
    engine = create_async_engine(config.DATABASE_URL_ASYNC, pool_pre_ping=True)

    print(f"CHUNK_SIZE={config.CHUNK_SIZE}, CHUNK_OVERLAP={config.CHUNK_OVERLAP}")

    # Load course_overview (đã enrich chương/bài lẻ)
    loader = SQLCourseOverviewEnrichedLoader(engine, since=since, course_ids=course_ids)
    docs: List[Document] = []
    async for d in loader.alazy_load():
        docs.append(d)
        if len(docs) >= args.limit:
            break

    if not docs:
        print("No documents found with given filters.")
        await engine.dispose()
        return

    # Chunking and embedding
    prefer_token = not args.no_token
    chunks = chunk_documents(docs, prefer_token=prefer_token)
    embs = embed_documents(chunks)

    # Save to DB
    n = await save_chunks_with_embeddings(engine, chunks, embs, compute_tokens=prefer_token)
    print(f"Saved {n} chunks with embeddings into DB.")

    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(main())
