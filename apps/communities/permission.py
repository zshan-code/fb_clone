from rest_framework import permissions
from .models import Membership

class IsCommunityAdmin(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        try:
            membership = Membership.objects.get(user=request.user, community=obj)
            return membership.role == 'admin'
        except Membership.DoesNotExist:
            return False

class IsAdminOrModerator(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        try:
            membership = Membership.objects.get(user=request.user, community=obj.community)
            return membership.role in ['admin', 'moderator']
        except Membership.DoesNotExist:
            return False

class IsOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.author == request.user or request.method in permissions.SAFE_METHODS
