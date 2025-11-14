# apps/communities/admin.py
from django.contrib import admin
from .models import Community, Membership, Post, Event, Poll, PollOption

# Register your models
@admin.register(Community)
class CommunityAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'privacy')
    search_fields = ('name', 'category')

@admin.register(Membership)
class MembershipAdmin(admin.ModelAdmin):
    list_display = ('user', 'community', 'role')
    list_filter = ('role',)
    search_fields = ('user__username', 'community__name')

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'community', 'created_at', 'pinned')
    list_filter = ('community', 'pinned')
    search_fields = ('title', 'content', 'author__username')

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'community', 'date')
    search_fields = ('title', 'community__name')

@admin.register(Poll)
class PollAdmin(admin.ModelAdmin):
    list_display = ('question', 'community', 'created_at')
    search_fields = ('question', 'community__name')

@admin.register(PollOption)
class PollOptionAdmin(admin.ModelAdmin):
    list_display = ('poll', 'option_text', 'votes')
