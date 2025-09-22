from __future__ import annotations
from typing import List
from langchain_core.documents import Document
from langchain_text_splitters import TokenTextSplitter

from app import config

def _make_token_splitter() -> TokenTextSplitter:
    return TokenTextSplitter(
        encoding_name="cl100k_base", # encoding_name giúp cho việc đếm token chính xác hơn 
        chunk_size=config.CHUNK_SIZE,
        chunk_overlap=config.CHUNK_OVERLAP
    )

def chunk_documents(docs: List[Document]) -> List[Document]:
    """
    Parameters
    ----------
    docs : List[Document]
        Các Document đã được loader/normalize tạo ra.
        metadata nên có tối thiểu: {'doc_type': str, 'course_id': int}

    Returns
    -------
    List[Document]
        Danh sách Document đã được chia nhỏ, mang đầy đủ metadata.
    """
    if not docs:
        return []

    splitter = _make_token_splitter()

    out: List[Document] = []
    for d in docs:
        parts = splitter.split_documents([d])
        total = len(parts)
        for idx, p in enumerate(parts):
            md = dict(d.metadata or {})
            md.update({"chunk_index": idx, "total_chunks": total})
            out.append(Document(page_content=p.page_content, metadata=md))
    return out

def chunk_course_overview(docs: List[Document]) -> List[Document]:
    cov = [d for d in docs if (d.metadata or {}).get("doc_type") == "course_overview"]
    return chunk_documents(cov)
