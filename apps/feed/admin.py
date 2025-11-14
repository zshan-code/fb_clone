from django.contrib import admin
from .models import Post

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ("id", "author", "visibility", "created_at")
    search_fields = ("author__username", "text")
    readonly_fields = ("created_at", "updated_at")
