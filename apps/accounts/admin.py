from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from .models import User, Profile

class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name = "Profile"
    fk_name = "user"
    fields = ("bio", "dob", "gender", "avatar", "created_at", "updated_at")
    readonly_fields = ("created_at", "updated_at")

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    inlines = (ProfileInline,)

    # if you want custom list_display
    list_display = ("username", "email", "is_staff", "is_active", "is_email_verified")
    list_filter = ("is_staff", "is_superuser", "is_active", "is_email_verified", "groups")

    fieldsets = (
        (None, {"fields": ("username", "password")}),
        (_("Personal info"), {"fields": ("first_name", "last_name", "email")}),
        (_("Permissions"), {
            "fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions"),
        }),
        (_("Important dates"), {"fields": ("last_login", "date_joined")}),
    )

    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("username", "email", "password1", "password2"),
        }),
    )

    search_fields = ("username", "email", "first_name", "last_name")
    ordering = ("username",)
    filter_horizontal = ("groups", "user_permissions")

    def get_inline_instances(self, request, obj=None):
        """
        Ensure profile inline only shown if app has Profile registered.
        """
        inline_instances = []
        if obj is None:
            # when creating a new user, still show inline (profile auto-created on save via signals)
            inline_instances = [ProfileInline(self.model, self.admin_site)]
        else:
            inline_instances = [ProfileInline(self.model, self.admin_site)]
        return inline_instances

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "dob", "gender", "created_at")
    search_fields = ("user__username", "user__email")
    readonly_fields = ("created_at", "updated_at")
