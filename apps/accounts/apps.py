from django.apps import AppConfig

class AppsAccountsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.accounts"
    label = "apps_accounts"

    def ready(self):
        import apps.accounts.signals  # noqa: F401
