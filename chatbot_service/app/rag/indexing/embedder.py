from __future__ import annotations
from typing import List
from langchain_core.documents import Document
from sentence_transformers import SentenceTransformer
from app import config

def get_embeddings_model() -> SentenceTransformer:
    return SentenceTransformer(config.EMBEDDING_MODEL, trust_remote_code=True)

def embed_documents(docs: List[Document]) -> List[List[float]]:
    """Trả về vectors theo cùng thứ tự docs."""
    if not docs:
        return []
    
    page_contents = [d.page_content for d in docs if d.page_content.strip()]
    if not page_contents:
        return [[] for _ in docs]  # trả về danh sách rỗng tương ứng

    model = get_embeddings_model()
    embs = model.encode(page_contents, normalize_embeddings=True)
    return embs

def embed_query(q: str) -> List[float]:
    return get_embeddings_model().embed_query(q)
