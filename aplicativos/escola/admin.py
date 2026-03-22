from django.contrib import admin
from .models import Professor, Turma, Matricula

admin.site.register(Professor)
admin.site.register(Turma)
admin.site.register(Matricula)
