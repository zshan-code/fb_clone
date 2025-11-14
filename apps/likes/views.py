from rest_framework import status, permissions, generics
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Like
from .serializers import LikeSerializer
from apps.feed.models import Post
from django.shortcuts import get_object_or_404
from django.db import IntegrityError

class LikePostView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, post_id):
        post = get_object_or_404(Post, pk=post_id)
        try:
            like = Like.objects.create(post=post, user=request.user)
        except IntegrityError:
            return Response({"detail": "Already liked."}, status=status.HTTP_400_BAD_REQUEST)
        return Response(LikeSerializer(like).data, status=status.HTTP_201_CREATED)

class UnlikePostView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, post_id):
        post = get_object_or_404(Post, pk=post_id)
        deleted, _ = Like.objects.filter(post=post, user=request.user).delete()
        if deleted:
            return Response({"detail": "Unliked."}, status=status.HTTP_200_OK)
        return Response({"detail": "Not liked."}, status=status.HTTP_400_BAD_REQUEST)

class PostLikesListView(generics.ListAPIView):
    """
    List likes on a post (optionally show users who liked)
    """
    serializer_class = LikeSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        post_id = self.kwargs.get("post_id")
        return Like.objects.filter(post_id=post_id).select_related("user")
