SQL_COURSE_BASE_ALL = """
select
  c.id as course_id,
  cc.id as course_content_id,
  cc.title,
  coalesce(cc.description, '') as description,
  u.first_name, u.last_name,
  array_remove(array_agg(distinct cat.name), null) as categories,
  c.price, c.discount, c.is_visible,
  c.start_date, c.regis_start_date, c.regis_end_date, c.max_students
from courses c
join coursecontents cc on cc.id = c.course_content_id
left join users u on u.id = cc.teacher_id
left join courses_categories ccg on ccg.course_id = cc.id
left join categories cat on cat.id = ccg.category_id
group by c.id, cc.id, cc.title, cc.description, u.first_name, u.last_name,
         c.price, c.discount, c.is_visible, c.start_date, c.regis_start_date, c.regis_end_date, c.max_students
order by c.id;
"""

SQL_COURSE_BASE_ONE = """
select
  c.id as course_id,
  cc.id as course_content_id,
  cc.title,
  coalesce(cc.description, '') as description,
  u.first_name, u.last_name,
  array_remove(array_agg(distinct cat.name), null) as categories,
  c.price, c.discount, c.is_visible,
  c.start_date, c.regis_start_date, c.regis_end_date, c.max_students
from courses c
join coursecontents cc on cc.id = c.course_content_id
left join users u on u.id = cc.teacher_id
left join courses_categories ccg on ccg.course_id = cc.id
left join categories cat on cat.id = ccg.category_id
where c.id = %s
group by c.id, cc.id, cc.title, cc.description, u.first_name, u.last_name,
         c.price, c.discount, c.is_visible, c.start_date, c.regis_start_date, c.regis_end_date, c.max_students
"""

SQL_STRUCTURE = """
select
  coalesce(
    (
      select json_agg(
        json_build_object(
          'id', ch.id,
          'title', ch.title,
          'order', ch.order,
          'lessons', (
            select coalesce(
              json_agg(
                json_build_object(
                  'id', l.id,
                  'title', l.title,
                  'order', l.order,
                  'is_visible', l.is_visible
                )
                order by l.order, l.id
              ),
              '[]'::json
            )
            from lessons l
            where l.chapter_id = ch.id
          )
        )
        order by ch.order, ch.id
      ),
      '[]'::json
    ) as chapters,
  coalesce(
    (
      select json_agg(
        json_build_object(
          'id', l.id,
          'title', l.title,
          'order', l.order,
          'is_visible', l.is_visible
        )
        order by l.order, l.id
      )
      from lessons l
      where l.course_id = %s and l.chapter_id is null
    ),
    '[]'::json
  ) as lessons_without_chapter
from coursecontents cc
where cc.id = %s;
"""

UPSERT_SQL = """
insert into rag_docs (course_id, doc_type, lang, text, embedding, meta, checksum, updated_at)
values (%s, %s, %s, %s, %s::vector, %s::jsonb, %s, now())
on conflict (course_id, doc_type)
do update set
  lang = excluded.lang,
  text = excluded.text,
  embedding = excluded.embedding,
  meta = excluded.meta,
  checksum = excluded.checksum,
  updated_at = now()
where rag_docs.checksum <> excluded.checksum;
"""

SELECT_CHECKSUM_SQL = """
select checksum from rag_docs
where course_id = %s and doc_type = 'course_overview'
"""