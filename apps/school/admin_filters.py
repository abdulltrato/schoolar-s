from django.contrib import admin


class EducationTrackFilter(admin.SimpleListFilter):
    title = "Ensino"
    parameter_name = "education_track"

    def lookups(self, request, model_admin):
        return (
            ("primary", "Primário"),
            ("secondary", "Secundário"),
            ("technical_professional", "Técnico Prof."),
        )

    def queryset(self, request, queryset):
        value = (self.value() or "").lower()
        if value == "primary":
            return queryset.filter(classroom__grade__number__lte=6)
        if value == "secondary":
            return queryset.filter(classroom__grade__number__gte=7, classroom__grade__number__lte=12)
        if value == "technical_professional":
            return queryset.filter(classroom__grade__number__gte=13)
        return queryset


class CycleBandFilter(admin.SimpleListFilter):
    title = "Ciclo / Nível"
    parameter_name = "cycle_band"

    def lookups(self, request, model_admin):
        return (
            ("primary_cycle_1", "Primário 1º ciclo"),
            ("primary_cycle_2", "Primário 2º ciclo"),
            ("secondary_cycle_1", "Secundário 1º ciclo"),
            ("secondary_cycle_2", "Secundário 2º ciclo"),
            ("technical_basic", "Técnico Básico"),
            ("technical_medium", "Técnico Médio"),
            ("technical_superior", "Técnico Superior"),
        )

    def queryset(self, request, queryset):
        value = (self.value() or "").lower()
        if value == "primary_cycle_1":
            return queryset.filter(classroom__grade__number__lte=3)
        if value == "primary_cycle_2":
            return queryset.filter(classroom__grade__number__gte=4, classroom__grade__number__lte=6)
        if value == "secondary_cycle_1":
            return queryset.filter(classroom__grade__number__gte=7, classroom__grade__number__lte=9)
        if value == "secondary_cycle_2":
            return queryset.filter(classroom__grade__number__gte=10, classroom__grade__number__lte=12)
        if value == "technical_basic":
            return queryset.filter(classroom__grade__number__gte=13, classroom__grade__number__lte=15)
        if value == "technical_medium":
            return queryset.filter(classroom__grade__number__gte=16, classroom__grade__number__lte=18)
        if value == "technical_superior":
            return queryset.filter(classroom__grade__number__gte=19)
        return queryset
