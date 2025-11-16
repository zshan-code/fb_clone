from django.apps import AppConfig

class CommunitiesConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.communities"

    def ready(self):
        # import signals so they are registered
        try:
            from . import signals  # noqa: F401
        except Exception:
            # in makemigrations/during early import this may fail; ignore safely
            pass
