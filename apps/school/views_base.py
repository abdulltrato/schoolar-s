from rest_framework import viewsets
# Viewsets base do DRF.

from core.viewsets import TenantModelViewSet
# ViewSet custom que aplica scoping de tenant.


class TenantReadOnlyViewSet(viewsets.ReadOnlyModelViewSet):
    """Base ReadOnly com escopo de tenant aplicado via filtros/permissions."""

    # Nenhuma customização extra; usado para semântica.
    pass


class TenantModelViewSetMixin(TenantModelViewSet):
    """Alias curto para o TenantModelViewSet usado nos módulos novos."""

    # Não altera comportamento, apenas nomeia de forma sucinta.
    pass
