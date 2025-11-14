from django.urls import path
from .views import CommentListCreateView, CommentDetailView

app_name = "comments"

urlpatterns = [
    # create/list comments for a post (post_id optional in url)
    path("posts/<int:post_id>/comments/", CommentListCreateView.as_view(), name="post-comments"),
    # list all comments or filter by ?post=<id>
    path("comments/", CommentListCreateView.as_view(), name="comments"),
    # detail: update/delete by comment id
    path("comments/<int:pk>/", CommentDetailView.as_view(), name="comment-detail"),
]
