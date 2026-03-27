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
        user_field = self.fields.get("user")
        if user_field is not None:
            user_field.queryset = get_user_model().objects.filter(
                school_profile__tenant_id__isnull=False,
            ).exclude(
                school_profile__tenant_id=""
            ).distinct()

    def clean(self):
        cleaned_data = super().clean()
        tenant_id = self._resolve_tenant_id(cleaned_data)
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
        tenant_id = (getattr(self.instance, "tenant_id", "") or "").strip()
        if tenant_id:
            return tenant_id

        request_tenant_id = (getattr(self.request, "tenant_id", "") or "").strip()
        if request_tenant_id:
            return request_tenant_id

        request_user = getattr(self.request, "user", None)
        profile = getattr(request_user, "school_profile", None) if request_user and request_user.is_authenticated else None
        profile_tenant_id = (getattr(profile, "tenant_id", "") or "").strip()
        if profile_tenant_id:
            return profile_tenant_id

        linked_user = cleaned_data.get("user") or getattr(self.instance, "user", None)
        linked_profile = getattr(linked_user, "school_profile", None) if linked_user else None
        return (getattr(linked_profile, "tenant_id", "") or "").strip()


@admin.register(Student)
class AlunoAdmin(TenantAwareAdmin):
    form = StudentAdminForm
    list_display = ("name", "grade", "education_level", "cycle", "estado")
    list_filter = ("cycle", "estado", "grade")
    search_fields = ("name",)
    readonly_fields = ("tenant_id", "education_level", "cycle")
    fields = (
        "tenant_id",
        "user",
        "name",
        "birth_date",
        "grade",
        "education_level",
        "cycle",
        "estado",
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
