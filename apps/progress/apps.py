from django.apps import AppConfig
# Configuração base de apps do Django.


class ProgressoConfig(AppConfig):
    """Configuração da aplicação de progresso (avaliações e notas)."""

    # Usa BigAutoField para PKs.
    default_auto_field = "django.db.models.BigAutoField"
    # Caminho Python da app.
    name = "apps.progress"
    # Nome exibido no admin.
    verbose_name = "Progresso"
