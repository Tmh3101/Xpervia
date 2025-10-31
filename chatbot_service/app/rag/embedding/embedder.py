from __future__ import annotations

import requests
from typing import List
from sentence_transformers import SentenceTransformer
from app import config

def _call_colab_embedding(text: str) -> List[float]:
    """
    Gọi dịch vụ embedding từ Colab LLM.
    """
    url = config.COLAB_LLM_URL + "/embed"
    payload = {"text": text}
    headers = {"Content-Type": "application/json"}

    response = requests.post(url, json=payload, headers=headers)
    response.raise_for_status()
    data = response.json()
    return data["vector"]


def get_embeddings_model() -> SentenceTransformer:
    return SentenceTransformer(config.EMBEDDING_MODEL, trust_remote_code=True)

def embed_docs(docs: List[str]) -> List[List[float]]:
    model = get_embeddings_model()
    embs = []
    if config.IS_COLAB_LLM:
        for doc in docs:
            emb = _call_colab_embedding(doc)
            embs.append(emb)
        return embs
    return model.encode(
        docs,
        batch_size=64,
        convert_to_numpy=True,
        normalize_embeddings=True,
        show_progress_bar=True
    )

def embed_query(q: str) -> List[float]:
    if config.IS_COLAB_LLM:
        print("Using Colab LLM for embedding.")
        return _call_colab_embedding(q)
    
    print('Fallback to local embedding model.')
    model = get_embeddings_model()
    return model.encode(q, normalize_embeddings=True)

