from rest_framework.permissions import BasePermission
from rest_framework.exceptions import PermissionDenied
from api.enums.role_enum import RoleEnum

class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        if not request.user.role == RoleEnum.ADMIN.name:
            raise PermissionDenied('You are not an admin')
        return True