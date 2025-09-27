import sys
import asyncio
from pathlib import Path
from sqlalchemy.ext.asyncio import create_async_engine

sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from app import config
from app.rag.embedding.embedder import embed_query
from app.rag.retrieval.search.lexical_retrieval import lexical_retrieve
from app.rag.retrieval.search.semantic_retrieval import semantic_retrieve
from app.rag.retrieval.hybrid_retrieval import hybrid_retrieve

async def main():
    engine = create_async_engine(config.DATABASE_URL_ASYNC, pool_pre_ping=True)

    query_text = "Lập trình"
    query_emb = embed_query(query_text)

    print(f"===== lexical_retrieval =====")
    lex = await lexical_retrieve(engine, query_text=query_text, top_k=5)
    for c in lex:
        print(c.metadata["title"])
        print()
    
    print(f"===== semantic_retrieval =====")
    sem = await semantic_retrieve(engine, query_embedding=query_emb, top_k=5)
    for c in sem:
        print(c.metadata["title"])
        print()

    print(f"===== hybrid_retrieval =====")
    hybrid = await hybrid_retrieve(engine, query_embedding=query_emb, query_text=query_text)
    for c in hybrid:
        print(c.metadata["title"])
        print()

    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(main())