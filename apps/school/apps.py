from django.apps import AppConfig


class EscolaConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.school"
    verbose_name = "Escola"

    def ready(self):
        from . import signals  # noqa: F401
