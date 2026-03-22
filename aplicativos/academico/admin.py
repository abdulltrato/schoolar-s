from django.contrib import admin
from .models import Aluno, AlunoCompetencia


@admin.register(Aluno)
class AlunoAdmin(admin.ModelAdmin):
    list_display = ("nome", "classe", "nivel_ensino", "ciclo", "estado")
    list_filter = ("ciclo", "estado", "classe")
    search_fields = ("nome",)
    readonly_fields = ("nivel_ensino", "ciclo",)
    fields = ("nome", "data_nascimento", "classe", "nivel_ensino", "ciclo", "estado")

    @admin.display(description="Nível de Ensino")
    def nivel_ensino(self, obj):
        if not obj or not obj.classe:
            return "-"
        return obj.nivel_ensino.title()


admin.site.register(AlunoCompetencia)
