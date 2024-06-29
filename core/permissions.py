from rest_framework import permissions


class IsAdminUser(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_admin

    def has_object_permission(self, request, view, obj):
        return request.user and request.user.is_admin


class IsStaffUser(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_staff

    def has_object_permission(self, request, view, obj):
        return request.user and request.user.is_staff


class IsSuperUser(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_superuser

    def has_object_permission(self, request, view, obj):
        return request.user and request.user.is_superuser


class IsStaffOrOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        # Safe check for the 'user' attribute
        obj_user = getattr(obj, "user", None)
        return request.user and (
            request.user.is_staff or obj_user == request.user or obj == request.user
        )  # Incase the obj is the user model itself
