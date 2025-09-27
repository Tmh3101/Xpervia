import sys
import asyncio
from pathlib import Path
from sqlalchemy.ext.asyncio import create_async_engine

sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from app import config
from app.rag.indexing.sources import SQLCourseOverviewEnrichedLoader
from app.rag.indexing.chunker import chunk_documents

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

    print(f"Total documents: {count}, Max length: {max_len}")

    chunked_docs = chunk_documents(docs)
    print(f"Total chunked documents: {len(chunked_docs)}")

    for i, doc in enumerate(chunked_docs):
        print(f"Chunk {i+1}: {doc.page_content}")
        print()

    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(main())