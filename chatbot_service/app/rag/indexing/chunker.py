from __future__ import annotations
from typing import List
from langchain_core.documents import Document
from langchain_text_splitters import TokenTextSplitter, RecursiveCharacterTextSplitter
from app import config

def _make_token_splitter() -> TokenTextSplitter:
    """
    Chunk theo token dùng tiktoken (nếu có).
    - encoding_name='cl100k_base' là lựa chọn phổ biến, đủ ổn định để ước lượng token.
    """
    return TokenTextSplitter(
        encoding_name="cl100k_base",
        chunk_size=config.CHUNK_SIZE,
        chunk_overlap=config.CHUNK_OVERLAP,
    )

def _make_recursive_splitter() -> RecursiveCharacterTextSplitter:
    """
    Fallback khi môi trường không có tiktoken hoặc bạn muốn chia theo ký tự.
    Bộ phân tách: đoạn trống → dòng → câu → từ.
    """
    return RecursiveCharacterTextSplitter(
        separators=["\n\n", "\n", ". ", " "],
        chunk_size=config.CHUNK_SIZE,
        chunk_overlap=config.CHUNK_OVERLAP,
    )


def chunk_documents(docs: List[Document], prefer_token: bool = True) -> List[Document]:
    """
    Chunk danh sách Document (course_overview / pricing / popularity).
    - Giữ nguyên metadata gốc (doc_type, course_id, ...).
    - Bổ sung 'chunk_index' và 'total_chunks' vào metadata của từng chunk.

    Parameters
    ----------
    docs : List[Document]
        Các Document đã được loader/normalize tạo ra.
        metadata nên có tối thiểu: {'doc_type': str, 'course_id': int}
    prefer_token : bool
        True -> dùng TokenTextSplitter, False -> dùng RecursiveCharacterTextSplitter.

    Returns
    -------
    List[Document]
        Danh sách Document đã được chia nhỏ, mang đầy đủ metadata.
    """
    if not docs:
        return []

    splitter = _make_token_splitter() if prefer_token else _make_recursive_splitter()

    out: List[Document] = []
    for d in docs:
        parts = splitter.split_documents([d])  # trả về list[Document]
        total = len(parts)
        # gắn chunk_index/total_chunks
        for idx, p in enumerate(parts):
            md = dict(d.metadata or {})
            md.update({"chunk_index": idx, "total_chunks": total})
            out.append(Document(page_content=p.page_content, metadata=md))
    return out

def chunk_course_overview(docs: List[Document], prefer_token: bool = True) -> List[Document]:
    """Chỉ chunk các Document có metadata['doc_type'] == 'course_overview'."""
    cov = [d for d in docs if (d.metadata or {}).get("doc_type") == "course_overview"]
    return chunk_documents(cov, prefer_token=prefer_token)

def chunk_pricing(docs: List[Document], prefer_token: bool = True) -> List[Document]:
    """Chỉ chunk các Document có metadata['doc_type'] == 'pricing_schedule'."""
    pr = [d for d in docs if (d.metadata or {}).get("doc_type") == "pricing_schedule"]
    return chunk_documents(pr, prefer_token=prefer_token)

def chunk_popularity(docs: List[Document], prefer_token: bool = True) -> List[Document]:
    """Chỉ chunk các Document có metadata['doc_type'] == 'popularity_signals'."""
    pp = [d for d in docs if (d.metadata or {}).get("doc_type") == "popularity_signals"]
    return chunk_documents(pp, prefer_token=prefer_token)
