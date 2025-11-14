# apps/friendships/views.py
from rest_framework import generics, status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db import IntegrityError, transaction
from django.contrib.auth import get_user_model

from .models import FriendRequest, Friendship
from .serializers import FriendRequestSerializer, FriendshipSerializer



User = get_user_model()

class SendFriendRequestView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        to_user_id = request.data.get("to_user")
        if not to_user_id:
            return Response({"detail": "to_user is required."}, status=status.HTTP_400_BAD_REQUEST)
        if int(to_user_id) == request.user.id:
            return Response({"detail": "Cannot send friend request to yourself."}, status=status.HTTP_400_BAD_REQUEST)

        to_user = get_object_or_404(User, pk=to_user_id)

        # If already friends
        if Friendship.objects.filter(user=request.user, friend=to_user).exists():
            return Response({"detail": "Already friends."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            fr, created = FriendRequest.objects.get_or_create(from_user=request.user, to_user=to_user, defaults={"message": request.data.get("message","")})
            if not created:
                return Response({"detail": "Friend request already sent."}, status=status.HTTP_400_BAD_REQUEST)
        except IntegrityError:
            return Response({"detail": "Could not create friend request."}, status=status.HTTP_400_BAD_REQUEST)

        return Response(FriendRequestSerializer(fr).data, status=status.HTTP_201_CREATED)


class CancelFriendRequestView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, request_id):
        fr = get_object_or_404(FriendRequest, pk=request_id, from_user=request.user)
        fr.delete()
        return Response({"detail": "Friend request canceled."}, status=status.HTTP_200_OK)


class IncomingFriendRequestsList(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = FriendRequestSerializer

    def get_queryset(self):
        return FriendRequest.objects.filter(to_user=self.request.user).order_by("-created_at")


class OutgoingFriendRequestsList(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = FriendRequestSerializer

    def get_queryset(self):
        return FriendRequest.objects.filter(from_user=self.request.user).order_by("-created_at")


class AcceptFriendRequestView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, request_id):
        fr = get_object_or_404(FriendRequest, pk=request_id, to_user=request.user)
        with transaction.atomic():
            # create both sides of friendship
            Friendship.objects.get_or_create(user=fr.from_user, friend=fr.to_user)
            Friendship.objects.get_or_create(user=fr.to_user, friend=fr.from_user)
            fr.delete()
        return Response({"detail": "Friend request accepted."}, status=status.HTTP_200_OK)


class DeclineFriendRequestView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, request_id):
        fr = get_object_or_404(FriendRequest, pk=request_id, to_user=request.user)
        fr.delete()
        return Response({"detail": "Friend request declined."}, status=status.HTTP_200_OK)


class FriendsListView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = FriendshipSerializer

    def get_queryset(self):
        return Friendship.objects.filter(user=self.request.user).select_related("friend").order_by("-created_at")


class UnfriendView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, friend_id):
        friend = get_object_or_404(User, pk=friend_id)
        Friendship.objects.filter(user=request.user, friend=friend).delete()
        Friendship.objects.filter(user=friend, friend=request.user).delete()
        return Response({"detail": "Unfriended."}, status=status.HTTP_200_OK)

