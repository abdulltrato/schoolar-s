from django.apps import AppConfig
# Configuração base de apps do Django.


class EscolaConfig(AppConfig):
    """Configuração da aplicação School."""

    # Usa BigAutoField para PKs.
    default_auto_field = "django.db.models.BigAutoField"
    # Caminho Python da app.
    name = "apps.school"
    # Nome legível para admin.
    verbose_name = "Escola"

    def ready(self):
        """Conecta sinais no carregamento da app."""
        # Importa handlers de sinais para registro.
        from . import signals  # noqa: F401
