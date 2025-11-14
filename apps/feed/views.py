# the views for the feed functionalities

from rest_framework import generics, permissions, pagination
from django.db.models import Q
from .models import Post
from .serializers import PostSerializer
from django.contrib.auth import get_user_model

from apps.friendships.models import Friendship  # uses your friendships app

#import made for the update del teh post created
from ..feed.permissions import IsAuthorOrReadOnly

User = get_user_model()

class StandardResultsPagination(pagination.PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 50

class CreatePostView(generics.CreateAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticated]

    # supports multipart/form-data for image uploads

class FeedListView(generics.ListAPIView):
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardResultsPagination

    def get_queryset(self):
        user = self.request.user

        # friend IDs for the requesting user
        friend_ids = Friendship.objects.filter(user=user).values_list("friend_id", flat=True)

        # posts that are public OR (friends and posted by a friend) OR the user's own posts
        qs = Post.objects.filter(
            Q(visibility=Post.PUBLIC) |
            Q(author__in=friend_ids, visibility=Post.FRIENDS) |
            Q(author=user)
        ).select_related("author").order_by("-created_at")
        return qs

class PostDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET: retrieve single post
    PUT/PATCH: update post (author only)
    DELETE: delete post (author only)
    """
    queryset = Post.objects.all().select_related("author")
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly]