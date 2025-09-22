from app import config
from sqlalchemy import (
    Table, Column, BigInteger, Integer, Text,
    String, JSON, DateTime, MetaData
)
from pgvector.sqlalchemy import Vector
from pydantic import BaseModel
from typing import Any, Dict, List, Optional

metadata = MetaData(schema="public") # sử dụng schema public
rag_chunks = Table(
    "rag_chunks",
    metadata,
    Column("id", BigInteger, primary_key=True, autoincrement=True),
    Column("chunk_uid", String(64), nullable=False, unique=True), # sha256 stable key, kết hợp course_id, doc_type, chunk_index, title, sha16(content)
    Column("course_id", BigInteger, nullable=True), # khoá học gốc (nếu có)
    Column("doc_type", String(64), nullable=False), # loại document: course_overview, pricing, popularity
    Column("lang", String(8), nullable=False, default="vi"), # ngôn ngữ của content
    Column("content", Text, nullable=False), # nội dung text đã render
    Column("content_tokens", Integer, nullable=True), # số token ước lượng trong content
    Column("embedding", Vector(config.EMBED_DIM), nullable=False), # vector nhúng
    Column("metadata", JSON, nullable=False, server_default="{}"), # metadata gốc (course_id, doc_type, title, chunk_index, total_chunks, ...)
    Column("created_at", DateTime(timezone=True), nullable=False), # thời điểm tạo bản ghi
    Column("updated_at", DateTime(timezone=True), nullable=False), # thời điểm cập nhật bản ghi
)

# 
class CourseOverviewMetadata(BaseModel):
    doc_type: str
    course_id: Optional[int]
    course_content_id: Optional[int]
    title: Optional[str] = None
    teacher_name: Optional[str] = None
    categories: Optional[List[str]] = None
    chapters_count: Optional[int] = None
    lessons_count: Optional[int] = None
    chunk_index: Optional[int] = None
    total_chunks: Optional[int] = None

class CourseOverview(BaseModel):
    title: str
    teacher_name: str
    categories: List[str]
    description: str
    price: int
    discount: float
    price_final: int
    start_date: Optional[str] = None
    regis_start_date: Optional[str] = None
    regis_end_date: Optional[str] = None
    max_students: Optional[int] = None
    enrollments_count: int
    favorites_count: int
    chapters_count: Optional[int] = None
    lessons_count: Optional[int] = None
    chapters: Optional[List[Dict[str, Any]]] = []
    lessons_no_chapter: Optional[List[Dict[str, Any]]] = []