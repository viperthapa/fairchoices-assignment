from rest_framework.permissions import BasePermission


class IsSuperAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_super_admin


class IsCountryAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_country_admin


class IsSuperAdminOrCountryAdmin(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        return user.is_super_admin or user.is_country_admin
