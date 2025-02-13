from rest_framework.permissions import BasePermission
from api.enums.role_enum import RoleEnum

class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.role == RoleEnum.ADMIN.name