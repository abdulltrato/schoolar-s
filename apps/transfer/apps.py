from django.apps import AppConfig
# Configuração base de apps do Django.


class TransferConfig(AppConfig):
    """Configuração da aplicação de transferências (alunos/professores)."""

    # Usa BigAutoField para PKs.
    default_auto_field = "django.db.models.BigAutoField"
    # Caminho Python da app.
    name = "apps.transfer"
    # Nome exibido no admin.
    verbose_name = "Transferências"
