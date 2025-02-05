from rest_framework.permissions import BasePermission

# Admin role
class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.role == 'admin'

# Teacher role
class IsTeacher(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.role == 'teacher'

class IsTeacherAndOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user.role == 'teacher' and obj.teacher == request.user

# Student role    
class IsStudent(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.role == 'student'
    
