from django.urls import path
from .views import LikePostView, UnlikePostView, PostLikesListView

app_name = "likes"

urlpatterns = [
    path("posts/<int:post_id>/like/", LikePostView.as_view(), name="like-post"),
    path("posts/<int:post_id>/unlike/", UnlikePostView.as_view(), name="unlike-post"),
    path("posts/<int:post_id>/likes/", PostLikesListView.as_view(), name="post-likes"),
]
