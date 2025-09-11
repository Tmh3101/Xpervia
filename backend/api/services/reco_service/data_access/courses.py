from api.models import CourseContent, Course
from typing import List, Dict, Optional

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