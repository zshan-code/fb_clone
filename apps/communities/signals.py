from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Membership, Community

@receiver(post_save, sender=Membership)
def update_member_count_on_add(sender, instance, created, **kwargs):
    if created and instance.is_approved:
        community = instance.community
        community.member_count = Membership.objects.filter(community=community, is_approved=True).count()
        community.save(update_fields=["member_count"])

@receiver(post_delete, sender=Membership)
def update_member_count_on_remove(sender, instance, **kwargs):
    community = instance.community
    community.member_count = Membership.objects.filter(community=community, is_approved=True).count()
    community.save(update_fields=["member_count"])
