from django.contrib import admin
from .models import Teacher, Classroom, Enrollment

admin.site.register(Teacher)
admin.site.register(Classroom)
admin.site.register(Enrollment)
