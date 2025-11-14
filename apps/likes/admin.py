from django.contrib import admin
from .models import Like

@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ("id", "post", "user", "created_at")
    search_fields = ("user__username", "post__text")
    readonly_fields = ("created_at",)
