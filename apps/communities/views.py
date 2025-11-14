from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Community, CommunityPost, CommunityComment, CommunityEvent, CommunityPoll
from .serializers import (
    CommunitySerializer, CommunityPostSerializer, CommunityCommentSerializer,
    CommunityEventSerializer, CommunityPollSerializer
)

# Communities
class CommunityListCreateView(generics.ListCreateAPIView):
    queryset = Community.objects.all()
    serializer_class = CommunitySerializer
    permission_classes = [IsAuthenticated]

class CommunityRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Community.objects.all()
    serializer_class = CommunitySerializer
    permission_classes = [IsAuthenticated]

# Membership
class JoinCommunityView(generics.GenericAPIView):
    serializer_class = CommunitySerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        community_id = request.data.get('community_id')
        try:
            community = Community.objects.get(id=community_id)
            community.members.add(request.user)
            return Response({'message': 'Joined successfully'})
        except Community.DoesNotExist:
            return Response({'error': 'Community not found'}, status=status.HTTP_404_NOT_FOUND)

class LeaveCommunityView(generics.GenericAPIView):
    serializer_class = CommunitySerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, community_id):
        try:
            community = Community.objects.get(id=community_id)
            community.members.remove(request.user)
            return Response({'message': 'Left successfully'})
        except Community.DoesNotExist:
            return Response({'error': 'Community not found'}, status=status.HTTP_404_NOT_FOUND)

# Posts & Comments
class CommunityPostListCreateView(generics.ListCreateAPIView):
    serializer_class = CommunityPostSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        community_id = self.kwargs['community_id']
        return CommunityPost.objects.filter(community_id=community_id)

    def perform_create(self, serializer):
        community_id = self.kwargs['community_id']
        serializer.save(author=self.request.user, community_id=community_id)

class CommunityCommentListCreateView(generics.ListCreateAPIView):
    serializer_class = CommunityCommentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        post_id = self.kwargs['post_id']
        return CommunityComment.objects.filter(post_id=post_id)

    def perform_create(self, serializer):
        post_id = self.kwargs['post_id']
        serializer.save(author=self.request.user, post_id=post_id)

# Events
class CommunityEventListCreateView(generics.ListCreateAPIView):
    serializer_class = CommunityEventSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        community_id = self.kwargs['community_id']
        return CommunityEvent.objects.filter(community_id=community_id)

    def perform_create(self, serializer):
        community_id = self.kwargs['community_id']
        serializer.save(community_id=community_id)

# Polls
class CommunityPollListCreateView(generics.ListCreateAPIView):
    serializer_class = CommunityPollSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        community_id = self.kwargs['community_id']
        return CommunityPoll.objects.filter(community_id=community_id)

    def perform_create(self, serializer):
        community_id = self.kwargs['community_id']
        serializer.save(community_id=community_id)
