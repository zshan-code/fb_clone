from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db import transaction
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly


# ... other imports above ...
from .models import Community, Membership, JoinRequest, CommunityPost,PostReport, PostLike, PostComment
from .serializers import (
    CommunitySerializer,
    MembershipSerializer,
    JoinRequestSerializer,
    CommunityPostSerializer,
    PostLikeSerializer,
    PostCommentSerializer,
    PostReportSerializer
)
from .permissions import IsCommunityAdminOrReadOnly, is_member, is_admin


# -----------------------
# COMMUNITY LIST + CREATE
# -----------------------
class CommunityListCreateView(generics.ListCreateAPIView):
    queryset = Community.objects.all().select_related("created_by")
    serializer_class = CommunitySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        qs = super().get_queryset()

        q = self.request.query_params.get("q")
        cat = self.request.query_params.get("category")
        visibility = self.request.query_params.get("visibility")

        if q:
            qs = qs.filter(name__icontains=q) | qs.filter(description__icontains=q)

        if cat:
            qs = qs.filter(category__icontains=cat)

        if visibility:
            qs = qs.filter(visibility=visibility)

        # restrict hidden communities
        user = self.request.user if self.request.user.is_authenticated else None
        if not user:
            qs = qs.exclude(visibility=Community.HIDDEN)

        return qs

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


# -----------------------
# COMMUNITY DETAIL
# -----------------------
class CommunityDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Community.objects.all().select_related("created_by")
    serializer_class = CommunitySerializer
    lookup_field = "slug"
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsCommunityAdminOrReadOnly]


# -----------------------
# JOIN COMMUNITY
# -----------------------
class JoinCommunityView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, slug):
        community = get_object_or_404(Community, slug=slug)

        if is_member(request.user, community):
            return Response({"detail": "Already a member."}, status=status.HTTP_400_BAD_REQUEST)

        # PUBLIC → instant join
        if community.visibility == Community.PUBLIC:
            with transaction.atomic():
                m, created = Membership.objects.get_or_create(
                    community=community,
                    user=request.user,
                    defaults={"is_approved": True},
                )
                community.member_count = Membership.objects.filter(
                    community=community,
                    is_approved=True
                ).count()
                community.save(update_fields=["member_count"])

            return Response(
                {"detail": "Joined community.", "membership_id": m.id},
                status=status.HTTP_201_CREATED,
            )

        # PRIVATE / HIDDEN → create join request
        jr, created = JoinRequest.objects.get_or_create(
            community=community,
            user=request.user,
            defaults={"message": request.data.get("message", "")},
        )

        if not created:
            return Response(
                {"detail": "Join request already pending or processed."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(JoinRequestSerializer(jr).data, status=status.HTTP_201_CREATED)


# -----------------------
# LEAVE COMMUNITY
# -----------------------
class LeaveCommunityView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, slug):
        community = get_object_or_404(Community, slug=slug)

        membership = Membership.objects.filter(
            community=community, user=request.user
        ).first()

        if not membership:
            return Response({"detail": "Not a member."}, status=status.HTTP_400_BAD_REQUEST)

        membership.delete()

        community.member_count = Membership.objects.filter(
            community=community, is_approved=True
        ).count()
        community.save(update_fields=["member_count"])

        return Response({"detail": "Left community."}, status=status.HTTP_200_OK)


# -----------------------
# LIST MEMBERS
# -----------------------
class ListMembersView(generics.ListAPIView):
    serializer_class = MembershipSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        slug = self.kwargs.get("slug")
        community = get_object_or_404(Community, slug=slug)
        return Membership.objects.filter(
            community=community, is_approved=True
        ).select_related("user")


# -----------------------
# APPROVE JOIN REQUEST
# -----------------------
class ApproveJoinRequestView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, slug, request_id):
        community = get_object_or_404(Community, slug=slug)

        if not is_admin(request.user, community):
            return Response(
                {"detail": "Not permitted."},
                status=status.HTTP_403_FORBIDDEN,
            )

        jr = get_object_or_404(JoinRequest, pk=request_id, community=community)

        if jr.processed:
            return Response({"detail": "Already processed."}, status=status.HTTP_400_BAD_REQUEST)

        with transaction.atomic():
            jr.processed = True
            jr.accepted = True
            jr.save(update_fields=["processed", "accepted"])

            m, created = Membership.objects.get_or_create(
                community=community,
                user=jr.user,
                defaults={"role": Membership.MEMBER, "is_approved": True},
            )

            community.member_count = Membership.objects.filter(
                community=community,
                is_approved=True
            ).count()
            community.save(update_fields=["member_count"])

        return Response(
            {"detail": "Join request accepted.", "membership_id": m.id},
            status=status.HTTP_200_OK,
        )


# -----------------------
# REJECT JOIN REQUEST
# -----------------------
class RejectJoinRequestView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, slug, request_id):
        community = get_object_or_404(Community, slug=slug)

        if not is_admin(request.user, community):
            return Response(
                {"detail": "Not permitted."},
                status=status.HTTP_403_FORBIDDEN,
            )

        jr = get_object_or_404(JoinRequest, pk=request_id, community=community)

        if jr.processed:
            return Response({"detail": "Already processed."}, status=status.HTTP_400_BAD_REQUEST)

        jr.processed = True
        jr.accepted = False
        jr.save(update_fields=["processed", "accepted"])

        return Response({"detail": "Join request rejected."}, status=status.HTTP_200_OK)


# -----------------------
# COMMUNITY POSTS
# -----------------------
class CommunityPostListCreateView(generics.ListCreateAPIView):
    """
    List posts in a community and allow members (or public) to create posts.
    Preserves existing permission and membership checks, and sets author on create.
    Returns `author` (id) and `author_detail` (object with name + avatar).
    """
    serializer_class = CommunityPostSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        slug = self.kwargs.get("slug")
        community = get_object_or_404(Community, slug=slug)

        user = self.request.user
        qs = CommunityPost.objects.filter(community=community, is_removed=False)

        # if private/hidden, only members can view
        if community.visibility in (Community.HIDDEN, Community.PRIVATE) and not is_member(user, community):
            return CommunityPost.objects.none()

        # select_related to avoid N+1 when serializing author and (optionally) profile
        # if your avatar is on profile, ensure author__profile is available
        return qs.select_related("author", "author__profile").order_by("-created_at")

    def perform_create(self, serializer):
        community = get_object_or_404(Community, slug=self.kwargs.get("slug"))
        user = self.request.user

        # only members can post in private/hidden communities
        if community.visibility in (Community.PRIVATE, Community.HIDDEN) and not is_member(user, community):
            raise permissions.PermissionDenied("Only members can post in this community.")

        # explicitly set community and author (keeps old behavior)
        serializer.save(community=community, author=user)


class CommunityPostDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve / update / delete a community post.
    """
    serializer_class = CommunityPostSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        # include author and community to avoid additional queries
        return CommunityPost.objects.select_related("author", "community").all()




# ---- Add this class near your other join-request / membership views ----
class CommunityJoinRequestListView(generics.ListAPIView):
    """
    List join requests for a community.
    Only community creator or admins may view.
    Optional query param `processed=true|false` to filter.
    """
    serializer_class = JoinRequestSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        slug = self.kwargs.get("slug")
        community = get_object_or_404(Community, slug=slug)

        # authorization: only creator or admin may list requests
        user = self.request.user
        if community.created_by != user and not is_admin(user, community):
            # return empty queryset - but better to raise permission denied
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("Not permitted to view join requests for this community.")

        qs = JoinRequest.objects.filter(community=community).order_by("-created_at")
        # optional filter: processed=true/false
        processed = self.request.query_params.get("processed")
        if processed is not None:
            if processed.lower() in ("1", "true", "yes"):
                qs = qs.filter(processed=True)
            elif processed.lower() in ("0", "false", "no"):
                qs = qs.filter(processed=False)
        return qs

# Like / Unlike
class PostLikeToggleView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        post = get_object_or_404(CommunityPost, pk=pk)
        user = request.user
        like, created = PostLike.objects.get_or_create(post=post, user=user)
        if created:
            return Response({"detail": "Liked"}, status=status.HTTP_201_CREATED)
        return Response({"detail": "Already liked"}, status=status.HTTP_200_OK)

    def delete(self, request, pk):
        post = get_object_or_404(CommunityPost, pk=pk)
        user = request.user
        deleted, _ = PostLike.objects.filter(post=post, user=user).delete()
        if deleted:
            return Response({"detail": "Unliked"}, status=status.HTTP_200_OK)
        return Response({"detail": "Not liked"}, status=status.HTTP_400_BAD_REQUEST)


# Comments: list/create and detail
class PostCommentListCreateView(generics.ListCreateAPIView):
    serializer_class = PostCommentSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        post = get_object_or_404(CommunityPost, pk=self.kwargs.get("pk"))
        return PostComment.objects.filter(post=post, is_removed=False).select_related("user").order_by("created_at")

    def perform_create(self, serializer):
        post = get_object_or_404(CommunityPost, pk=self.kwargs.get("pk"))
        serializer.save(post=post, user=self.request.user)


class PostCommentDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = PostCommentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return PostComment.objects.select_related("user", "post").all()

    def perform_update(self, serializer):
        comment = self.get_object()
        if comment.user != self.request.user:
            raise permissions.PermissionDenied("Can't edit someone else's comment.")
        serializer.save()

    def perform_destroy(self, instance):
        # soft-delete comment (keeps history)
        if instance.user != self.request.user:
            raise permissions.PermissionDenied("Can't delete someone else's comment.")
        instance.is_removed = True
        instance.save(update_fields=["is_removed"])


# Reports: create a report
class PostReportCreateView(generics.CreateAPIView):
    serializer_class = PostReportSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        post = get_object_or_404(CommunityPost, pk=self.kwargs.get("pk"))
        serializer.save(post=post, reporter=self.request.user)


# Admin: list reports for community and act on them
class CommunityReportListView(generics.ListAPIView):
    serializer_class = PostReportSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        slug = self.kwargs.get("slug")
        community = get_object_or_404(Community, slug=slug)
        user = self.request.user
        # only community admins / creator allowed
        if not is_admin(user, community) and community.created_by != user:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("Not permitted.")
        return PostReport.objects.filter(post__community=community).select_related("post", "reporter", "handled_by").order_by("-created_at")


class PostReportActionView(APIView):
    """
    Admin endpoint to accept/reject a report.
    Accepting can optionally remove the post (is_removed=True).
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, report_id):
        report = get_object_or_404(PostReport, pk=report_id)
        community = report.post.community
        if not is_admin(request.user, community) and community.created_by != request.user:
            return Response({"detail": "Not permitted."}, status=status.HTTP_403_FORBIDDEN)

        action = request.data.get("action")  # "accept" or "reject"
        if action not in ("accept", "reject"):
            return Response({"detail": "Invalid action."}, status=status.HTTP_400_BAD_REQUEST)

        if action == "accept":
            report.status = PostReport.STATUS_ACCEPTED
            # mark handled_by
            report.handled_by = request.user
            report.save(update_fields=["status", "handled_by"])
            # optionally remove post
            remove = request.data.get("remove_post", False)
            if remove:
                report.post.is_removed = True
                report.post.save(update_fields=["is_removed"])
            return Response({"detail": "Report accepted."}, status=status.HTTP_200_OK)

        # reject
        report.status = PostReport.STATUS_REJECTED
        report.handled_by = request.user
        report.save(update_fields=["status", "handled_by"])
        return Response({"detail": "Report rejected."}, status=status.HTTP_200_OK)

#remaining The user by the admin controller
class RemoveMemberView(APIView):
    """
    Remove a membership by membership id.
    Allowed actors:
      - community.owner (created_by)
      - community admin (membership.role == ADMIN)
      - the member themself (self-unsubscribe)
      - superuser
    URL pattern expected: /api/communities/<slug>/remove-member/<int:membership_id>/
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, slug, membership_id):
        community = get_object_or_404(Community, slug=slug)
        membership = get_object_or_404(Membership, pk=membership_id, community=community)

        caller = request.user

        # allow if caller is superuser
        if caller.is_superuser:
            allowed = True
        # allow if caller is community owner (compare ids)
        elif community.created_by_id == getattr(caller, "id", None):
            allowed = True
        # allow if caller is a community admin
        elif is_admin(caller, community):
            allowed = True
        # allow if caller is the member themself
        elif membership.user_id == getattr(caller, "id", None):
            allowed = True
        else:
            allowed = False

        if not allowed:
            return Response({"detail": "Not permitted to remove this member."}, status=status.HTTP_403_FORBIDDEN)

        # perform delete and update counter atomically
        with transaction.atomic():
            membership.delete()
            community.member_count = Membership.objects.filter(community=community, is_approved=True).count()
            community.save(update_fields=["member_count"])

        return Response({"detail": "Member removed."}, status=status.HTTP_200_OK)
    
#report viewing 
class IsStaffOrSuperuser(permissions.BasePermission):
    """
    Allow access only to staff or superusers.
    (You can replace this with a more custom permission if you have a site-admin role.)
    """
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and (request.user.is_staff or request.user.is_superuser))


class AdminAllReportsListView(generics.ListAPIView):
    """
    List all PostReport entries across the site. Admins can filter by:
      - ?status=pending|accepted|rejected
      - ?community=<slug> (filter by post.community.slug)
    This endpoint is admin-only (staff or superuser).
    """
    serializer_class = PostReportSerializer
    permission_classes = [IsStaffOrSuperuser]
    queryset = PostReport.objects.select_related("post", "reporter", "handled_by", "post__community").all()

    def get_queryset(self):
        qs = super().get_queryset().order_by("-created_at")
        # optional status filter
        status = self.request.query_params.get("status")
        if status:
            qs = qs.filter(status__iexact=status)

        # optional community filter by slug
        community_slug = self.request.query_params.get("community")
        if community_slug:
            qs = qs.filter(post__community__slug=community_slug)

        return qs
    
#views  for the report action
class PostReportActionView(APIView):
    """
    Admin endpoint to accept/reject a report.
    URL: /api/communities/<slug>/reports/<report_id>/action/
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, slug, report_id):
        # find community and report, ensure they match
        community = get_object_or_404(Community, slug=slug)
        report = get_object_or_404(PostReport, pk=report_id)

        # ensure the report's post belongs to this community
        if report.post.community_id != community.id:
            return Response({"detail": "Report does not belong to this community."}, status=status.HTTP_400_BAD_REQUEST)

        # permission check: only community admin or community creator can act
        if not is_admin(request.user, community) and community.created_by != request.user:
            return Response({"detail": "Not permitted."}, status=status.HTTP_403_FORBIDDEN)

        action = request.data.get("action")  # expected "accept" or "reject"
        if action not in ("accept", "reject"):
            return Response({"detail": "Invalid action. Use 'accept' or 'reject'."}, status=status.HTTP_400_BAD_REQUEST)

        if action == "accept":
            report.status = PostReport.STATUS_ACCEPTED
            report.handled_by = request.user
            report.save(update_fields=["status", "handled_by"])
            # optionally remove the post
            remove = request.data.get("remove_post", False)
            if remove:
                post = report.post
                post.is_removed = True
                post.save(update_fields=["is_removed"])
            serializer = PostReportSerializer(report, context={"request": request})
            return Response({"detail": "Report accepted.", "report": serializer.data}, status=status.HTTP_200_OK)

        # reject
        report.status = PostReport.STATUS_REJECTED
        report.handled_by = request.user
        report.save(update_fields=["status", "handled_by"])
        serializer = PostReportSerializer(report, context={"request": request})
        return Response({"detail": "Report rejected.", "report": serializer.data}, status=status.HTTP_200_OK)


