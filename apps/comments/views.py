from rest_framework import generics, permissions
from .models import Comment
from .serializers import CommentSerializer
from .permissions import IsAuthorOrReadOnly
from apps.feed.models import Post
from django.shortcuts import get_object_or_404

class CommentListCreateView(generics.ListCreateAPIView):
    """
    GET: list comments for a post (query: /?post=<post_id> or use URL pattern)
    POST: create comment for a post (post field required)
    """
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        post_id = self.kwargs.get("post_id") or self.request.query_params.get("post")
        if post_id:
            return Comment.objects.filter(post_id=post_id).select_related("author")
        return Comment.objects.all().select_related("author")

    def perform_create(self, serializer):
        # if url contains post_id, set it automatically
        post_id = self.kwargs.get("post_id")
        if post_id:
            post = get_object_or_404(Post, pk=post_id)
            serializer.save(author=self.request.user, post=post)
        else:
            serializer.save(author=self.request.user)


# appending th updated class
# apps/comments/views.py


class CommentDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve / update / delete a single comment.
    Only the comment author can update or delete.
    """
    queryset = Comment.objects.all().select_related("author", "post")
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly]
