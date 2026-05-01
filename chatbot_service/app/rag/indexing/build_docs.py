from typing import List, Dict, Optional
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.core.schemas import (
    Courses, CourseContents, Users, Categories, Chapters, Lessons, CourseContentsCategories
)

def fetch_course_block(session: Session, course_id: int):
    """
    Lấy block dữ liệu thô cần thiết cho 1 course_id (theo bảng Courses.id),
    nhưng liên kết sang CourseContents/Chapters/Lessons/Categories.
    """
    # 1) Lấy Courses + CourseContents + Teacher
    c_alias = session.execute(
        select(
            Courses.id.label("course_id"),
            Courses.price, Courses.discount, Courses.is_visible,
            Courses.start_date, Courses.regis_start_date, Courses.regis_end_date, Courses.max_students,
            CourseContents.id.label("course_content_id"),
            CourseContents.title, CourseContents.description,
            Users.first_name, Users.last_name
        )
        .join(CourseContents, CourseContents.id == Courses.course_content_id)
        .join(Users, Users.id == CourseContents.teacher_id)
        .where(Courses.id == course_id)
    ).mappings().first()

    if not c_alias:
        return None

    # 2) Categories (qua CourseContents)
    cat_rows = session.execute(
        select(Categories.name)
        .select_from(Courses)
        .join(CourseContents, CourseContents.id == Courses.course_content_id)
        .join(CourseContentsCategories, CourseContentsCategories.coursecontent_id == CourseContents.id, isouter=True)
        .join(Categories, Categories.id == CourseContentsCategories.category_id, isouter=True)
        .where(Courses.id == course_id)
    ).all()
    categories = [r[0] for r in cat_rows if r[0]]

    # 3) Chapters của CourseContents
    chap_rows = session.execute(
        select(Chapters.id, Chapters.title, Chapters.order)
        .where(Chapters.course_content_id == c_alias["course_content_id"])
        .order_by(Chapters.order.asc(), Chapters.id.asc())
    ).all()
    chapters = [{"id": cid, "title": ttl, "order": ordn} for (cid, ttl, ordn) in chap_rows]

    # 4) Lessons thuộc CourseContents này (có/không có chapter)
    les_rows = session.execute(
        select(
            Lessons.id,
            Lessons.title,
            Lessons.chapter_id,
            Lessons.order,
            Lessons.is_visible
        )
        .where(Lessons.course_content_id == c_alias["course_content_id"])
        .order_by(
            Lessons.chapter_id.asc().nullsfirst(),
            Lessons.order.asc(),
            Lessons.id.asc()
        )
    ).all()
    lessons = [
        {"id": lid, "title": ltitle, "chapter_id": ch, "order": ordn, "is_visible": vis}
        for (lid, ltitle, ch, ordn, vis) in les_rows
    ]

    return {
        "course": c_alias,
        "categories": categories,
        "chapters": chapters,
        "lessons": lessons
    }

def build_document_text(block: dict) -> tuple[str, dict]:
    """Tạo document text + meta giàu ngữ cảnh đúng định dạng bạn yêu cầu."""
    c = block["course"]
    categories = block["categories"]
    chapters = block["chapters"]
    lessons = block["lessons"]

    teacher_name = f'{(c["first_name"] or "").strip()} {(c["last_name"] or "").strip()}'.strip()
    cats = ", ".join(categories) if categories else "(trống)"

    # Map lessons theo chapter_id
    by_chapter: Dict[Optional[int], List[dict]] = {}
    for ls in lessons:
        by_chapter.setdefault(ls["chapter_id"], []).append(ls)

    # Bài học không thuộc chương
    orphan_lessons = by_chapter.get(None, [])

    # Header khóa học
    header_lines = [
        f"Tiêu đề: {c['title']}",
        f"Mô tả: {c['description']}",
        f"Danh mục: {cats}",
        f"Giảng viên: {teacher_name}",
        f"Học phí:" + f"{c['price'] if c['price'] is not None else 'Miễn phí'}"
                    +  (f", Giảm {c['discount']*100:.0f}% còn {c['price']*(1-c['discount']):.0f}" if c['discount'] and c['price'] else ""),
        "",
        f"Số chương: {len(chapters)}",
        f"Số bài học: {len(lessons)}",
    ]

    # Liệt kê Chương & Bài học
    section_lines = []
    if chapters:
        section_lines.append("Tổng quan cấu trúc:")
        for ch in chapters:
            l_in = by_chapter.get(ch["id"], [])
            section_lines.append(
                f"- Chương {ch['order']}. {ch['title']} gồm các bài học: {', '.join([ls['title'] for ls in l_in]) if l_in else '(không có bài học nào)'}"
            )

    # Bài học không thuộc chương nào
    if orphan_lessons:
        section_lines.append(f"- Bài học không thuộc chương nào gồm: {', '.join([ls['title'] for ls in orphan_lessons])}")

    # Gộp text + cleanup
    text = "\n".join([*header_lines, "", *section_lines]).strip()
    text = " ".join(text.split())

    # meta gọn gàng
    meta = {
        "title": c["title"],
        "categories": categories,
        "teacher": teacher_name,
        "price": c["price"],
        "discount": c["discount"],
        "num_chapters": len(chapters),
        "num_lessons": len(lessons),
        "chapters": [{"id": ch["id"], "title": ch["title"], "order": ch["order"]} for ch in chapters],
        "lessons": [{"id": str(l["id"]), "title": l["title"], "order": l["order"]} for l in lessons + orphan_lessons],
    }
    return text, meta
