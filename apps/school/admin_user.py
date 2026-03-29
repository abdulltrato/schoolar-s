from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as DefaultUserAdmin

from .models import UserProfile


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    fk_name = "user"
    can_delete = False
    extra = 0
    readonly_fields = ("tenant_id",)
    fields = ("tenant_id", "role", "school", "province", "district", "active")

    def has_add_permission(self, request, obj=None):
        if obj is None:
            return False
        try:
            getattr(obj, "school_profile")
            return False
        except Exception:
            return True


UserModel = get_user_model()
admin.site.unregister(UserModel)


@admin.register(UserModel)
class TenantUserAdmin(DefaultUserAdmin):
    inlines = [UserProfileInline]
    list_display = DefaultUserAdmin.list_display + ("tenant_id",)
    list_select_related = ("school_profile",)

    def get_inline_instances(self, request, obj=None):
        if obj is None:
            return []
        return super().get_inline_instances(request, obj=obj)

    def tenant_id(self, obj):
        return getattr(getattr(obj, "school_profile", None), "tenant_id", "")

    tenant_id.short_description = "Tenant"

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        profile, _ = UserProfile.objects.get_or_create(user=obj)
        if request.user and hasattr(request.user, "school_profile"):
            profile_tenant = (request.user.school_profile.tenant_id or "").strip()
            if profile_tenant and profile.tenant_id != profile_tenant:
                profile.tenant_id = profile_tenant
        if not profile.tenant_id:
            profile.tenant_id = (
                getattr(request.user, "school_profile", None) and request.user.school_profile.tenant_id
            ) or profile.tenant_id
        profile.save()
