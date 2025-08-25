from rest_framework.permissions import BasePermission
from api.enums import RoleEnum
from api.models import (
    Course, Chapter, Lesson, Assignment, Submission, SubmissionScore, CourseContent
)

class IsTeacher(BasePermission):
    def has_permission(self, request, view):
        return request.user.user_metadata.role == RoleEnum.TEACHER.name
    
# Owner permission for course, chapter, lesson
class IsCourseOwner(BasePermission):
    def has_permission(self, request, view):
        course_id = view.kwargs.get('course_id')
        if course_id:
            try:
                course = Course.objects.get(id=course_id)
            except Course.DoesNotExist:
                return True
            return str(course.course_content.teacher_id) == request.user.id
        
        chapter_id = view.kwargs.get('chapter_id')
        if chapter_id:
            try:
                chapter = Chapter.objects.get(id=chapter_id)
            except Chapter.DoesNotExist:
                return True
            return str(chapter.course_content.teacher_id) == request.user.id
        
        lesson_id = view.kwargs.get('lesson_id')
        if lesson_id:
            try:
                lesson = Lesson.objects.get(id=lesson_id)
            except Lesson.DoesNotExist:
                return True
            return str(lesson.course_content.teacher_id) == request.user.id
        
        assignment_id = view.kwargs.get('assignment_id')
        if assignment_id:
            try:
                assignment = Assignment.objects.get(id=assignment_id)
            except Assignment.DoesNotExist:
                return True
            return str(assignment.lesson.course_content.teacher_id) == request.user.id
        
        submission_id = view.kwargs.get('submission_id')
        if submission_id:
            try:
                submission = Submission.objects.get(id=submission_id)
            except Submission.DoesNotExist:
                return True
            return str(submission.assignment.lesson.course_content.teacher_id) == request.user.id
        
        return True

    def has_object_permission(self, request, view, obj):
        if isinstance(obj, Course):
            return str(obj.course_content.teacher_id) == request.user.id
        elif isinstance(obj, Chapter) or isinstance(obj, Lesson):
            return str(obj.course_content.teacher_id) == request.user.id
        elif isinstance(obj, Assignment):
            course_content = obj.lesson.course_content
            return str(course_content.teacher_id) == request.user.id
        elif isinstance(obj, Submission):
            course_content = obj.assignment.lesson.course_content
            return str(course_content.teacher_id) == request.user.id
        elif isinstance(obj, SubmissionScore):
            course_content = obj.submission.assignment.lesson.course_content
            return str(course_content.teacher_id) == request.user.id
        return True