from django.http import HttpResponse
from rest_framework.decorators import action

from core.viewsets import RobustModelViewSet

from .models import Certificate
from .pdf import generate_certificate_pdf
from .serializers import CertificateSerializer


class CertificateViewSet(RobustModelViewSet):
    queryset = Certificate.objects.select_related("student", "course").prefetch_related("records__subject").order_by("-issued_at")
    serializer_class = CertificateSerializer
    ordering_fields = ("id", "issued_at", "student__name", "course__title")
    search_fields = ("student__name", "course__title", "status")
    allowed_roles = {
        "*": {"national_admin", "provincial_admin", "district_admin", "school_director", "teacher"},
        "list": {"national_admin", "provincial_admin", "district_admin", "school_director", "teacher", "guardian", "student"},
        "retrieve": {"national_admin", "provincial_admin", "district_admin", "school_director", "teacher", "guardian", "student"},
    }

    @action(detail=True, methods=["get"], url_path="pdf")
    def download_pdf(self, request, pk=None):
        certificate = self.get_object()
        pdf_bytes = generate_certificate_pdf(certificate)
        filename = "certificado.pdf"
        response = HttpResponse(pdf_bytes, content_type="application/pdf")
        response["Content-Disposition"] = f'attachment; filename="{filename}"'
        return response
