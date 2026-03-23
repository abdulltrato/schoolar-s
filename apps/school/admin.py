from django.contrib import admin
from .models import AuditAlert, AuditEvent, Teacher, Classroom, Enrollment

admin.site.register(Teacher)
admin.site.register(Classroom)
admin.site.register(Enrollment)
admin.site.register(AuditEvent)
admin.site.register(AuditAlert)
