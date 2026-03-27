from django.contrib import admin

from core.admin_utils import TenantAwareAdmin

from .models import Report


@admin.register(Report)
class ReportAdmin(TenantAwareAdmin):
    pass
