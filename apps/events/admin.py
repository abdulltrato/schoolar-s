from django.contrib import admin

from core.admin_utils import TenantAwareAdmin

from .models import Event


@admin.register(Event)
class EventAdmin(TenantAwareAdmin):
    pass
