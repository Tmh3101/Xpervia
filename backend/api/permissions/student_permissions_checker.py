from rest_framework.permissions import BasePermission
from rest_framework.exceptions import PermissionDenied, NotFound
from api.enums.role_enum import RoleEnum
from api.models.lesson_model import Lesson
from api.models.chapter_model import Chapter
from api.models.assignment_model import Assignment
from api.models.enrollment_model import Enrollment

class IsStudent(BasePermission):
    def has_permission(self, request, view):
        if not request.user.role == RoleEnum.STUDENT.name:
            raise PermissionDenied('You are not a student')
        return True
    

class WasCourseEnrolled(BasePermission):
    def has_permission(self, request, view):
        # Kiểm tra nếu view là Assignment view
        if 'lesson_id' in view.kwargs:
            lesson_id = view.kwargs.get('lesson_id')
            if not lesson_id:
                raise NotFound('Lesson ID not provided')
            try:
                lesson = Lesson.objects.get(id=lesson_id)
                course = lesson.course
            except Lesson.DoesNotExist:
                raise NotFound('Lesson does not exist')

            if not Enrollment.objects.filter(student=request.user, course_detail__course=course).exists():
                raise PermissionDenied('You are not enrolled in this course')
        
        if 'course_id' in view.kwargs:
            course_id = view.kwargs.get('course_id')
            if not Enrollment.objects.filter(student=request.user, course_detail__course_id=course_id).exists():
                raise PermissionDenied('You are not enrolled in this course')
            
        return True  # Nếu không phải Assignment view, tiếp tục kiểm tra ở has_object_permission

    def has_object_permission(self, request, view, obj):
        # Kiểm tra nếu obj là Chapter hoặc Lesson
        if isinstance(obj, Chapter) or isinstance(obj, Lesson):
            course = obj.course
        elif isinstance(obj, Assignment):
            lesson_id = view.kwargs.get('lesson_id')
            if lesson_id:
                try:
                    lesson = Lesson.objects.get(id=lesson_id)
                    course = lesson.course
                except Lesson.DoesNotExist:
                    raise NotFound('Lesson does not exist')
            else:
                assignment_id = view.kwargs.get('id')
                try:
                    assignment = Assignment.objects.get(id=assignment_id)
                    course = assignment.lesson.course
                except Assignment.DoesNotExist:
                    raise NotFound('Assignment does not exist')
                
        else:
            return False

        if not Enrollment.objects.filter(student=request.user, course_detail__course=course).exists():
            raise PermissionDenied('You are not enrolled in this course')

        return True
        