#urls for the calling of the apis

from django.urls import path
from .views import CreatePostView, FeedListView, PostDetailView

app_name = "feed"

urlpatterns = [
    path("posts/", CreatePostView.as_view(), name="create-post"),
    path("feed/", FeedListView.as_view(), name="feed"),

    #api for the update and the del of the post
    path("posts/<int:pk>/", PostDetailView.as_view(), name="post-detail"),
]
