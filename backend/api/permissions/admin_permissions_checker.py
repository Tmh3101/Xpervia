from rest_framework.permissions import BasePermission
from api.enums import RoleEnum

class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.role == RoleEnum.ADMIN.name