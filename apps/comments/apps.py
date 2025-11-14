from django.apps import AppConfig

class CommentsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.comments"

    def ready(self):
        # import signals here if you have them, e.g.:
        # from . import signals  # noqa: F401
        pass
