from api.models import CourseContent, Course
from typing import List, Dict, Optional, Tuple
from django.db.models import Count

# Lấy dữ liệu course từ DB, bao gồm categories
def fetch_courses_with_categories() -> List[Dict]:
    courses = CourseContent.objects.prefetch_related('categories').all()
    result = []
    for course in courses:
        result.append({
            'id': course.id,
            'title': course.title,
            'description': course.description,
            'categories': [cat.name for cat in course.categories.all()]
        })
    return result

# Lấy dữ liệu 1 course từ DB theo ID bao gồm categories
def fetch_course_by_id(course_id: int) -> Dict:
    try:
        course = CourseContent.objects.prefetch_related('categories').get(id=course_id)
        return {
            'id': course.id,
            'title': course.title,
            'description': course.description,
            'categories': [cat.name for cat in course.categories.all()]
        }
    except CourseContent.DoesNotExist:
        return {}
    
# Lấy tất cả course IDs
def fetch_all_course_ids() -> List[int]:
    return list(CourseContent.objects.values_list('id', flat=True))

# Lấy danh sách course_id ứng viên để gợi ý
def visible_candidates(exclude_ids: Optional[set[int]] = None) -> List[int]:
    course_contents = fetch_courses_with_categories()
    ids = []
    for cc in course_contents:
        if exclude_ids and cc['id'] in exclude_ids:
            continue
        if Course.objects.filter(id=cc['id'], is_visible=False).exists():
            continue
        ids.append(cc['id'])
    return ids

# Lấy danh sách course_id phổ biến nhất (dựa trên tổng số enroll + favorite)
def fetch_popular_course_ids(limit: int = 100) -> list[int]:
    courses = (
        Course.objects.select_related("course_content")
        .filter(is_visible=True)
        .annotate(
            num_students=Count("enrollments", distinct=True),
            num_favorites=Count("favorites", distinct=True),
        )
        .order_by("-num_students", "-num_favorites")
        .values_list("id", flat=True)
    )
    if limit > 0:
        courses = courses[:limit]

    result: List[Tuple] = []
    for cid in courses:
        result.append((cid, 1.0))  # popular courses có score = 1.0

    return result

# Lấy tất cả course_id đang is_visible=True
def list_visible_course_ids() -> list[int]:
    courses = (
        Course.objects.select_related("course_content")
        .filter(is_visible=True)
        .values_list("id", flat=True)
    )
    return list(courses)
