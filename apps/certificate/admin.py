from django.contrib import admin
# Ferramentas de registro do admin.
from django.urls import reverse
# Resolve URLs nomeadas.
from django.utils.html import format_html
# Permite renderizar link seguro em HTML.

from core.admin_utils import TenantAwareAdmin
# Admin base com escopo por tenant.

from .models import Certificate, CertificateExamRecord
# Modelos administrados.


class CertificateExamRecordInline(admin.TabularInline):
    """Exibe registros de exame diretamente no admin de certificados."""

    # Modelo que será exibido inline.
    model = CertificateExamRecord
    # Não cria linhas extras vazias por padrão.
    extra = 0
    # Campos apenas leitura; edição ocorre via serviço.
    readonly_fields = ("subject", "exam_type", "score", "exam_date", "assessment")
    # Não permite remover registros pelo inline.
    can_delete = False


@admin.register(Certificate)
class CertificateAdmin(TenantAwareAdmin):
    """Admin de certificados com link rápido para PDF seguro."""

    # Filtros laterais.
    list_filter = ("status", "course")
    # Campos pesquisáveis.
    search_fields = ("student__name", "course__title", "status")
    # Campos somente leitura.
    readonly_fields = ("issued_at",)
    # Inline exibindo registros de exame.
    inlines = [CertificateExamRecordInline]
    # Campos que recebem hyperlink para detalhes.
    list_display_links = ("student", "course")

    def pdf_link(self, obj):
        """Gera link para download do PDF, se certificado estiver emitido."""
        if obj.status != "issued":
            return "Não emitido"
        url = reverse("certificate-certificate-pdf", args=[obj.pk])
        return format_html('<a href="{}" target="_blank">Download PDF</a>', url)

    # Título da coluna no admin.
    pdf_link.short_description = "PDF seguro"
    # Colunas visíveis.
    list_display = ("student", "course", "status", "issued_at", "pdf_link")


@admin.register(CertificateExamRecord)
class CertificateExamRecordAdmin(TenantAwareAdmin):
    """Admin para registros de exame associados a certificados."""

    # Colunas exibidas.
    list_display = ("certificate", "subject", "exam_type", "score", "exam_date")
    # Campos de busca.
    search_fields = ("certificate__student__name", "subject__name", "exam_type")
