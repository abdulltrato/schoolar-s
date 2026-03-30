from django.contrib import admin
# Ferramentas do Django admin.

from core.admin_utils import TenantAwareAdmin
# Mixin que aplica scoping de tenant.

from .models import Progression
# Modelo de progresso/acompanhamento.


@admin.register(Progression)
class ProgressionAdmin(TenantAwareAdmin):
    """Admin básico para Progression com filtros de tenant herdados."""
    pass
