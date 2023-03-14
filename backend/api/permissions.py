from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsAuthorOrReadOnly(BasePermission):
    def has_object_permission(self, request, view, obj):
        return ((request.method in SAFE_METHODS)
                or (obj.author == request.user))


class IsAdminPermission(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_admin


class IsStaffOrAuthorOrReadOnlyPermission(BasePermission):
    def has_permission(self, request, view):
        return (
            request.method in SAFE_METHODS
            or request.user.is_authenticated
        )

    def has_object_permission(self, request, view, obj):
        if (
            request.method in SAFE_METHODS
            or obj.author == request.user
        ):
            return True
        return (
            request.user.is_authenticated
            and (request.user.is_moderator or request.user.is_admin)
        )
