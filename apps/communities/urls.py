from django.urls import path
from .views import (
    CommunityListCreateView, CommunityRetrieveUpdateDestroyView,
    JoinCommunityView, LeaveCommunityView,
    CommunityPostListCreateView, CommunityCommentListCreateView,
    CommunityEventListCreateView, CommunityPollListCreateView
)

app_name = "communities"

urlpatterns = [
    path('', CommunityListCreateView.as_view(), name='community_list_create'),
    path('<int:pk>/', CommunityRetrieveUpdateDestroyView.as_view(), name='community_detail'),
    
    path('join/', JoinCommunityView.as_view(), name='join_community'),
    path('leave/<int:community_id>/', LeaveCommunityView.as_view(), name='leave_community'),
    
    path('<int:community_id>/posts/', CommunityPostListCreateView.as_view(), name='community_posts'),
    path('posts/<int:post_id>/comments/', CommunityCommentListCreateView.as_view(), name='community_comments'),
    
    path('<int:community_id>/events/', CommunityEventListCreateView.as_view(), name='community_events'),
    path('<int:community_id>/polls/', CommunityPollListCreateView.as_view(), name='community_polls'),
]
