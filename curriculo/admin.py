from django.contrib import admin
from .models import AreaCurricular, Disciplina, Competencia, CurriculoBase, CurriculoLocal

admin.site.register(AreaCurricular)
admin.site.register(Disciplina)
admin.site.register(Competencia)
admin.site.register(CurriculoBase)
admin.site.register(CurriculoLocal)
