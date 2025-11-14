from django.urls import path
from .views import (
    CommunityListCreateView, CommunityDetailView,
    MembershipRequestView, AcceptRejectMembershipView, RemoveMemberView,
    PostListCreateView, PostDetailView, PinPostView, SharePostView, LikePostView,
    EventListCreateView, EventDetailView,
    PollListCreateView, PollOptionVoteView
)

urlpatterns = [
    # Communities
    path('communities/', CommunityListCreateView.as_view(), name='community_list_create'),
    path('communities/<int:pk>/', CommunityDetailView.as_view(), name='community_detail'),

    # Membership
    path('members/join/', MembershipRequestView.as_view(), name='join_community'),
    path('members/<int:membership_id>/action/', AcceptRejectMembershipView.as_view(), name='membership_action'),
    path('members/<int:pk>/remove/', RemoveMemberView.as_view(), name='remove_member'),

    # Posts
    path('posts/', PostListCreateView.as_view(), name='post_list_create'),
    path('posts/<int:pk>/', PostDetailView.as_view(), name='post_detail'),
    path('posts/<int:pk>/pin/', PinPostView.as_view(), name='pin_post'),
    path('posts/share/', SharePostView.as_view(), name='share_post'),
    path('posts/<int:pk>/like/', LikePostView.as_view(), name='like_post'),

    # Events
    path('events/', EventListCreateView.as_view(), name='event_list_create'),
    path('events/<int:pk>/', EventDetailView.as_view(), name='event_detail'),

    # Polls
    path('polls/', PollListCreateView.as_view(), name='poll_list_create'),
    path('polls/<int:poll_id>/vote/<int:option_id>/', PollOptionVoteView.as_view(), name='poll_vote'),
]
