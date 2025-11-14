from rest_framework import serializers
from .models import Comment
from django.contrib.auth import get_user_model

User = get_user_model()

class UserMiniSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "username")

class CommentSerializer(serializers.ModelSerializer):
    author = UserMiniSerializer(read_only=True)

    class Meta:
        model = Comment
        fields = ("id", "post", "author", "text", "created_at", "updated_at")
        read_only_fields = ("id", "author", "created_at", "updated_at")

    def create(self, validated_data):
        request = self.context.get("request")
        validated_data["author"] = request.user
        return super().create(validated_data)
