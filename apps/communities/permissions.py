from rest_framework import permissions
from .models import Membership, Community

class IsCommunityAdminOrReadOnly(permissions.BasePermission):
    """
    Allow safe methods for anyone (subject to visibility checks in views).
    Only community admins (or community creator) can edit/delete community settings.
    """

    def has_object_permission(self, request, view, obj):
        # obj is Community instance
        if request.method in permissions.SAFE_METHODS:
            return True
        # allow creator
        if getattr(obj, "created_by", None) == request.user:
            return True
        # check membership role
        try:
            mem = Membership.objects.filter(community=obj, user=request.user, is_approved=True).first()
            if mem and mem.role == Membership.ADMIN:
                return True
        except Exception:
            pass
        return False

def is_member(user, community):
    return Membership.objects.filter(community=community, user=user, is_approved=True).exists()

def is_admin(user, community):
    """
    Return True if the given user is considered a community admin.
    A user is admin if:
      - they are the community.creator (created_by), OR
      - they are a superuser, OR
      - they have an approved Membership with role == Membership.ADMIN.
    """
    if not user or not getattr(user, "is_authenticated", False):
        return False

    # fast checks: creator or site superuser
    if getattr(community, "created_by_id", None) == getattr(user, "id", None):
        return True
    if getattr(user, "is_superuser", False):
        return True

    # lastly, check membership role
    m = Membership.objects.filter(community=community, user=user, is_approved=True).first()
    return bool(m and m.role == Membership.ADMIN)

