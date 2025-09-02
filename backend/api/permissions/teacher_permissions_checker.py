from rest_framework.permissions import BasePermission
from api.enums import RoleEnum
from api.models import (
    Course, Chapter, Lesson, Assignment, Submission, SubmissionScore
)

class IsTeacher(BasePermission):
    def has_permission(self, request, view):
        return request.user.role == RoleEnum.TEACHER.name
    
# Owner permission for course, chapter, lesson
class IsCourseOwner(BasePermission):
    def has_permission(self, request, view):
        if 'course_id' in view.kwargs:
            try:
                course = Course.objects.get(id=view.kwargs.get('course_id'))
            except Course.DoesNotExist:
                return True
            return course.course_content.teacher_id == request.user.id
        
        if 'chapter_id' in view.kwargs:
            try:
                chapter = Chapter.objects.get(id=view.kwargs.get('chapter_id'))
            except Chapter.DoesNotExist:
                return True
            return chapter.course_content.teacher_id == request.user.id

        if 'lesson_id' in view.kwargs:
            try:
                lesson = Lesson.objects.get(id=view.kwargs.get('lesson_id'))
            except Lesson.DoesNotExist:
                return True
            return lesson.course_content.teacher_id == request.user.id

        if 'assignment_id' in view.kwargs:
            try:
                assignment = Assignment.objects.get(id=view.kwargs.get('assignment_id'))
            except Assignment.DoesNotExist:
                return True
            return assignment.lesson.course_content.teacher_id == request.user.id
        
        if 'submission_id' in view.kwargs:
            try:
                submission = Submission.objects.get(id=view.kwargs.get('submission_id'))
            except Submission.DoesNotExist:
                return True
            return submission.assignment.lesson.course_content.teacher_id == request.user.id
        
        return True

    def has_object_permission(self, request, view, obj):
        if isinstance(obj, Course):
            return obj.course_content.teacher_id == request.user.id
        
        if isinstance(obj, Chapter) or isinstance(obj, Lesson):
            return obj.course_content.teacher_id == request.user.id
        
        if isinstance(obj, Assignment):
            return obj.lesson.course_content.teacher_id == request.user.id
        
        if isinstance(obj, Submission):
            return obj.assignment.lesson.course_content.teacher_id == request.user.id
        
        if isinstance(obj, SubmissionScore):
            return obj.submission.assignment.lesson.course_content.teacher_id == request.user.id

        return True