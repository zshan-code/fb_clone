from rest_framework import serializers
from .models import Like
from django.contrib.auth import get_user_model

User = get_user_model()

class LikeSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Like
        fields = ("id", "post", "user", "created_at")
        read_only_fields = ("id", "user", "created_at")
