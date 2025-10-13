import asyncio
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

from app.rag.chain import RAGPipeline, GenerativeConfig

QUESTION = "Sau khi hoành thành khóa học Xây dựng RESTful API với Java Spring Boot tôi sẽ nhận được các kỹ năng gì?"

async def main():
    pipe = RAGPipeline(
        GenerativeConfig(),
        return_chunks=True,  # tiện in ra để debug
    )

    out = await pipe.ainvoke(
        QUESTION,
        history=[{"role": "human", "content": "Xin chào"}],
        system_prompt="Bạn luôn bám sát context.",
        use_simple_prompt=False,
    )

    print("\n=== ANSWER ===\n", out["answer"])
    if "retrieved_chunks" in out:
        print("\n=== CHUNKS (top) ===")
        out["retrieved_chunks"]

if __name__ == "__main__":
    asyncio.run(main())
