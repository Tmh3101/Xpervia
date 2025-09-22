from __future__ import annotations
from typing import Optional, Sequence, Dict, Any
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncEngine
from langchain_core.document_loaders import BaseLoader
from langchain_core.documents import Document
from sqlalchemy import text

from app.rag.indexing import normalize
from app.core.schemas import CourseOverviewMetadata, CourseOverview
from app.core.data_sql import COURSE_OVERVIEW_ENRICHED_SQL

def _to_utc(dt: Optional[datetime]) -> Optional[datetime]:
    if dt is None: return None
    return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)

class SQLCourseOverviewEnrichedLoader(BaseLoader):
    def __init__(self, engine: AsyncEngine, since: Optional[datetime]=None, course_ids: Optional[Sequence[int]]=None):
        self.engine = engine
        self.since = _to_utc(since)
        self.course_ids = list(course_ids) if course_ids else None

    async def alazy_load(self):
        async with self.engine.connect() as conn:
            res = await conn.execute(
                text(COURSE_OVERVIEW_ENRICHED_SQL),
                {"since": self.since, "filter_course_ids": self.course_ids}
            )
            for row in res.mappings():
                r: Dict[str, Any] = dict(row)

                chapters_count = len(r.get("chapters_full") or [])
                lessons_count = sum(len(ch.get("lessons") or []) for ch in r.get("chapters_full")) + len(r.get("lessons_no_chapter"))

                course_overview_data = CourseOverview(
                    title=r.get("title") or "",
                    teacher_name=r.get("teacher_name") or "",
                    categories=r.get("categories") or [],
                    description=r.get("description") or "",
                    price=int(r.get("price") or 0),
                    discount=float(r.get("discount") or 0.0),
                    price_final=int(r.get("price_final") or 0),
                    start_date=str(r.get("start_date") or "") or None,
                    regis_start_date=str(r.get("regis_start_date") or "") or None,
                    regis_end_date=str(r.get("regis_end_date") or "") or None,
                    max_students=r.get("max_students"),
                    enrollments_count=int(r.get("enrollments_count") or 0),
                    favorites_count=int(r.get("favorites_count") or 0),
                    chapters_count=chapters_count,
                    lessons_count=lessons_count,
                    chapters=r.get("chapters_json") or [],
                    lessons_no_chapter=r.get("lessons_no_chapter") or [],
                )

                # Render thành nội dung text
                text_body = normalize.render_course_overview(course_overview_data)

                metadata = CourseOverviewMetadata(
                    doc_type="course_overview",
                    course_id=int(r["course_id"]),
                    course_content_id=int(r["course_content_id"]),
                    title=r.get("title"),
                    teacher_name=r.get("teacher_name"),
                    categories=r.get("categories") or [],
                    chapters_count=chapters_count,
                    lessons_count=lessons_count,
                )

                yield Document(page_content=text_body, metadata=metadata.model_dump())
