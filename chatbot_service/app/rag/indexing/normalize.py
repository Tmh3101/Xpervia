from __future__ import annotations
import html
import re
import unicodedata
from typing import Iterable, List, Dict, Any, Optional

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
    """Full pipeline clean for arbitrary HTML-ish text."""
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
        return f"{int(n):,}".replace(",", ".")  # 1.234.567 (VN style)
    except Exception:
        return "0"

def _fmt_money_vn(n: Optional[int]) -> str:
    # Chỉ định dạng số, đơn vị sẽ ghi bên ngoài nếu cần
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

# render document content for course_overview
def render_course_overview(
    *,
    title: str,
    teacher_name: str,
    categories: List[str],
    description: str,
    price: int,
    discount: float,
    price_final: int,
    start_date: Optional[str],
    regis_start_date: Optional[str],
    regis_end_date: Optional[str],
    max_students: Optional[int],
    enrollments_count: int,
    favorites_count: int,
    chapters: List[Dict[str, Any]] = None,
    lessons_no_chapter: List[Dict[str, Any]] = None,
    chapters_count: Optional[int] = None,
    lessons_count: Optional[int] = None,
) -> str:
    chapters = chapters or []
    lessons_no_chapter = lessons_no_chapter or []

    title = _clean(title)
    teacher = _clean(teacher_name)
    cats = _csv(categories)
    desc = _clean(description)

    price_s = _fmt_money_vn(price)
    discount_s = _fmt_percent(discount)
    price_final_s = _fmt_money_vn(price_final)

    start_s = _fmt_date_iso(start_date)
    regis_s = f"{_fmt_date_iso(regis_start_date)} → {_fmt_date_iso(regis_end_date)}".strip(" → ")

    max_stu_s = "Không giới hạn" if (max_students is None) else _fmt_int(max_students)
    enroll_s = _fmt_int(enrollments_count)
    fav_s = _fmt_int(favorites_count)

    # Tóm tắt syllabus
    ch_count = chapters_count if chapters_count is not None else len(chapters)
    ls_count_calc = sum(len(ch.get("lessons") or []) for ch in chapters) + len(lessons_no_chapter)
    ls_count = lessons_count if lessons_count is not None else ls_count_calc

    parts = [
        f"[Khóa học] {title}",
        f"[Giảng viên] {teacher}" if teacher else "",
        f"[Thể loại] {cats}" if cats else "",
        "[Mô tả]",
        desc or "(Chưa có mô tả chi tiết)",
        "",
        f"[Giá] {price_s}  [Giảm] {discount_s}  [Giá sau giảm] {price_final_s}",
        f"[Khai giảng] {start_s}" if start_s else "",
        f"[Đăng ký] {regis_s}" if regis_s else "",
        f"[Chỉ tiêu] {max_stu_s}",
        f"[Phổ biến] Enroll: {enroll_s}, Yêu thích: {fav_s}",
        "",
        f"[Syllabus] Số chương: {ch_count}, Số bài học: {ls_count}",
    ]

    # Danh sách chương + bài học trong từng chương
    if chapters[0].get("chapter_id") is not None:
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
    if lessons_no_chapter:
        parts.append("[Bài học không thuộc chương nào]")
        for ls in lessons_no_chapter:
            lt = _clean(ls.get("lesson_title") or "")
            lo = ls.get("order")
            parts.append(f"  • Bài {lo}: {lt}")

    return _collapse_ws("\n".join(p for p in parts if p != ""))

# render document content for pricing & schedule
def render_pricing_schedule(
    *,
    course_title: str,
    price: int,
    discount: float,
    price_final: int,
    start_date: Optional[str],
    regis_start_date: Optional[str],
    regis_end_date: Optional[str],
    max_students: Optional[int],
) -> str:
    """
    Tóm tắt riêng phần Giá & Lịch. Văn bản ngắn, rõ, dễ trích dẫn độc lập.
    """
    course_title = _clean(course_title)
    price_s = _fmt_money_vn(price)
    discount_s = _fmt_percent(discount)
    price_final_s = _fmt_money_vn(price_final)
    start_s = _fmt_date_iso(start_date)
    regis_s = f"{_fmt_date_iso(regis_start_date)} → {_fmt_date_iso(regis_end_date)}".strip(" → ")
    max_stu_s = "Không giới hạn" if (max_students is None) else _fmt_int(max_students)

    parts = [
        f"[Khóa học] {course_title}",
        f"[Giá hiện tại] {price_final_s} (Gốc {price_s}, Giảm {discount_s})",
        f"[Khai giảng] {start_s}" if start_s else "",
        f"[Đăng ký] {regis_s}" if regis_s else "",
        f"[Chỉ tiêu] {max_stu_s}",
    ]
    return _collapse_ws("\n".join(p for p in parts if p != ""))

# render document content for popularity signals
def render_popularity_signals(
    *,
    course_title: str,
    enrollments_count: int,
    favorites_count: int,
) -> str:
    """
    Tín hiệu phổ biến để tăng khả năng khớp ý định "khóa học hot/phổ biến".
    """
    course_title = _clean(course_title)
    enroll_s = _fmt_int(enrollments_count)
    fav_s = _fmt_int(favorites_count)

    parts = [
        f"[Khóa học] {course_title}",
        f"[Phổ biến] Số lượng học viên đã tham gia: {enroll_s}, Số lượng yêu thích: {fav_s}",
    ]
    return _collapse_ws("\n".join(p for p in parts if p != ""))
