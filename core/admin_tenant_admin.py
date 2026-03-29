from __future__ import annotations

from django.contrib import admin

from .admin_forms import BaseTenantAdmin
from .admin_helpers import AUDIT_READONLY_FIELDS, iter_request_user_field_names, model_has_field


class TenantAwareAdmin(BaseTenantAdmin):
    """
    Admin that auto-populates tenant_id and request user audit fields.
    """

    def get_fields(self, request, obj=None):
        fields = list(super().get_fields(request, obj=obj))
        for field_name in iter_request_user_field_names(self.model):
            if model_has_field(self.model, field_name) and field_name not in fields:
                fields.append(field_name)
        return tuple(fields)

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
        model_admin = self

        class RequestAwareForm(form_class):
            def __init__(self, *args, **inner_kwargs):
                if "request" not in inner_kwargs:
                    inner_kwargs["request"] = request
                try:
                    super().__init__(*args, **inner_kwargs)
                except TypeError:
                    inner_kwargs.pop("request", None)
                    super().__init__(*args, **inner_kwargs)
                model_admin._apply_request_user_fields(self, request)

        return RequestAwareForm


class DerivedTenantAdmin(admin.ModelAdmin):
    """
    Lightweight admin for derived tenant models that cannot use TenantAdminForm directly.
    """

    readonly_fields = ("tenant_id",)

    def _apply_request_user_fields(self, form, request) -> None:
        # Reuse the same behavior as TenantAwareAdmin without depending on TenantAdminForm.
        TenantAwareAdmin._apply_request_user_fields(self, form, request)

    def get_fields(self, request, obj=None):
        fields = list(super().get_fields(request, obj=obj))
        for field_name in iter_request_user_field_names(self.model):
            if model_has_field(self.model, field_name) and field_name not in fields:
                fields.append(field_name)
        return tuple(fields)

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
        model_admin = self

        class RequestAwareForm(form_class):
            def __init__(self, *args, **inner_kwargs):
                if "request" not in inner_kwargs:
                    inner_kwargs["request"] = request
                try:
                    super().__init__(*args, **inner_kwargs)
                except TypeError:
                    inner_kwargs.pop("request", None)
                    super().__init__(*args, **inner_kwargs)
                model_admin._apply_request_user_fields(self, request)

        return RequestAwareForm
