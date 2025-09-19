from rest_framework.permissions import BasePermission
from api.enums import RoleEnum
from api.models import Enrollment, Lesson, Chapter, Assignment, Course

class IsStudent(BasePermission):
    def has_permission(self, request, view):
        return request.user.role == RoleEnum.STUDENT.name
    

class WasCourseEnrolled(BasePermission):
    def has_permission(self, request, view):
        course_content = None

        if 'lesson_id' in view.kwargs:
            try:
                lesson = Lesson.objects.get(id=view.kwargs.get('lesson_id'))
                course_content = lesson.course_content
            except Lesson.DoesNotExist:
                return True
        
        if 'course_id' in view.kwargs:
            try:
                course = Course.objects.get(id=view.kwargs.get('course_id'))
                course_content = course.course_content
            except Course.DoesNotExist:
                return True
        
        if 'chapter_id' in view.kwargs:
            try:
                chapter = Chapter.objects.get(id=view.kwargs.get('chapter_id'))
                course_content = chapter.course_content
            except Chapter.DoesNotExist:
                return True
            
        if 'assignment_id' in view.kwargs:
            try:
                assignment = Assignment.objects.get(id=view.kwargs.get('assignment_id'))
                course_content = assignment.lesson.course_content
            except Assignment.DoesNotExist:
                return True
            
        if not course_content:
            return True
        
        return Enrollment.objects.filter(
            student_id=request.user.id,
            course__course_content=course_content
        ).exists()

    def has_object_permission(self, request, view, obj):
        if isinstance(obj, Chapter) or isinstance(obj, Lesson):
            course_content = obj.course_content
        elif isinstance(obj, Assignment):
            course_content = obj.lesson.course_content    
        else:
            return True

        return Enrollment.objects.filter(
            student_id=request.user.id,
            course__course_content=course_content
        ).exists()
    

class IsSubmissionOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.student_id == request.user.id
