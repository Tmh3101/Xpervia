from rest_framework.permissions import BasePermission
from api.enums.role_enum import RoleEnum
from api.models.lesson_model import Lesson
from api.models.chapter_model import Chapter
from api.models.enrollment_model import Enrollment

class IsStudent(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.role == RoleEnum.STUDENT.name
    

class WasCourseEnrolled(BasePermission):
    def has_object_permission(self, request, view, obj):
        if isinstance(obj, Chapter):
            course = obj.course
        
        elif isinstance(obj, Lesson):
            course = obj.course
        
        else:
            lesson_id = view.kwargs.get('lesson_id')
            if not lesson_id:
                return False
            try:
                lesson = Lesson.objects.get(id=lesson_id)
                course = lesson.course
            except Lesson.DoesNotExist:
                return False

        return (
            request.user and
            request.user.role == RoleEnum.STUDENT.name and
            Enrollment.objects.filter(
                student=request.user,
                course_detail__course=course
            ).exists()
        )
        