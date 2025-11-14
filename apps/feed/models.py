# the feed model for the user
from django.db import models
from django.conf import settings

class Post(models.Model):
    PUBLIC = "public"
    FRIENDS = "friends"
    PRIVATE = "private"
    VISIBILITY_CHOICES = [
        (PUBLIC, "Public"),
        (FRIENDS, "Friends"),
        (PRIVATE, "Private"),
    ]

    author = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="posts", on_delete=models.CASCADE)
    text = models.TextField(blank=True)
    image = models.ImageField(upload_to="posts/", null=True, blank=True)
    visibility = models.CharField(max_length=10, choices=VISIBILITY_CHOICES, default=FRIENDS)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Post {self.pk} by {self.author}"


