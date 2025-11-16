# apps/communities/urls.py
from django.urls import path
from .views import (
    CommunityListCreateView,
    CommunityDetailView,
    JoinCommunityView,
    LeaveCommunityView,
    ListMembersView,
    ApproveJoinRequestView,
    RejectJoinRequestView,
    CommunityPostListCreateView,
    CommunityPostDetailView,
    CommunityJoinRequestListView,
    CommunityReportListView,
    RemoveMemberView,
    PostReportActionView,   # <- add this import
)

app_name = "communities"

urlpatterns = [
    path("", CommunityListCreateView.as_view(), name="community-list"),
    path("<slug:slug>/", CommunityDetailView.as_view(), name="community-detail"),
    path("<slug:slug>/join/", JoinCommunityView.as_view(), name="community-join"),
    path("<slug:slug>/leave/", LeaveCommunityView.as_view(), name="community-leave"),
    path("<slug:slug>/members/", ListMembersView.as_view(), name="community-members"),
    path("<slug:slug>/requests/<int:request_id>/approve/", ApproveJoinRequestView.as_view(), name="approve-request"),
    path("<slug:slug>/requests/<int:request_id>/reject/", RejectJoinRequestView.as_view(), name="reject-request"),
    #fetch the all the request in the specific community
    path("<slug:slug>/requests/", CommunityJoinRequestListView.as_view(), name="community-requests"),
    path("<slug:slug>/posts/", CommunityPostListCreateView.as_view(), name="post-list-create"),
    path("<slug:slug>/posts/<int:pk>/", CommunityPostDetailView.as_view(), name="post-detail"),

    # list reports for community (already present)
    path("<slug:slug>/reports/", CommunityReportListView.as_view(), name="community-reports"),

    # **action endpoint for a specific report (accept/reject)**
    path("<slug:slug>/reports/<int:report_id>/action/", PostReportActionView.as_view(), name="report-action"),

    path("<slug:slug>/remove-member/<int:membership_id>/", RemoveMemberView.as_view(), name="remove-member"),
]
