from django.contrib import admin
from .models import Community, Membership, JoinRequest, CommunityPost

@admin.register(Community)
class CommunityAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "slug", "visibility", "created_by", "member_count", "created_at")
    search_fields = ("name", "slug", "description", "about", "category")
    readonly_fields = ("member_count",)
    list_filter = ("visibility",)

@admin.register(Membership)
class MembershipAdmin(admin.ModelAdmin):
    list_display = ("id", "community", "user", "role", "is_approved", "joined_at")
    search_fields = ("community__name", "user__username", "user__email")
    list_filter = ("role", "is_approved")

@admin.register(JoinRequest)
class JoinRequestAdmin(admin.ModelAdmin):
    list_display = ("id", "community", "user", "message", "created_at", "processed", "accepted")
    search_fields = ("community__name", "user__username", "message")
    list_filter = ("processed", "accepted")

@admin.register(CommunityPost)
class CommunityPostAdmin(admin.ModelAdmin):
    list_display = ("id", "community", "author", "created_at", "is_removed")
    search_fields = ("community__name", "author__username", "text")
    list_filter = ("is_removed",)
