from django.contrib.auth import get_user_model
from .models import Block
from apps.profiles.models import Profile  # Profile lives in apps.profiles
from apps.friendships.models import FriendRequest, Friendship

User = get_user_model()

def are_friends(user1, user2):
    """
    Return True if a confirmed friendship exists between the two users.
    Confirmed friendships are represented by the `Friendship` model.
    """
    return Friendship.objects.filter(user=user1, friend=user2).exists() or \
           Friendship.objects.filter(user=user2, friend=user1).exists()


def is_blocked(user_a, user_b):
    """
    Returns True if user_a blocked user_b OR user_b blocked user_a.
    """
    return Block.objects.filter(blocker=user_a, blocked=user_b).exists() or \
           Block.objects.filter(blocker=user_b, blocked=user_a).exists()


# apps/chat/utils.py

def can_send_message(sender, receiver):
    """
    Check if sender can send a message to receiver.
    Returns (allowed: bool, reason: str).
    Current checks: blocked status. Expand as needed.
    """
    if is_blocked(sender, receiver):
        return False, "You are blocked or have blocked this user."

    return True, "Message can be sent."