from rest_framework.permissions import BasePermission
from rest_framework.exceptions import PermissionDenied, NotFound
from api.enums.role_enum import RoleEnum
from api.models.chapter_model import Chapter
from api.models.lesson_model import Lesson
from api.models.course_model import Course
from api.models.assignment_model import Assignment
from api.models.submission_score_model import SubmissionScore

class IsTeacher(BasePermission):
    def has_permission(self, request, view):
        if not request.user.role == RoleEnum.TEACHER.name:
            raise PermissionDenied('You are not a teacher')
        return True
    
# Owner permission for course, chapter, lesson
class IsCourseOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        permission_denied_message = 'You are not allowed to perform this action'

        if isinstance(obj, Course):
            if not obj.teacher == request.user:
                raise PermissionDenied(permission_denied_message)
        elif isinstance(obj, Chapter) or isinstance(obj, Lesson):
            if not obj.course.teacher == request.user:
                raise PermissionDenied(permission_denied_message)
        elif isinstance(obj, Assignment):
            lesson_id = view.kwargs.get('lesson_id')
            if not lesson_id:
                raise NotFound('Lesson ID not provided')
            try:
                lesson = Lesson.objects.get(id=lesson_id)
                course = lesson.course
            except Lesson.DoesNotExist:
                raise NotFound('Lesson does not exist')
            if not course.teacher == request.user:
                raise PermissionDenied(permission_denied_message)
        elif isinstance(obj, SubmissionScore):
            lesson = obj.submission.assignment.lesson
            course = lesson.course
            if not course.teacher == request.user:
                raise PermissionDenied(permission_denied_message)
        return True