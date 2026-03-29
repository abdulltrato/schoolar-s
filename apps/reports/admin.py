import json

from django import forms
from django.contrib import admin
from django.core.exceptions import ValidationError

from core.admin_utils import TenantAwareAdmin, TenantAdminForm

from .models import Report


class ReportAdminForm(TenantAdminForm):
    content = forms.CharField(
        required=False,
        label="Conteúdo",
        help_text="Aceita texto simples ou JSON. Texto simples será guardado como {'text': <conteúdo>}",
        widget=forms.Textarea(attrs={"rows": 8}),
    )

    class Meta:
        model = Report
        fields = "__all__"

    def clean_content(self):
        raw = self.cleaned_data.get("content")
        if raw in (None, ""):
            return {}

        # If already a structured value (e.g., from admin raw_id import), keep it.
        if isinstance(raw, (dict, list)):
            return raw

        if isinstance(raw, str):
            stripped = raw.strip()
            if not stripped:
                return {}
            # Try to parse as JSON; fallback to wrapping as text.
            try:
                parsed = json.loads(stripped)
                if isinstance(parsed, (dict, list)):
                    return parsed
                # Parsed as a primitive (string/number/bool); wrap as text.
                return {"text": parsed}
            except json.JSONDecodeError:
                return {"text": stripped}

        raise ValidationError("Formato de conteúdo inválido; forneça texto ou JSON.")


@admin.register(Report)
class ReportAdmin(TenantAwareAdmin):
    form = ReportAdminForm
    list_display = ("title", "type", "tenant_id", "student", "generated_at")
    readonly_fields = ("serial_number", "verification_code", "verification_hash", "verification_version")
