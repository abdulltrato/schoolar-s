from django import forms
from django.contrib import admin
from django.contrib.auth import get_user_model

from core.admin_utils import TenantAwareAdmin, resolve_request_tenant

from .models import Student, StudentCompetency


class StudentAdminForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = "__all__"

    def __init__(self, *args, request=None, **kwargs):
        self.request = request
        super().__init__(*args, **kwargs)
        # The Student model has two user-related fields:
        # - `user`: the student's login account (optional).
        # - `usuario`: audit actor (auto-filled from the logged-in user).
        # To avoid confusion and tenant validation issues on creation, keep `user` out of the add form.
        self.fields.pop("user", None)

    def clean(self):
        cleaned_data = super().clean()
        tenant_id = (getattr(self.instance, "tenant_id", "") or "").strip()
        if not tenant_id:
            tenant_id = (resolve_request_tenant(self.request) or "").strip()
        if tenant_id:
            self.instance.tenant_id = tenant_id
            cleaned_data["tenant_id"] = tenant_id
        return cleaned_data

    def add_error(self, field, error):
        if field == "tenant_id" and field not in self.fields:
            return super().add_error(None, error)
        return super().add_error(field, error)

    def _update_errors(self, errors):
        tenant_errors = []
        if hasattr(errors, "error_dict") and "tenant_id" in errors.error_dict and "tenant_id" not in self.fields:
            tenant_errors = list(errors.error_dict.pop("tenant_id"))

        super()._update_errors(errors)

        for tenant_error in tenant_errors:
            super().add_error(None, tenant_error)

    def _resolve_tenant_id(self, cleaned_data):
        # Backwards-compat alias for older code paths (kept to minimize churn).
        return (resolve_request_tenant(self.request) or "").strip()


@admin.register(Student)
class AlunoAdmin(TenantAwareAdmin):
    form = StudentAdminForm
    list_display = ("name", "grade", "education_level", "cycle", "estado")
    list_filter = ("cycle", "estado", "grade")
    search_fields = ("name",)
    readonly_fields = ("tenant_id", "education_level", "cycle")
    fieldsets = (
        (
            "Dados do aluno",
            {
                "fields": (
                    "name",
                    "birth_date",
                    "grade",
                    "education_level",
                    "cycle",
                    "estado",
                )
            },
        ),
        (
            "Auditoria",
            {
                "fields": (
                    "tenant_id",
                    "code",
                    "usuario",
                    "created_at",
                    "updated_at",
                    "deleted_at",
                )
            },
        ),
    )

    @admin.display(description="Nível de Ensino")
    def education_level(self, obj):
        if not obj or not obj.grade:
            return "-"
        return obj.education_level.title()


class StudentCompetencyAdminForm(forms.ModelForm):
    class Meta:
        model = StudentCompetency
        fields = "__all__"

    def __init__(self, *args, request=None, **kwargs):
        self.request = request
        super().__init__(*args, **kwargs)
        tenant_id = self._resolve_request_tenant()
        student_field = self.fields.get("student")
        if student_field is not None and tenant_id:
            student_field.queryset = student_field.queryset.filter(tenant_id=tenant_id)

    def clean(self):
        cleaned_data = super().clean()
        student = cleaned_data.get("student") or getattr(self.instance, "student", None)
        tenant_id = (getattr(student, "tenant_id", "") or "").strip()
        if tenant_id:
            self.instance.tenant_id = tenant_id
            cleaned_data["tenant_id"] = tenant_id
        return cleaned_data

    def _resolve_request_tenant(self):
        return resolve_request_tenant(self.request)


@admin.register(StudentCompetency)
class StudentCompetencyAdmin(TenantAwareAdmin):
    form = StudentCompetencyAdminForm
    list_display = ("student", "competency", "nivel", "tenant_id")
    readonly_fields = ("tenant_id",)
    fields = ("student", "competency", "nivel", "tenant_id")
