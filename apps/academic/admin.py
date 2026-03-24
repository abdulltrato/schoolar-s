from django import forms
from django.contrib import admin

from .models import Student, StudentCompetency


class StudentAdminForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = "__all__"

    def __init__(self, *args, request=None, **kwargs):
        self.request = request
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        tenant_id = self._resolve_tenant_id(cleaned_data)
        if tenant_id:
            self.instance.tenant_id = tenant_id
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
class AlunoAdmin(admin.ModelAdmin):
    form = StudentAdminForm
    list_display = ("name", "grade", "education_level", "cycle", "estado")
    list_filter = ("cycle", "estado", "grade")
    search_fields = ("name",)
    readonly_fields = ("education_level", "cycle",)
    fields = ("name", "birth_date", "grade", "education_level", "cycle", "estado")

    def get_form(self, request, obj=None, change=False, **kwargs):
        form_class = super().get_form(request, obj, change=change, **kwargs)

        class RequestAwareStudentAdminForm(form_class):
            def __init__(self, *args, **inner_kwargs):
                inner_kwargs["request"] = request
                super().__init__(*args, **inner_kwargs)

        return RequestAwareStudentAdminForm

    @admin.display(description="Nível de Ensino")
    def education_level(self, obj):
        if not obj or not obj.grade:
            return "-"
        return obj.education_level.title()


admin.site.register(StudentCompetency)
