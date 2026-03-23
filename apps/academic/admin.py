from django.contrib import admin
from .models import Student, StudentCompetency


@admin.register(Student)
class AlunoAdmin(admin.ModelAdmin):
    list_display = ("name", "grade", "education_level", "cycle", "estado")
    list_filter = ("cycle", "estado", "grade")
    search_fields = ("name",)
    readonly_fields = ("education_level", "cycle",)
    fields = ("name", "birth_date", "grade", "education_level", "cycle", "estado")

    @admin.display(description="Nível de Ensino")
    def education_level(self, obj):
        if not obj or not obj.grade:
            return "-"
        return obj.education_level.title()


admin.site.register(StudentCompetency)
