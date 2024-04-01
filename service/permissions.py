from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsAdminOrRoomClient(BasePermission):
    """
    Checking if the user is the room client or a superuser.
    For room clients only delete and safe methods on object level are allowed.
    """

    def has_object_permission(self, request, view, obj):
        return bool(
            (obj.client == request.user and (request.method in SAFE_METHODS or request.method == 'DELETE'))
            or request.user.is_superuser
        )


class IsAdminOrReadOnly(BasePermission):
    """
    Checking if the user is a superuser. Otherwise, only safe methods are allowed.
    """

    def has_permission(self, request, view):
        return bool(
            request.method in SAFE_METHODS or request.user.is_superuser
        )

    def has_object_permission(self, request, view, obj):
        return bool(
            request.method in SAFE_METHODS or request.user.is_superuser
        )
