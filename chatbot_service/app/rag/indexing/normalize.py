from __future__ import annotations
import re
import html
import unicodedata
from typing import Iterable, Any, Optional

from app.core.schemas import CourseOverview

_HTML_TAG_RE = re.compile(r"<[^>]+>")
_MULTI_NL_RE = re.compile(r"\n{3,}")
_MULTI_SPACE_RE = re.compile(r"[ \t]{2,}")

def _to_text(value: Any) -> str:
    if value is None:
        return ""
    return str(value)

def _strip_html(s: str) -> str:
    s = html.unescape(s or "")
    s = re.sub(r"</(p|div|section|br|li|ul|ol|h[1-6])\s*>", "\n", s, flags=re.IGNORECASE)
    s = _HTML_TAG_RE.sub("", s)
    return s

def _normalize_unicode(s: str) -> str:
    return unicodedata.normalize("NFC", s or "")

def _collapse_ws(s: str) -> str:
    if not s:
        return ""
    
    s = _MULTI_NL_RE.sub("\n\n", s)
    s = _MULTI_SPACE_RE.sub(" ", s)
    lines = [ln.strip() for ln in s.splitlines()]
    s = "\n".join(ln for ln in lines if ln is not None)
    return s.strip()

def _clean(s: str) -> str:
    return _collapse_ws(_normalize_unicode(_strip_html(_to_text(s))))

def _csv(items: Iterable[Any]) -> str:
    safe = [i for i in (items or []) if i not in (None, "", [])]
    return ", ".join(map(str, safe))

def _fmt_percent(frac: Optional[float]) -> str:
    try:
        if frac is None:
            return "0%"
        return f"{round(float(frac) * 100):d}%"
    except Exception:
        return "0%"

def _fmt_int(n: Optional[int]) -> str:
    try:
        return f"{int(n):,}".replace(",", ".") 
    except Exception:
        return "0"

def _fmt_money_vn(n: Optional[int]) -> str:
    return _fmt_int(n)

def _fmt_date_iso(d: Optional[str]) -> str:
    """
    Đầu vào mong muốn: ISO string hoặc None.
    Trả về dạng YYYY-MM-DD (nếu parse đơn giản được) hoặc giữ nguyên.
    """
    if not d:
        return ""
    if "T" in d:
        d = d.split("T", 1)[0]
    return d

def render_course_overview(course_overview: CourseOverview) -> str:
    chapters = course_overview.chapters or []
    lessons_no_chapter = course_overview.lessons_no_chapter or []
    title = _clean(course_overview.title)
    teacher = _clean(course_overview.teacher_name)
    cats = _csv(course_overview.categories)
    desc = _clean(course_overview.description)
    price_s = _fmt_money_vn(course_overview.price)
    discount_s = _fmt_percent(course_overview.discount)
    price_final_s = _fmt_money_vn(course_overview.price_final)
    start_s = _fmt_date_iso(course_overview.start_date)
    regis_s = f"{_fmt_date_iso(course_overview.regis_start_date)} → {_fmt_date_iso(course_overview.regis_end_date)}".strip(" → ")
    max_stu_s = "Không giới hạn" if (course_overview.max_students is None) else _fmt_int(course_overview.max_students)
    enroll_s = _fmt_int(course_overview.enrollments_count)
    fav_s = _fmt_int(course_overview.favorites_count)
    ch_count = course_overview.chapters_count
    ls_count = course_overview.lessons_count

    parts = [
        f"[Khóa học] {title}",
        f"[Giảng viên] {teacher}" if teacher else "",
        f"[Thể loại] {cats}" if cats else "",
        f"[Mô tả] {desc if desc else '(Chưa có mô tả chi tiết)'}",
        f"[Giá] {price_s}  [Giảm] {discount_s}  [Giá sau giảm] {price_final_s}",
        f"[Khai giảng] {start_s}" if start_s else "",
        f"[Đăng ký] {regis_s}" if regis_s else "",
        f"[Chỉ tiêu] {max_stu_s}",
        f"[Phổ biến] Số học viên: {enroll_s}, Yêu thích: {fav_s}",
        f"[Syllabus] Số chương: {ch_count}, Số bài học: {ls_count}",
    ]

    # Danh sách chương + bài học trong từng chương
    if len(chapters) > 0:
        parts.append("[Danh sách chương]")
        for ch in chapters:
            ch_title = _clean(ch.get("chapter_title") or "")
            ch_order = ch.get("order")
            parts.append(f"  - Chương {ch_order}: {ch_title}")
            lessons = ch.get("lessons") or []
            if lessons:
                for ls in lessons:
                    lt = _clean(ls.get("lesson_title") or "")
                    lo = ls.get("order")
                    parts.append(f"      • Bài {lo}: {lt}")

    # Bài học không thuộc chương nào
    if len(lessons_no_chapter) > 0:
        parts.append("[Bài học không thuộc chương nào]")
        for ls in lessons_no_chapter:
            lt = _clean(ls.get("lesson_title") or "")
            lo = ls.get("order")
            parts.append(f"  • Bài {lo}: {lt}")

    return _collapse_ws("\n".join(p for p in parts if p != ""))