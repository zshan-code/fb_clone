# apps/feed/permissions.py
from rest_framework import permissions

class IsAuthorOrReadOnly(permissions.BasePermission):
    """
    Allow safe methods for everyone, but only the post author can edit or delete.
    """

    def has_object_permission(self, request, view, obj):
        # Read-only permissions are allowed for any request
        if request.method in permissions.SAFE_METHODS:
            return True
        # Write permissions are only allowed to the author of the post
        return getattr(obj, "author", None) == request.user
