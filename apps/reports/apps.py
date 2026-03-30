from django.apps import AppConfig
# Configuração base de apps do Django.


class RelatoriosConfig(AppConfig):
    """Configuração da aplicação de relatórios."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.reports"
    verbose_name = "Relatórios"
