from django.apps import AppConfig
# Configuração base de apps do Django.


class CurriculoConfig(AppConfig):
    """Configuração da aplicação de currículo para registro no Django."""

    # Usa BigAutoField para chaves primárias por padrão.
    default_auto_field = "django.db.models.BigAutoField"
    # Caminho Python da app.
    name = "apps.curriculum"
    # Nome legível exibido no admin.
    verbose_name = "Currículo"
