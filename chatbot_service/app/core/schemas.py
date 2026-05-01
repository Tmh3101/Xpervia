from datetime import datetime
from typing import List, Optional
from sqlalchemy.dialects.postgresql import JSONB
from pgvector.sqlalchemy import Vector
from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db import Base

class Users(Base):
    __tablename__ = "users"
    id: Mapped[str] = mapped_column(primary_key=True)
    email: Mapped[Optional[str]]
    first_name: Mapped[str]
    last_name: Mapped[str]

class Categories(Base):
    __tablename__ = "categories"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    description: Mapped[Optional[str]]

class CourseContents(Base):
    __tablename__ = "course_contents"
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str]
    description: Mapped[Optional[str]]
    thumbnail_path: Mapped[str]
    thumbnail_url: Mapped[Optional[str]]
    teacher_id: Mapped[str] = mapped_column(ForeignKey("users.id"))

    teacher: Mapped[Users] = relationship("Users")

class Courses(Base):
    __tablename__ = "courses"
    id: Mapped[int] = mapped_column(primary_key=True)
    course_content_id: Mapped[int] = mapped_column(ForeignKey("course_contents.id"))
    price: Mapped[Optional[int]]
    discount: Mapped[Optional[float]]
    is_visible: Mapped[bool]
    created_at: Mapped[datetime]
    start_date: Mapped[datetime]
    regis_start_date: Mapped[datetime]
    regis_end_date: Mapped[datetime]
    max_students: Mapped[Optional[int]]

    course_content: Mapped[CourseContents] = relationship("CourseContents")

class CourseContentsCategories(Base):
    __tablename__ = "course_contents_categories"
    coursecontent_id: Mapped[int] = mapped_column(ForeignKey("course_contents.id"), primary_key=True)
    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id"), primary_key=True)

class Chapters(Base):
    __tablename__ = "chapters"
    id: Mapped[int] = mapped_column(primary_key=True)
    course_content_id: Mapped[int] = mapped_column(ForeignKey("course_contents.id"))
    title: Mapped[str]
    order: Mapped[int]
    created_at: Mapped[datetime]

class Lessons(Base):
    __tablename__ = "lessons"
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str]
    content: Mapped[Optional[str]]
    video_id: Mapped[str]
    subtitle_vi_id: Mapped[Optional[str]]
    attachment_id: Mapped[Optional[str]]
    course_content_id: Mapped[int] = mapped_column(ForeignKey("course_contents.id"))
    chapter_id: Mapped[Optional[int]] = mapped_column(ForeignKey("chapters.id"))
    is_visible: Mapped[bool]
    order: Mapped[int]
    created_at: Mapped[datetime]

# Bảng vector
class RagDocs(Base):
    __tablename__ = "rag_docs"
    id: Mapped[int] = mapped_column(primary_key=True)
    course_id: Mapped[int]
    doc_type: Mapped[str]
    lang: Mapped[Optional[str]]
    text: Mapped[str]
    embedding: Mapped[List[float]] = mapped_column(Vector(768))
    meta: Mapped[dict] = mapped_column("meta", JSONB) 
    checksum: Mapped[str]
    updated_at: Mapped[datetime]

    __table_args__ = (UniqueConstraint("course_id", "doc_type", name="uq_rag_course_doctype"),)