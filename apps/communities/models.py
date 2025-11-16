from django.db import models
from django.conf import settings
from django.utils.text import slugify

User = settings.AUTH_USER_MODEL


class Community(models.Model):
    PUBLIC = "public"
    PRIVATE = "private"
    HIDDEN = "hidden"
    VISIBILITY_CHOICES = [
        (PUBLIC, "Public"),
        (PRIVATE, "Private"),
        (HIDDEN, "Hidden"),
    ]

    name = models.CharField(max_length=150)
    slug = models.SlugField(max_length=170, unique=True, blank=True)
    # simple text category field (e.g. "gaming", "python", "music")
    category = models.CharField(max_length=100, blank=True, null=True)
    # community picture (one image)
    picture = models.ImageField(upload_to="communities/pictures/", null=True, blank=True)
    # short description and a longer about field
    description = models.CharField(max_length=400, blank=True)
    about = models.TextField(blank=True)
    visibility = models.CharField(max_length=10, choices=VISIBILITY_CHOICES, default=PRIVATE)
    created_by = models.ForeignKey(User, related_name="created_communities", on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    member_count = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["-created_at"]

    def save(self, *args, **kwargs):
        # auto-generate slug from name only when empty
        if not self.slug:
            base = slugify(self.name)[:150]
            slug = base
            i = 1
            while Community.objects.filter(slug=slug).exists():
                slug = f"{base}-{i}"
                i += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name}"


class Membership(models.Model):
    ADMIN = "admin"
    MODERATOR = "moderator"
    MEMBER = "member"
    ROLE_CHOICES = [(ADMIN, "Admin"), (MODERATOR, "Moderator"), (MEMBER, "Member")]

    community = models.ForeignKey(Community, related_name="memberships", on_delete=models.CASCADE)
    user = models.ForeignKey(User, related_name="community_memberships", on_delete=models.CASCADE)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default=MEMBER)
    joined_at = models.DateTimeField(auto_now_add=True)
    is_approved = models.BooleanField(default=True)  # for private communities set False initially

    class Meta:
        unique_together = ("community", "user")

    def __str__(self):
        return f"{self.user} in {self.community} as {self.role}"


class JoinRequest(models.Model):
    community = models.ForeignKey(Community, related_name="join_requests", on_delete=models.CASCADE)
    user = models.ForeignKey(User, related_name="community_join_requests", on_delete=models.CASCADE)
    message = models.CharField(max_length=500, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    processed = models.BooleanField(default=False)
    accepted = models.BooleanField(null=True, blank=True)  # None = unprocessed, True = accepted, False = rejected

    class Meta:
        unique_together = ("community", "user")


class CommunityPost(models.Model):
    community = models.ForeignKey(Community, related_name="posts", on_delete=models.CASCADE)
    author = models.ForeignKey(User, related_name="community_posts", on_delete=models.CASCADE)
    text = models.TextField(blank=True)
    image = models.ImageField(upload_to="community/posts/", null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_removed = models.BooleanField(default=False)
    removed_by = models.ForeignKey(User, null=True, blank=True, related_name="+", on_delete=models.SET_NULL)

    class Meta:
        ordering = ["-created_at"]

#for the post like coment in te community
class PostLike(models.Model):
    post = models.ForeignKey("CommunityPost", on_delete=models.CASCADE, related_name="likes")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="post_likes")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("post", "user")
        ordering = ("-created_at",)

    def __str__(self):
        return f"{self.user_id} likes {self.post_id}"


class PostComment(models.Model):
    post = models.ForeignKey("CommunityPost", on_delete=models.CASCADE, related_name="comments")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="post_comments")
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_removed = models.BooleanField(default=False)

    class Meta:
        ordering = ("created_at",)

    def __str__(self):
        return f"Comment {self.pk} on {self.post_id} by {self.user_id}"


class PostReport(models.Model):
    STATUS_PENDING = "pending"
    STATUS_ACCEPTED = "accepted"
    STATUS_REJECTED = "rejected"
    STATUS_CHOICES = (
        (STATUS_PENDING, "Pending"),
        (STATUS_ACCEPTED, "Accepted"),
        (STATUS_REJECTED, "Rejected"),
    )

    post = models.ForeignKey("CommunityPost", on_delete=models.CASCADE, related_name="reports")
    reporter = models.ForeignKey(User, on_delete=models.CASCADE, related_name="reports_made")
    reason = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default=STATUS_PENDING)
    handled_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="reports_handled")

    class Meta:
        ordering = ("-created_at",)

    def __str__(self):
        return f"Report {self.pk} for post {self.post_id} ({self.status})"