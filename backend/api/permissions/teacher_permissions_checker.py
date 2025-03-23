from rest_framework.permissions import BasePermission
from api.enums import RoleEnum
from api.models import (
    Course, Chapter, Lesson, Assignment, Submission, SubmissionScore, CourseContent
)

class IsTeacher(BasePermission):
    def has_permission(self, request, view):
        return request.user.role == RoleEnum.TEACHER.name
    
# Owner permission for course, chapter, lesson
class IsCourseOwner(BasePermission):
    def has_permission(self, request, view):

        if view.kwargs.get('course_id'):
            try:
                course = Course.objects.get(id=view.kwargs.get('course_id'))
            except Course.DoesNotExist:
                return True
            return course.course_content.teacher == request.user
        
        if view.kwargs.get('chapter_id'):
            try:
                chapter = Chapter.objects.get(id=view.kwargs.get('chapter_id'))
            except Chapter.DoesNotExist:
                return True
            return chapter.course_content.teacher == request.user
        
        if view.kwargs.get('lesson_id'):
            try:
                lesson = Lesson.objects.get(id=view.kwargs.get('lesson_id'))
            except Lesson.DoesNotExist:
                return True
            return lesson.course_content.teacher == request.user
        
        if view.kwargs.get('assignment_id'):
            try:
                assignment = Assignment.objects.get(id=view.kwargs.get('assignment_id'))
            except Assignment.DoesNotExist:
                return True
            return assignment.lesson.course_content.teacher == request.user
        
        if view.kwargs.get('submission_id'):
            try:
                submission = Submission.objects.get(id=view.kwargs.get('submission_id'))
            except Submission.DoesNotExist:
                return True
            return submission.assignment.lesson.course_content.teacher == request.user
        
        return True

    def has_object_permission(self, request, view, obj):
        if isinstance(obj, Course):
            return obj.course_content.teacher == request.user
        elif isinstance(obj, Chapter) or isinstance(obj, Lesson):
            return obj.course_content.teacher == request.user
        elif isinstance(obj, Assignment):
            course_content = obj.lesson.course_content
            return course_content.teacher == request.user
        elif isinstance(obj, Submission):
            course_content = obj.assignment.lesson.course_content
            return course_content.teacher == request.user
        elif isinstance(obj, SubmissionScore):
            course_content = obj.submission.assignment.lesson.course_content
            return course_content.teacher == request.user
        return True