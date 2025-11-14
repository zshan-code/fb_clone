# The functionalities of the feed
from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Post

User = get_user_model()

class UserMiniSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "username")

class PostSerializer(serializers.ModelSerializer):
    author = UserMiniSerializer(read_only=True)
    image = serializers.ImageField(required=False, allow_null=True)

    class Meta:
        model = Post
        fields = ("id", "author", "text", "image", "visibility", "created_at", "updated_at")
        read_only_fields = ("id", "author", "created_at", "updated_at")

    def create(self, validated_data):
        request = self.context.get("request")
        validated_data["author"] = request.user
        return super().create(validated_data)
