# apps/communities/posts_urls.py
from django.urls import path
from . import views

urlpatterns = [
    # under /api/posts/ the pattern becomes: /api/posts/<pk>/like/
    path("<int:pk>/like/", views.PostLikeToggleView.as_view(), name="post-like"),
    # /api/posts/<pk>/comments/
    path("<int:pk>/comments/", views.PostCommentListCreateView.as_view(), name="post-comments"),
    # /api/posts/<pk>/report/
    path("<int:pk>/report/", views.PostReportCreateView.as_view(), name="post-report"),
    # comment detail (not nested)
    path("comments/<int:pk>/", views.PostCommentDetailView.as_view(), name="comment-detail"),
    # report action is ok here if you want it under /api/posts/ as well:
    path("reports/<int:report_id>/action/", views.PostReportActionView.as_view(), name="report-action"),
]
