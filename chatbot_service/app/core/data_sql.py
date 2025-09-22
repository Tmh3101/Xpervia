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