from django.contrib import admin
from .models import CurriculumArea, Subject, Competency, BaseCurriculum, LocalCurriculum

admin.site.register(CurriculumArea)
admin.site.register(Subject)
admin.site.register(Competency)
admin.site.register(BaseCurriculum)
admin.site.register(LocalCurriculum)
