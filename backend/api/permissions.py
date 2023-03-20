from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsAdminPermission(BasePermission):
    '''Разрешение действий только для администратора.'''
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_admin


class IsAdminOrAuthorOrReadOnlyPermission(BasePermission):
    '''
    Разрешение действий только для администратора или для создателя объекта.
    '''
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
            request.user.is_authenticated and request.user.is_admin
        )
