import re

from rest_framework import serializers

from apps.school.models import AcademicYear


class TenantAcademicYearField(serializers.PrimaryKeyRelatedField):
    ADMIN_ROLES = {"national_admin", "provincial_admin", "district_admin"}

    default_error_messages = {
        "invalid": "Ano letivo inválido. Use o id ou o código YYYY-YYYY.",
        "does_not_exist": "Ano letivo não encontrado para o código \"{code}\".",
        "tenant_required": "Informe X-Tenant-ID para usar o código do ano letivo.",
        "ambiguous": "Existem múltiplos anos letivos com o código \"{code}\".",
    }

    def __init__(self, **kwargs):
        kwargs.setdefault("queryset", AcademicYear.objects.all())
        super().__init__(**kwargs)

    def to_internal_value(self, data):
        if data is None:
            return super().to_internal_value(data)

        if isinstance(data, str):
            value = data.strip()
            if value.isdigit():
                return super().to_internal_value(int(value))
            if re.fullmatch(r"\d{4}-\d{4}", value):
                return self._resolve_by_code(value)

        return super().to_internal_value(data)

    def _resolve_by_code(self, code):
        queryset = self.get_queryset()
        if queryset is None:
            self.fail("invalid")

        tenant_id = self._resolve_tenant_id()
        if tenant_id:
            queryset = queryset.filter(tenant_id=tenant_id)
        queryset = queryset.filter(code=code)

        matches = list(queryset[:2])
        if len(matches) == 1:
            return matches[0]
        if not matches:
            self.fail("does_not_exist", code=code)
        if tenant_id:
            self.fail("ambiguous", code=code)
        self.fail("tenant_required", code=code)

    def _resolve_tenant_id(self):
        request = self.context.get("request")
        if not request:
            return None

        tenant_id = getattr(request, "tenant_id", None)
        if not tenant_id:
            headers = getattr(request, "headers", None)
            if headers is not None:
                tenant_id = headers.get("X-Tenant-ID")
            if not tenant_id:
                tenant_id = request.META.get("HTTP_X_TENANT_ID")

        tenant_id = (tenant_id or "").strip()
        if tenant_id:
            return tenant_id

        user = getattr(request, "user", None)
        if user and getattr(user, "is_authenticated", False):
            profile = getattr(user, "school_profile", None)
            if profile:
                if profile.role in self.ADMIN_ROLES:
                    return None
                return (profile.tenant_id or "").strip() or None
        return None
