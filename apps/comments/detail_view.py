from rest_framework import generics, permissions
from .models import Comment
from .serializers import CommentSerializer
from .permissions import IsAuthorOrReadOnly
#is ko simple views.py main b blend kia ja skta hy
class CommentDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Comment.objects.all().select_related("author")
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly]
