from rest_framework import viewsets

from core.viewsets import TenantModelViewSet


class TenantReadOnlyViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Base ReadOnly viewset com scoping de tenant via permission classes/filters do projeto.
    """

    pass


class TenantModelViewSetMixin(TenantModelViewSet):
    """
    Alias para manter nome curto nos novos módulos.
    """

    pass
