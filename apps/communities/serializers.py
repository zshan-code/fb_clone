# serializers.py
from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Community, Membership, JoinRequest, CommunityPost, PostComment, PostLike, PostReport

User = get_user_model()


class SimpleUserForRequestsSerializer(serializers.Serializer):
    """
    Minimal user info for join-requests frontend:
    - id
    - username
    - display_name (first + last if available otherwise username)
    - avatar (absolute URL if request present and avatar exists, otherwise null)
    """
    id = serializers.IntegerField(read_only=True)
    username = serializers.CharField(read_only=True)
    display_name = serializers.SerializerMethodField(read_only=True)
    avatar = serializers.SerializerMethodField(read_only=True)

    def get_display_name(self, user):
        first = getattr(user, "first_name", "") or ""
        last = getattr(user, "last_name", "") or ""
        name = f"{first} {last}".strip()
        return name if name else getattr(user, "username", None)

    def get_avatar(self, user):
        request = self.context.get("request", None)
        # many setups store avatar on user.profile.avatar
        profile = getattr(user, "profile", None)
        if profile is not None:
            avatar_field = getattr(profile, "avatar", None)
            if avatar_field:
                try:
                    if request:
                        return request.build_absolute_uri(avatar_field.url)
                    return avatar_field.url
                except Exception:
                    return None
        # if you kept avatar directly on user model, try that too:
        avatar_field = getattr(user, "avatar", None)
        if avatar_field:
            try:
                if request:
                    return request.build_absolute_uri(avatar_field.url)
                return avatar_field.url
            except Exception:
                return None
        return None


class MembershipSerializer(serializers.ModelSerializer):
    # keep existing id-based writeable field for backwards compatibility
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    # new read-only nested user details for frontend convenience
    user_detail = SimpleUserForRequestsSerializer(source="user", read_only=True)
    role = serializers.CharField(read_only=True)

    class Meta:
        model = Membership
        fields = ("id", "community", "user", "user_detail", "role", "joined_at", "is_approved")


class CommunitySerializer(serializers.ModelSerializer):
    created_by = serializers.PrimaryKeyRelatedField(read_only=True)
    picture = serializers.ImageField(required=False, allow_null=True)
    category = serializers.CharField(required=False, allow_blank=True, allow_null=True)

    # read-only list for frontend convenience (prefetch membership_set in view)
    memberships = MembershipSerializer(source="membership_set", many=True, read_only=True)

    class Meta:
        model = Community
        fields = (
            "id",
            "name",
            "slug",
            "category",
            "picture",
            "description",
            "about",
            "visibility",
            "created_by",
            "created_at",
            "member_count",
            "memberships",
        )
        read_only_fields = ("id", "slug", "created_at", "member_count", "created_by")

    def create(self, validated_data):
        # preserve behavior: set created_by from request user
        validated_data["created_by"] = self.context["request"].user
        return super().create(validated_data)


class JoinRequestSerializer(serializers.ModelSerializer):
    # replace plain user id with nested user info for reads
    user = SimpleUserForRequestsSerializer(read_only=True)
    community = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = JoinRequest
        fields = ("id", "community", "user", "message", "created_at", "processed", "accepted")

    def create(self, validated_data):
        # preserve behavior: set user from request when creating
        request = self.context.get("request")
        validated_data["user"] = request.user
        return super().create(validated_data)


class UserBriefSerializer(serializers.ModelSerializer):
    """
    Minimal public user info used in post lists.
    display_name is computed from first_name + last_name if available, otherwise username.
    avatar is computed similarly to SimpleUserForRequestsSerializer.
    """
    display_name = serializers.SerializerMethodField()
    avatar = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ("id", "username", "display_name", "avatar")

    def get_display_name(self, obj):
        first = getattr(obj, "first_name", "") or ""
        last = getattr(obj, "last_name", "") or ""
        full = f"{first} {last}".strip()
        return full if full else getattr(obj, "username", None)

    def get_avatar(self, obj):
        request = self.context.get("request", None)

        # preference order: user.avatar then user.profile.avatar
        avatar_field = getattr(obj, "avatar", None)
        if not avatar_field:
            profile = getattr(obj, "profile", None)
            avatar_field = getattr(profile, "avatar", None) if profile is not None else None

        if not avatar_field:
            return None

        try:
            url = avatar_field.url
        except Exception:
            return None

        return request.build_absolute_uri(url) if request else url


class CommunityPostSerializer(serializers.ModelSerializer):
    author = serializers.PrimaryKeyRelatedField(read_only=True)
    author_detail = UserBriefSerializer(source="author", read_only=True)

    likes_count = serializers.SerializerMethodField()
    comments_count = serializers.SerializerMethodField()
    liked_by_user = serializers.SerializerMethodField()
    recent_comments = serializers.SerializerMethodField()  # small preview for frontend

    class Meta:
        model = CommunityPost
        fields = (
            "id",
            "community",
            "author",
            "author_detail",
            "text",
            "image",
            "likes_count",
            "comments_count",
            "liked_by_user",
            "recent_comments",
            "created_at",
            "updated_at",
            "is_removed",
        )
        read_only_fields = ("id", "author", "author_detail", "likes_count", "comments_count", "liked_by_user", "recent_comments", "created_at", "updated_at", "is_removed")

    def get_likes_count(self, obj):
        return obj.likes.count()

    def get_comments_count(self, obj):
        return obj.comments.filter(is_removed=False).count()

    def get_liked_by_user(self, obj):
        user = self.context.get("request").user
        if not user or not user.is_authenticated:
            return False
        return obj.likes.filter(user=user).exists()

    def get_recent_comments(self, obj):
        # return up to 3 recent non-removed comments
        qs = obj.comments.filter(is_removed=False).select_related("user").order_by("-created_at")[:3]
        return PostCommentSerializer(qs, many=True, context=self.context).data

    def create(self, validated_data):
        validated_data["author"] = self.context["request"].user
        return super().create(validated_data)

    def update(self, instance, validated_data):
        """
        Preserve existing image if the update payload does not include 'image'.
        This avoids losing the picture when updating other fields via PATCH or PUT.
        """
        # if 'image' not in validated_data, keep current image
        if "image" not in validated_data:
            validated_data["image"] = instance.image
        return super().update(instance, validated_data)



# serializers.py (add these below CommunityPostSerializer / UserBriefSerializer)

class PostLikeSerializer(serializers.ModelSerializer):
    user = SimpleUserForRequestsSerializer(read_only=True)

    class Meta:
        model = PostLike
        fields = ("id", "post", "user", "created_at")


class PostCommentSerializer(serializers.ModelSerializer):
    user = SimpleUserForRequestsSerializer(read_only=True)

    class Meta:
        model = PostComment
        fields = ("id", "post", "user", "text", "created_at", "updated_at", "is_removed")
        read_only_fields = ("id", "user", "created_at", "updated_at", "is_removed")

    def create(self, validated_data):
        validated_data["user"] = self.context["request"].user
        return super().create(validated_data)

    def update(self, instance, validated_data):
        # only update text if provided
        instance.text = validated_data.get("text", instance.text)
        instance.save(update_fields=["text", "updated_at"])
        return instance


class PostReportSerializer(serializers.ModelSerializer):
    reporter = SimpleUserForRequestsSerializer(read_only=True)
    handled_by = SimpleUserForRequestsSerializer(read_only=True)

    class Meta:
        model = PostReport
        fields = ("id", "post", "reporter", "reason", "created_at", "status", "handled_by")
        read_only_fields = ("id", "reporter", "created_at", "handled_by", "status")

    def create(self, validated_data):
        validated_data["reporter"] = self.context["request"].user
        return super().create(validated_data)

