# apps/friendships/serializers.py
from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import FriendRequest, Friendship

User = get_user_model()

class FriendRequestSerializer(serializers.ModelSerializer):
    from_user = serializers.PrimaryKeyRelatedField(read_only=True)
    to_user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())

    class Meta:
        model = FriendRequest
        fields = ("id", "from_user", "to_user", "message", "created_at")
        read_only_fields = ("id", "from_user", "created_at")

class FriendshipSerializer(serializers.ModelSerializer):
    friend = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Friendship
        fields = ("id", "friend", "created_at")
