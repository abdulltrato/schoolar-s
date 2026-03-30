from django.apps import AppConfig
# Classe base de configuração de apps.


class CertificateConfig(AppConfig):
    """Configuração da aplicação de certificados."""

    # Tipo padrão de chave primária.
    default_auto_field = "django.db.models.BigAutoField"
    # Caminho do aplicativo.
    name = "apps.certificate"
    # Nome legível exibido no admin.
    verbose_name = "Certificados"
