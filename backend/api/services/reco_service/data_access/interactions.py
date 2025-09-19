from __future__ import annotations
from typing import Dict, List, Tuple, Literal
from datetime import datetime, timezone
from django.db import connection
from api.models import Enrollment, Favorite

EventType = Literal["enroll", "favorite"]

def _utc_now() -> datetime:
    return datetime.now(timezone.utc)

# Lấy các sự kiện (enroll, favorite) của user 
def fetch_user_events(user_id: str, limit: int = 50) -> List[Dict]:
    enrollments = Enrollment.objects.filter(student_id=user_id)
    favorites = Favorite.objects.filter(student_id=user_id)

    rows = []
    for e in enrollments:
        rows.append((e.course.course_content.id, 'enroll', e.created_at))

    for f in favorites:
        rows.append((f.course.course_content.id, 'favorite', f.created_at))

    now = _utc_now()
    out: List[Dict] = []
    for course_id, ev_type, ts in rows:
        # ts có thể là naive hoặc aware; chuẩn hóa về aware UTC nếu cần
        if isinstance(ts, datetime) and ts.tzinfo is None:
            ts = ts.replace(tzinfo=timezone.utc)
        delta_days = (now - ts).total_seconds() / 86400.0 if isinstance(ts, datetime) else 0.0
        out.append({
            "course_id": int(course_id),
            "type": ev_type,
            "timestamp": ts,
            "days_ago": float(max(0.0, delta_days)),
        })
    return out

# Lấy toàn bộ interactions để build CF ma trận R
def fetch_all_interactions() -> List[Tuple[str, int, EventType, datetime]]:
    enrollments = Enrollment.objects.all()
    favorites = Favorite.objects.all()

    rows = []
    for e in enrollments:
        rows.append((e.student.id, e.course.course_content.id, 'enroll', e.created_at))

    for f in favorites:
        rows.append((f.student.id, f.course.course_content.id, 'favorite', f.created_at))

    out: List[Tuple[str, int, EventType, datetime]] = []
    for student_id, course_id, ev_type, ts in rows:
        if isinstance(ts, datetime) and ts.tzinfo is None:
            ts = ts.replace(tzinfo=timezone.utc)
        out.append((str(student_id), int(course_id), ev_type, ts))
    return out
