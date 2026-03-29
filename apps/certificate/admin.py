from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html

from core.admin_utils import TenantAwareAdmin

from .models import Certificate, CertificateExamRecord


class CertificateExamRecordInline(admin.TabularInline):
    model = CertificateExamRecord
    extra = 0
    readonly_fields = ("subject", "exam_type", "score", "exam_date", "assessment")
    can_delete = False


@admin.register(Certificate)
class CertificateAdmin(TenantAwareAdmin):
    list_filter = ("status", "course")
    search_fields = ("student__name", "course__title", "status")
    readonly_fields = ("issued_at",)
    inlines = [CertificateExamRecordInline]
    list_display_links = ("student", "course")
    def pdf_link(self, obj):
        if obj.status != "issued":
            return "Não emitido"
        url = reverse("certificate-certificate-pdf", args=[obj.pk])
        return format_html('<a href="{}" target="_blank">Download PDF</a>', url)
    pdf_link.short_description = "PDF seguro"
    list_display = ("student", "course", "status", "issued_at", "pdf_link")


@admin.register(CertificateExamRecord)
class CertificateExamRecordAdmin(TenantAwareAdmin):
    list_display = ("certificate", "subject", "exam_type", "score", "exam_date")
    search_fields = ("certificate__student__name", "subject__name", "exam_type")
