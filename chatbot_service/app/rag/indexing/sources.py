from __future__ import annotations
from typing import Optional, Sequence, Dict, Any, List
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncEngine
from sqlalchemy import text
from langchain_core.document_loaders import BaseLoader
from langchain_core.documents import Document
from app.rag.indexing import normalize

def _to_utc(dt: Optional[datetime]) -> Optional[datetime]:
    if dt is None: return None
    return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)

# SQL để load course_overview đã ENRICHED
COURSE_OVERVIEW_ENRICHED_SQL = """
with base as (
  select
    cc.id  as course_content_id,
    c.id   as course_id,
    cc.title,
    cc.description,
    (u.first_name || ' ' || u.last_name) as teacher_name,
    u.id   as teacher_id,
    array_remove(array_agg(distinct cat.name), null) as categories,
    c.price,
    coalesce(c.discount, 0)::float as discount,
    (c.price * (1 - coalesce(c.discount,0)))::int as price_final,
    c.is_visible,
    c.start_date,
    c.regis_start_date,
    c.regis_end_date,
    c.max_students,
    coalesce(enr_cnt.count_enroll, 0) as enrollments_count,
    coalesce(fav_cnt.count_fav, 0) as favorites_count,
    cc.thumbnail_url,
    cc.thumbnail_path,
    greatest(c.created_at, u.updated_at) as updated_at
  from public.course_contents cc
  join public.courses c on c.course_content_id = cc.id
  join public.users u on u.id = cc.teacher_id
  left join public.course_contents_categories ccg on ccg.coursecontent_id = cc.id
  left join public.categories cat on cat.id = ccg.category_id
  left join (
    select course_id, count(*) as count_enroll
    from public.enrollments group by course_id
  ) enr_cnt on enr_cnt.course_id = c.id
  left join (
    select course_id, count(*) as count_fav
    from public.favorites group by course_id
  ) fav_cnt on fav_cnt.course_id = c.id
  where c.is_visible = true
  group by cc.id, c.id, u.id, cc.title, cc.description, c.price, c.discount,
           c.is_visible, c.start_date, c.regis_start_date, c.regis_end_date,
           c.max_students, enr_cnt.count_enroll, fav_cnt.count_fav,
           cc.thumbnail_url, cc.thumbnail_path, c.created_at, u.updated_at
),
chapters_list as (
  select
    ch.course_content_id,
    json_agg(
      json_build_object(
        'chapter_id', ch.id,
        'chapter_title', ch.title,
        'order', ch."order"
      )
      order by ch."order"
    ) as chapters_json
  from public.chapters ch
  group by ch.course_content_id
),
lessons_visible as (
  select
    l.course_content_id,
    l.id as lesson_id,
    l.title as lesson_title,
    l."order" as order,
    l.chapter_id
  from public.lessons l
  where l.is_visible = true
),
chapter_lessons as (
  select
    ch.course_content_id,
    ch.id as chapter_id,
    json_agg(
      json_build_object(
        'lesson_id', lv.lesson_id,
        'lesson_title', lv.lesson_title,
        'order', lv.order
      )
      order by lv.order
    ) as lessons_json
  from public.chapters ch
  join lessons_visible lv
    on lv.course_content_id = ch.course_content_id
   and lv.chapter_id = ch.id
  group by ch.course_content_id, ch.id
),
chapters_enriched as (
  select
    b.course_content_id,
    json_agg(
      json_build_object(
        'chapter_id', (c_item->>'chapter_id')::bigint,
        'chapter_title', c_item->>'chapter_title',
        'order', (c_item->>'order')::int,
        'lessons',
          coalesce(
            (
              select cl.lessons_json
              from chapter_lessons cl
              where cl.course_content_id = b.course_content_id
                and cl.chapter_id = (c_item->>'chapter_id')::bigint
            ),
            '[]'::json
          )
      )
      order by (c_item->>'order')::int
    ) as chapters_full
  from base b
  left join chapters_list chlist on chlist.course_content_id = b.course_content_id
  left join lateral json_array_elements(coalesce(chlist.chapters_json, '[]'::json)) as c_item on true
  group by b.course_content_id
),
unassigned_lessons as (
  select
    lv.course_content_id,
    json_agg(
      json_build_object(
        'lesson_id', lv.lesson_id,
        'lesson_title', lv.lesson_title,
        'order', lv.order
      )
      order by lv.order
    ) as lessons_no_chapter
  from lessons_visible lv
  where lv.chapter_id is null
  group by lv.course_content_id
)
select
  b.*,
  coalesce(ce.chapters_full, '[]'::json) as chapters_full,
  coalesce(ul.lessons_no_chapter, '[]'::json) as lessons_no_chapter
from base b
left join chapters_enriched ce on ce.course_content_id = b.course_content_id
left join unassigned_lessons ul on ul.course_content_id = b.course_content_id
order by b.course_id;
"""

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

                # Chuẩn bị các trường
                title=r.get("title") or ""
                teacher_name=r.get("teacher_name") or ""
                categories=r.get("categories") or []
                description=r.get("description") or ""
                price=int(r.get("price") or 0)
                discount=float(r.get("discount") or 0.0)
                price_final=price * (1 - discount) if discount > 0 else price
                start_date=str(r.get("start_date") or "") or None
                regis_start_date=str(r.get("regis_start_date") or "") or None
                regis_end_date=str(r.get("regis_end_date") or "") or None
                max_students=r.get("max_students")
                enrollments_count=int(r.get("enrollments_count") or 0)
                favorites_count=int(r.get("favorites_count") or 0)
                chapters_full: List[Dict[str, Any]] = r.get("chapters_full") or []
                lessons_no_chapter: List[Dict[str, Any]] = r.get("lessons_no_chapter") or []

                # Tính số chương/bài học
                chapters_count = len(chapters_full)
                lessons_count = sum(len(ch.get("lessons") or []) for ch in chapters_full) + len(lessons_no_chapter)

                # Render thành nội dung text
                text_body = normalize.render_course_overview(
                    title=title,
                    teacher_name=teacher_name,
                    categories=categories,
                    description=description,
                    price=price,
                    discount=discount,
                    price_final=price_final,
                    start_date=start_date,
                    regis_start_date=regis_start_date,
                    regis_end_date=regis_end_date,
                    max_students=max_students,
                    enrollments_count=enrollments_count,
                    favorites_count=favorites_count,
                    chapters=chapters_full,
                    lessons_no_chapter=lessons_no_chapter,
                    chapters_count=chapters_count,
                    lessons_count=lessons_count,
                )

                # Tạo Document metadata
                metadata = {
                    "doc_type": "course_overview",
                    "course_id": int(r["course_id"]),
                    "course_content_id": int(r["course_content_id"]),
                    "title": r.get("title"),
                    "teacher_name": r.get("teacher_name"),
                    "categories": r.get("categories") or [],
                    "chapters_count": chapters_count,
                    "lessons_count": lessons_count,
                }

                yield Document(page_content=text_body, metadata=metadata)
