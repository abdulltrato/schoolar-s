from django.http import HttpResponse
# Utilizado para devolver bytes do PDF.
from rest_framework.decorators import action
# Permite adicionar rota customizada ao viewset.

from core.viewsets import RobustModelViewSet
# Viewset base com tratamento robusto.

from .models import Certificate
# Modelo principal.
from .pdf import generate_certificate_pdf
# Função geradora do PDF.
from .serializers import CertificateSerializer
# Serializer correspondente.


class CertificateViewSet(RobustModelViewSet):
    """Endpoints REST para certificados, incluindo download do PDF."""

    # Queryset padrão com relacionamentos carregados.
    queryset = Certificate.objects.select_related("student", "course").prefetch_related("records__subject").order_by("-issued_at")
    # Serializer usado nas respostas.
    serializer_class = CertificateSerializer
    # Campos permitidos para ordenação via API.
    ordering_fields = ("id", "issued_at", "student__name", "course__title")
    # Campos pesquisáveis.
    search_fields = ("student__name", "course__title", "status")
    # Controle de papéis autorizados.
    allowed_roles = {
        "*": {"national_admin", "provincial_admin", "district_admin", "school_director", "teacher"},
        "list": {"national_admin", "provincial_admin", "district_admin", "school_director", "teacher", "guardian", "student"},
        "retrieve": {"national_admin", "provincial_admin", "district_admin", "school_director", "teacher", "guardian", "student"},
    }

    @action(detail=True, methods=["get"], url_path="pdf")
    def download_pdf(self, request, pk=None):
        """Retorna o PDF seguro do certificado selecionado."""
        # Busca objeto respeitando filtros de tenant.
        certificate = self.get_object()
        # Gera bytes do PDF.
        pdf_bytes = generate_certificate_pdf(certificate)
        filename = "certificado.pdf"
        # Monta resposta HTTP com content-type adequado.
        response = HttpResponse(pdf_bytes, content_type="application/pdf")
        response["Content-Disposition"] = f'attachment; filename="{filename}"'
        return response
