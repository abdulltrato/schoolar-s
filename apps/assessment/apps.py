from django.apps import AppConfig
# Importa classe base de configuração de apps do Django.


class AvaliacaoConfig(AppConfig):
    """Configuração da aplicação de avaliações."""

    # Define o tipo padrão de chave primária.
    default_auto_field = "django.db.models.BigAutoField"
    # Caminho completo da aplicação.
    name = "apps.assessment"
    # Nome legível exibido no admin.
    verbose_name = "Avaliação"
