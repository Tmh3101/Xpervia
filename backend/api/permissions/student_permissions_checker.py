from rest_framework.permissions import BasePermission
from api.enums import RoleEnum
from api.models import Enrollment, Lesson, Chapter, Assignment, Course

class IsStudent(BasePermission):
    def has_permission(self, request, view):
        return request.user.role == RoleEnum.STUDENT.name
    

class WasCourseEnrolled(BasePermission):
    def has_permission(self, request, view):
        if 'lesson_id' in view.kwargs:
            try:
                lesson = Lesson.objects.get(id=view.kwargs.get('lesson_id'))
                course = lesson.course
            except Lesson.DoesNotExist:
                return True
        
        if 'course_id' in view.kwargs:
            try:
                course = Course.objects.get(id=view.kwargs.get('course_id'))
            except Course.DoesNotExist:
                return True
        
        if 'chapter_id' in view.kwargs:
            try:
                chapter = Chapter.objects.get(id=view.kwargs.get('chapter_id'))
                course = chapter.course
            except Chapter.DoesNotExist:
                return True
            
        if 'assignment_id' in view.kwargs:
            try:
                assignment = Assignment.objects.get(id=view.kwargs.get('assignment_id'))
                course = assignment.lesson.course
            except Assignment.DoesNotExist:
                return True
            
        return Enrollment.objects.filter(
            student=request.user,
            course_detail__course=course
        ).exists()

    def has_object_permission(self, request, view, obj):
        if isinstance(obj, Chapter) or isinstance(obj, Lesson):
            course = obj.course
        elif isinstance(obj, Assignment):
            course = obj.lesson.course     
        else:
            return True

        return Enrollment.objects.filter(
            student=request.user,
            course_detail__course=course
        ).exists()
    

class IsSubmissionOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.student == request.user
        