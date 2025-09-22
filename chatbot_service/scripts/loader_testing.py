import sys
import asyncio
from pathlib import Path
from sqlalchemy.ext.asyncio import create_async_engine

sys.path.append(str(Path(__file__).resolve().parent.parent))

from app import config
from app.rag.indexing.sources import SQLCourseOverviewEnrichedLoader

async def main():
    engine = create_async_engine(config.DATABASE_URL_ASYNC, pool_pre_ping=True)
    loader = SQLCourseOverviewEnrichedLoader(engine, since=None, course_ids=None)

    count = 0
    max_len = 0
    async for doc in loader.alazy_load():
        count += 1
        print(f"#{count}", doc.metadata.get("doc_type"), doc.metadata.get("course_id"))
        print(doc.page_content, "\n")
        max_len = max(max_len, len(doc.page_content))

    print(f"Total documents: {count}, Max length: {max_len}")
    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(main())