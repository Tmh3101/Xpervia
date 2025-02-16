from rest_framework.permissions import BasePermission
from api.enums import RoleEnum
from api.models import (
    Course, Chapter, Lesson, Assignment, Submission, SubmissionScore, CourseDetail
)

class IsTeacher(BasePermission):
    def has_permission(self, request, view):
        return request.user.role == RoleEnum.TEACHER.name
    
# Owner permission for course, chapter, lesson
class IsCourseOwner(BasePermission):
    def has_permission(self, request, view):
        if view.kwargs.get('course_id'):
            try:
                course_detail = CourseDetail.objects.get(id=view.kwargs.get('course_id'))
            except CourseDetail.DoesNotExist:
                return True
            return course_detail.course.teacher == request.user
        
        if view.kwargs.get('chapter_id'):
            try:
                chapter = Chapter.objects.get(id=view.kwargs.get('chapter_id'))
            except Chapter.DoesNotExist:
                return True
            return chapter.course.teacher == request.user
        
        if view.kwargs.get('lesson_id'):
            try:
                lesson = Lesson.objects.get(id=view.kwargs.get('lesson_id'))
            except Lesson.DoesNotExist:
                return True
            return lesson.course.teacher == request.user
        
        if view.kwargs.get('assignment_id'):
            try:
                assignment = Assignment.objects.get(id=view.kwargs.get('assignment_id'))
            except Assignment.DoesNotExist:
                return True
            return assignment.lesson.course.teacher == request.user
        
        if view.kwargs.get('submission_id'):
            try:
                submission = Submission.objects.get(id=view.kwargs.get('submission_id'))
            except Submission.DoesNotExist:
                return True
            return submission.assignment.lesson.course.teacher == request.user
        
        return True

    def has_object_permission(self, request, view, obj):
        if isinstance(obj, Course):
            return obj.teacher == request.user
        elif isinstance(obj, Chapter) or isinstance(obj, Lesson):
            return obj.course.teacher == request.user
        elif isinstance(obj, Assignment):
            course = obj.lesson.course
            return course.teacher == request.user
        elif isinstance(obj, Submission):
            course = obj.assignment.lesson.course
            return course.teacher == request.user
        elif isinstance(obj, SubmissionScore):
            lesson = obj.submission.assignment.lesson
            course = lesson.course
            return course.teacher == request.user
        return True