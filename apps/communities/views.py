from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Community, Membership, Post, Event, Poll, PollOption
from .serializers import CommunitySerializer, MembershipSerializer, PostSerializer, EventSerializer, PollSerializer, PollOptionSerializer
from .permission import IsCommunityAdmin, IsAdminOrModerator, IsOwnerOrReadOnly

# Community Views
class CommunityListCreateView(generics.ListCreateAPIView):
    queryset = Community.objects.all()
    serializer_class = CommunitySerializer
    permission_classes = [permissions.IsAuthenticated]

class CommunityDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Community.objects.all()
    serializer_class = CommunitySerializer
    permission_classes = [permissions.IsAuthenticated, IsCommunityAdmin]

# Membership Views
class MembershipRequestView(generics.CreateAPIView):
    queryset = Membership.objects.all()
    serializer_class = MembershipSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user, status='pending')

class AcceptRejectMembershipView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsCommunityAdmin]

    def post(self, request, membership_id):
        action = request.data.get('action')
        try:
            membership = Membership.objects.get(id=membership_id)
            if action == 'accept':
                membership.status = 'approved'
            elif action == 'reject':
                membership.status = 'rejected'
            membership.save()
            return Response({"status": membership.status})
        except Membership.DoesNotExist:
            return Response({"detail": "Membership not found"}, status=status.HTTP_404_NOT_FOUND)

class RemoveMemberView(generics.DestroyAPIView):
    queryset = Membership.objects.all()
    serializer_class = MembershipSerializer
    permission_classes = [permissions.IsAuthenticated, IsCommunityAdmin]

# Post Views
class PostListCreateView(generics.ListCreateAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        community_id = self.request.data.get('community')
        serializer.save(author=self.request.user, community_id=community_id)

class PostDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly | IsAdminOrModerator]

class PinPostView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsCommunityAdmin]

    def post(self, request, pk):
        post = Post.objects.get(pk=pk)
        post.pinned = True
        post.save()
        return Response({"detail": "Post pinned"})

    def delete(self, request, pk):
        post = Post.objects.get(pk=pk)
        post.pinned = False
        post.save()
        return Response({"detail": "Post unpinned"})

class SharePostView(generics.CreateAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(
            author=self.request.user,
            community_id=self.request.data.get('community'),
            shared_from_id=self.request.data.get('shared_from')
        )

class LikePostView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        post = Post.objects.get(pk=pk)
        if request.user in post.likes.all():
            post.likes.remove(request.user)
            liked = False
        else:
            post.likes.add(request.user)
            liked = True
        return Response({"liked": liked, "likes_count": post.likes.count()})

# Event Views
class EventListCreateView(generics.ListCreateAPIView):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

class EventDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    permission_classes = [permissions.IsAuthenticated, IsCommunityAdmin]

# Poll Views
class PollListCreateView(generics.ListCreateAPIView):
    queryset = Poll.objects.all()
    serializer_class = PollSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

class PollOptionVoteView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, poll_id, option_id):
        try:
            option = PollOption.objects.get(pk=option_id, poll_id=poll_id)
            user = request.user
            if user in option.votes.all():
                option.votes.remove(user)
                voted = False
            else:
                option.votes.add(user)
                voted = True
            return Response({"voted": voted, "votes_count": option.votes.count()})
        except PollOption.DoesNotExist:
            return Response({"detail": "Option not found"}, status=status.HTTP_404_NOT_FOUND)
