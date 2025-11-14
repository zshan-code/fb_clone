# apps/friendships/urls.py
from django.urls import path
from .views import (
    SendFriendRequestView, CancelFriendRequestView,
    IncomingFriendRequestsList, OutgoingFriendRequestsList,
    AcceptFriendRequestView, DeclineFriendRequestView,
    FriendsListView, UnfriendView,
)

app_name = "friendships"

urlpatterns = [
    path("send/", SendFriendRequestView.as_view(), name="send-request"),
    path("cancel/<int:request_id>/", CancelFriendRequestView.as_view(), name="cancel-request"),
    path("incoming/", IncomingFriendRequestsList.as_view(), name="incoming-requests"),
    path("outgoing/", OutgoingFriendRequestsList.as_view(), name="outgoing-requests"),
    path("accept/<int:request_id>/", AcceptFriendRequestView.as_view(), name="accept-request"),
    path("decline/<int:request_id>/", DeclineFriendRequestView.as_view(), name="decline-request"),
    path("friends/", FriendsListView.as_view(), name="friends-list"),
    path("unfriend/<int:friend_id>/", UnfriendView.as_view(), name="unfriend"),
]
