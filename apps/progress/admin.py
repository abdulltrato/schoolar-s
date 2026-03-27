from django.contrib import admin

from core.admin_utils import TenantAwareAdmin

from .models import Progression


@admin.register(Progression)
class ProgressionAdmin(TenantAwareAdmin):
    pass
