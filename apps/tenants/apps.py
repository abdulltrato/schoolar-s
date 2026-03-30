from django.apps import AppConfig
# Configuração base de apps do Django.


class TenantsConfig(AppConfig):
    """Configuração da app de tenants (multi-escola)."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.tenants"
    verbose_name = "Escola"
