from django.apps import AppConfig


class KonamiConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "konami"

    def ready(self):
        import konami.signals   # noqa: F401