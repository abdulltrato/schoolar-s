from django.contrib import admin

from core.admin_utils import TenantAwareAdmin

from .models import Transfer


@admin.register(Transfer)
class TransferAdmin(TenantAwareAdmin):
    actions = ["apply_transfers"]
    list_display = ("code", "kind", "status", "tenant_id", "created_at", "applied_at")
    list_filter = ("kind", "status", "tenant_id")
    search_fields = ("code", "student__name", "teacher__name", "tenant_id")
    readonly_fields = ("code", "tenant_id", "status", "applied_at", "error_message", "created_at", "updated_at", "deleted_at", "usuario")

    fieldsets = (
        (
            "Transferência",
            {
                "fields": (
                    "kind",
                    "student",
                    "teacher",
                    "from_school",
                    "from_classroom",
                    "to_school",
                    "to_classroom",
                    "new_specialty",
                    "move_teaching_assignments",
                    "reason",
                )
            },
        ),
        (
            "Estado",
            {
                "fields": (
                    "status",
                    "applied_at",
                    "error_message",
                )
            },
        ),
        (
            "Auditoria",
            {
                "fields": (
                    "tenant_id",
                    "usuario",
                    "created_at",
                    "updated_at",
                    "deleted_at",
                )
            },
        ),
    )

    def apply_transfers(self, request, queryset):
        applied = 0
        failed = 0
        for transfer in queryset:
            try:
                transfer.apply()
                applied += 1
            except Exception:
                failed += 1
        self.message_user(request, f"Aplicadas: {applied}. Falhas: {failed}.")

    apply_transfers.short_description = "Aplicar transferências selecionadas"
