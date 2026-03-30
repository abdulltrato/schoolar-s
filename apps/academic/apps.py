from django.apps import AppConfig


# Configuração da aplicação Django para o módulo acadêmico.
class AcademicoConfig(AppConfig):
    # Usa BigAutoField como tipo padrão para chaves primárias.
    default_auto_field = "django.db.models.BigAutoField"
    # Caminho Python completo da aplicação.
    name = "apps.academic"
    # Nome legível exibido no admin.
    verbose_name = "Acadêmico"
