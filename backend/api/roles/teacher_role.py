from rest_framework.permissions import BasePermission
from api.enums.role_enum import RoleEnum

class IsTeacher(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.role == RoleEnum.TEACHER.name
    
# Owner permission for course, chapter, lesson
class IsCourseOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user.role == RoleEnum.TEACHER.name and obj.course.teacher == request.user