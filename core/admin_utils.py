from __future__ import annotations

from typing import Iterable

from django import forms
from django.contrib import admin
from django.core.exceptions import FieldDoesNotExist

from core.models import tenant_id_from_user


def model_has_field(model, field_name: str) -> bool:
    try:
        model._meta.get_field(field_name)
        return True
    except FieldDoesNotExist:
        return False


AUDIT_READONLY_FIELDS: tuple[str, ...] = ("created_at", "updated_at", "deleted_at")


def resolve_request_tenant(request) -> str:
    if not request:
        return ""
    tenant_id = (getattr(request, "tenant_id", "") or "").strip()
    if tenant_id:
        return tenant_id
    request_user = getattr(request, "user", None)
    return (tenant_id_from_user(request_user) or "").strip()


def iter_request_user_field_names(model) -> Iterable[str]:
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


class SafeModelForm(forms.ModelForm):
    """
    Prevents admin forms from crashing when model validation raises errors for fields
    that are not present on the form (e.g., readonly admin fields).
    """

    def add_error(self, field, error):
        if field is None and isinstance(error, dict):
            for field_name, field_errors in error.items():
                if field_name in self.fields:
                    super().add_error(field_name, field_errors)
                else:
                    super().add_error(None, field_errors)
            return

        if field is None and hasattr(error, "error_dict"):
            error_dict = getattr(error, "error_dict", None) or {}
            for field_name, field_errors in error_dict.items():
                if field_name in self.fields:
                    super().add_error(field_name, field_errors)
                else:
                    super().add_error(None, field_errors)
            return

        if field and field not in self.fields:
            return super().add_error(None, error)

        return super().add_error(field, error)


class TenantAdminForm(SafeModelForm):
    def __init__(self, *args, request=None, **kwargs):
        self.request = request
        self.request_user = getattr(request, "user", None) if request else None
        super().__init__(*args, **kwargs)
        tenant_id = self._resolve_request_tenant()
        tenant_field = self.fields.get("tenant_id")
        if tenant_field is not None:
            tenant_field.disabled = True
            if tenant_id:
                tenant_field.initial = tenant_id

        if self.request_user and getattr(self.request_user, "is_authenticated", False):
            model = self._meta.model
            create_field = getattr(model, "REQUEST_USER_CREATE_FIELD", None)
            create_fields = getattr(model, "REQUEST_USER_CREATE_FIELDS", None) or ()
            update_field = getattr(model, "REQUEST_USER_UPDATE_FIELD", None)
            update_fields = getattr(model, "REQUEST_USER_UPDATE_FIELDS", None) or ()

            if not self.instance.pk:
                for field_name in [*( [create_field] if create_field else [] ), *list(create_fields)]:
                    field_name = (field_name or "").strip()
                    if not field_name:
                        continue
                    setattr(self.instance, field_name, self.request_user)

            for field_name in [*( [update_field] if update_field else [] ), *list(update_fields)]:
                field_name = (field_name or "").strip()
                if not field_name:
                    continue
                setattr(self.instance, field_name, self.request_user)

            for field_name in iter_request_user_field_names(model):
                user_field = self.fields.get(field_name)
                if user_field is None:
                    continue
                user_field.disabled = True
                user_field.initial = self.request_user
        self._apply_queryset_filters(tenant_id)

    def _apply_queryset_filters(self, tenant_id: str) -> None:
        if not tenant_id:
            return
        for field in self.fields.values():
            queryset = getattr(field, "queryset", None)
            if queryset is None:
                continue
            try:
                field.queryset = queryset.filter(tenant_id=tenant_id)
            except Exception:
                continue

    def clean(self):
        cleaned_data = super().clean()
        tenant_id = (getattr(self.instance, "tenant_id", "") or "").strip()
        if not tenant_id:
            tenant_id = self._resolve_request_tenant()
        if tenant_id:
            self.instance.tenant_id = tenant_id
            cleaned_data["tenant_id"] = tenant_id

        if self.request_user and getattr(self.request_user, "is_authenticated", False):
            model = self._meta.model
            create_field = getattr(model, "REQUEST_USER_CREATE_FIELD", None)
            create_fields = getattr(model, "REQUEST_USER_CREATE_FIELDS", None) or ()
            update_field = getattr(model, "REQUEST_USER_UPDATE_FIELD", None)
            update_fields = getattr(model, "REQUEST_USER_UPDATE_FIELDS", None) or ()

            if not self.instance.pk:
                for field_name in [*( [create_field] if create_field else [] ), *list(create_fields)]:
                    field_name = (field_name or "").strip()
                    if not field_name:
                        continue
                    setattr(self.instance, field_name, self.request_user)
                    if field_name in self.fields:
                        cleaned_data[field_name] = self.request_user

            for field_name in [*( [update_field] if update_field else [] ), *list(update_fields)]:
                field_name = (field_name or "").strip()
                if not field_name:
                    continue
                setattr(self.instance, field_name, self.request_user)
                if field_name in self.fields:
                    cleaned_data[field_name] = self.request_user
        return cleaned_data

    def _resolve_request_tenant(self) -> str:
        return resolve_request_tenant(self.request)


class TenantAwareAdmin(admin.ModelAdmin):
    form = TenantAdminForm
    readonly_fields = ("tenant_id",)

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = list(super().get_readonly_fields(request, obj=obj))

        for field_name in AUDIT_READONLY_FIELDS:
            if model_has_field(self.model, field_name) and field_name not in readonly_fields:
                readonly_fields.append(field_name)

        for field_name in iter_request_user_field_names(self.model):
            if model_has_field(self.model, field_name) and field_name not in readonly_fields:
                readonly_fields.append(field_name)

        if model_has_field(self.model, "code") and getattr(self.model, "AUTO_CODE", False):
            if "code" not in readonly_fields:
                readonly_fields.append("code")

        if model_has_field(self.model, "custom_id"):
            if "custom_id" not in readonly_fields:
                readonly_fields.append("custom_id")

        return tuple(readonly_fields)

    def get_form(self, request, obj=None, change=False, **kwargs):
        form_class = super().get_form(request, obj, change=change, **kwargs)

        class RequestAwareForm(form_class):
            def __init__(self, *args, **inner_kwargs):
                inner_kwargs["request"] = request
                super().__init__(*args, **inner_kwargs)

        return RequestAwareForm


class DerivedTenantAdmin(admin.ModelAdmin):
    form = SafeModelForm
    readonly_fields = ("tenant_id",)

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = list(super().get_readonly_fields(request, obj=obj))

        for field_name in AUDIT_READONLY_FIELDS:
            if model_has_field(self.model, field_name) and field_name not in readonly_fields:
                readonly_fields.append(field_name)

        for field_name in iter_request_user_field_names(self.model):
            if model_has_field(self.model, field_name) and field_name not in readonly_fields:
                readonly_fields.append(field_name)

        if model_has_field(self.model, "code") and getattr(self.model, "AUTO_CODE", False):
            if "code" not in readonly_fields:
                readonly_fields.append("code")

        if model_has_field(self.model, "custom_id"):
            if "custom_id" not in readonly_fields:
                readonly_fields.append("custom_id")

        return tuple(readonly_fields)
