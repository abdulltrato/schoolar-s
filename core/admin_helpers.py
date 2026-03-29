from __future__ import annotations

from typing import Iterable

from django.core.exceptions import FieldDoesNotExist

from core.models import tenant_id_from_user


AUDIT_READONLY_FIELDS: tuple[str, ...] = ("created_at", "updated_at", "deleted_at")


def model_has_field(model, field_name: str) -> bool:
    """Return True when `field_name` is present on the model (including inherited fields)."""
    try:
        model._meta.get_field(field_name)
        return True
    except FieldDoesNotExist:
        return False


def resolve_request_tenant(request) -> str:
    """Extract the tenant_id from request or authenticated user profile."""
    if not request:
        return ""
    tenant_id = (getattr(request, "tenant_id", "") or "").strip()
    if tenant_id:
        return tenant_id
    request_user = getattr(request, "user", None)
    return (tenant_id_from_user(request_user) or "").strip()


def iter_request_user_field_names(model) -> Iterable[str]:
    """Yield unique field names configured to store request user references."""
    configured = []
    for attr in ("REQUEST_USER_CREATE_FIELD", "REQUEST_USER_UPDATE_FIELD"):
        name = getattr(model, attr, None)
        if name:
            configured.append(name)
    for attr in ("REQUEST_USER_CREATE_FIELDS", "REQUEST_USER_UPDATE_FIELDS"):
        names = getattr(model, attr, None) or ()
        configured.extend(list(names))

    seen = set()
    for name in configured:
        name = (name or "").strip()
        if not name or name in seen:
            continue
        seen.add(name)
        yield name
