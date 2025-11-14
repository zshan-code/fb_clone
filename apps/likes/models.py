from django.db import models
from django.conf import settings
from apps.feed.models import Post

class Like(models.Model):
    post = models.ForeignKey(Post, related_name="likes", on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="likes", on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("post", "user")
        ordering = ["-created_at"]

    def __str__(self):
        return f"Like by {self.user} on post {self.post_id}"
