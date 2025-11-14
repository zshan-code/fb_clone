# apps/friendships/models.py
from django.db import models
from django.conf import settings

User = settings.AUTH_USER_MODEL

class FriendRequest(models.Model):
    from_user = models.ForeignKey(User, related_name="sent_friend_requests", on_delete=models.CASCADE)
    to_user = models.ForeignKey(User, related_name="received_friend_requests", on_delete=models.CASCADE)
    message = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("from_user", "to_user")
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.from_user} -> {self.to_user}"

class Friendship(models.Model):
    user = models.ForeignKey(User, related_name="friends", on_delete=models.CASCADE)
    friend = models.ForeignKey(User, related_name="friend_of", on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "friend")

    def __str__(self):
        return f"{self.user} is friends with {self.friend}"
