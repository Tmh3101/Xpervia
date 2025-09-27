import sys
import asyncio
from pathlib import Path
from sqlalchemy.ext.asyncio import create_async_engine

sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from app import config
from app.rag.indexing.sources import SQLCourseOverviewEnrichedLoader
from app.rag.indexing.upsert import save_chunks_with_embeddings

async def main():
    engine = create_async_engine(config.DATABASE_URL_ASYNC, pool_pre_ping=True)
    loader = SQLCourseOverviewEnrichedLoader(engine, since=None, course_ids=None)

    count = 0
    max_len = 0
    docs = []
    async for doc in loader.alazy_load():
        count += 1
        max_len = max(max_len, len(doc.page_content))
        docs.append(doc)

    saved = await save_chunks_with_embeddings(engine, docs)
    print(f"Loaded {count} documents, saved {saved} chunks with embeddings.")

    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(main())