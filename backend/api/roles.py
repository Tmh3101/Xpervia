from rest_framework.permissions import BasePermission

# Admin role
class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.role == 'admin'

# Teacher role
class IsTeacher(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.role == 'teacher'


# Student role    
class IsStudent(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.role == 'student'


# Owner permission
class IsCourseOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user.role == 'teacher' and obj.course.teacher == request.user

class IsCourseOfChapterOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user.role == 'teacher' and obj.course.teacher == request.user
    
class IsCourseOfLessonOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user.role == 'teacher' and obj.course.teacher == request.user
    
class IsUserOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user == obj
    
