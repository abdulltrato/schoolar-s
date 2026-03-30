from django.apps import AppConfig
# Configuração base de apps do Django.


class LearningConfig(AppConfig):
    """Configuração da aplicação de ensino online (cursos, aulas, tarefas)."""

    # Usa BigAutoField para PKs.
    default_auto_field = "django.db.models.BigAutoField"
    # Caminho Python da app.
    name = "apps.learning"
    # Nome exibido no admin.
    verbose_name = "Ensino Online"
