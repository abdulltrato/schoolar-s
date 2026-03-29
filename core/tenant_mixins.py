from __future__ import annotations

from django.core.exceptions import ValidationError


class TenantValidationMixin:
    """
    Shared tenant validation helpers to reduce duplication across models.
    """

    def ensure_tenant(self, *candidate_tenants: str) -> str:
        """
        Accepts candidate tenant_ids (strings) and sets self.tenant_id from the first non-empty,
        ensuring it matches any existing tenant_id on the instance.
        """
        current = (getattr(self, "tenant_id", "") or "").strip()
        for candidate in candidate_tenants:
            candidate = (candidate or "").strip()
            if not candidate:
                continue
            if current and current != candidate:
                raise ValidationError({"tenant_id": "tenant_id must be consistent across related objects."})
            current = candidate
        if not current:
            raise ValidationError({"tenant_id": "tenant_id is required."})
        setattr(self, "tenant_id", current)
        return current
