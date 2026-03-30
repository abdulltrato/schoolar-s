from django.http import HttpResponse
# Respostas HTTP diretas para exportação.
from rest_framework import status
# Códigos HTTP.
from rest_framework.decorators import action
# Decorador para actions customizadas.
from rest_framework.permissions import AllowAny
# Permissão aberta no endpoint de verificação.
from rest_framework.response import Response
# Respostas DRF.

from core.viewsets import RobustModelViewSet
# ViewSet base robusta.

from .models import Report
# Modelo de relatório.
from .serializers import ReportGenerationSerializer, ReportSerializer
# Serializers de leitura e geração.
from .services import ReportGenerationService, render_report_html, render_report_pdf
# Serviços de geração e renderização.


class ReportViewSet(RobustModelViewSet):
    """CRUD de relatórios + geração/validação/exportação."""
    queryset = Report.objects.select_related("student").all()
    serializer_class = ReportSerializer
    search_fields = ("title", "type", "period", "student__name")
    ordering_fields = ("id", "title", "type", "period", "generated_at")
    ordering = ("-generated_at",)
    audit_resource = "report"
    http_method_names = ["get", "post", "head", "options"]

    def create(self, request, *args, **kwargs):
        """Desabilita criação direta; deve usar action generate."""
        return Response(
            {
                "detail": "A emissão manual de relatórios está desativada. Use o endpoint de geração assinado.",
            },
            status=status.HTTP_405_METHOD_NOT_ALLOWED,
        )

    @action(detail=False, methods=["get"])
    def catalog(self, request):
        """Lista catálogo de tipos de relatório disponíveis."""
        return Response({"results": ReportGenerationService.get_catalog()})

    @action(detail=False, methods=["post"])
    def generate(self, request):
        """Gera relatório a partir de parâmetros validados; opcionalmente persiste."""
        serializer = ReportGenerationSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        validated = serializer.validated_data

        service = ReportGenerationService(user=request.user)
        payload = service.generate(
            report_kind=validated["report_kind"],
            student=validated.get("student"),
            academic_year=validated.get("academic_year"),
            grade=validated.get("grade"),
            classroom=validated.get("classroom"),
            period_scope=validated.get("period_scope"),
            period_order=validated.get("period_order"),
            emit_alerts=validated.get("emit_alerts", False),
        )

        if not validated.get("persist", True):
            return Response(payload, status=status.HTTP_200_OK)

        title = validated.get("title") or payload.get("title") or service.default_title_for(validated["report_kind"], payload)
        tenant_id = ""
        if validated.get("student") is not None:
            tenant_id = getattr(validated["student"], "tenant_id", "") or ""
        if not tenant_id:
            profile = getattr(request.user, "school_profile", None)
            tenant_id = getattr(profile, "tenant_id", "") if profile else ""
        report = Report.objects.create(
            title=title,
            type=service.report_type_for(validated["report_kind"]),
            period=service.default_period_for(payload),
            content=payload,
            student=validated.get("student") if validated["report_kind"] in service.STUDENT_KINDS else None,
            tenant_id=tenant_id,
        )
        data = self.get_serializer(report).data
        return Response(data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=["get"], permission_classes=[AllowAny])
    def verify(self, request):
        """Endpoint público para verificar assinatura de um relatório."""
        verification_code = (request.query_params.get("code") or "").strip()
        provided_hash = (request.query_params.get("hash") or "").strip()

        if not verification_code:
            return Response(
                {
                    "valid": False,
                    "reason": "Código de verificação em falta.",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        report = Report.objects.select_related("student").filter(verification_code=verification_code).first()
        if report is None:
            return Response(
                {
                    "valid": False,
                    "reason": "Documento não encontrado para o código indicado.",
                    "verification_code": verification_code,
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        valid = report.verify_integrity(provided_hash=provided_hash or None)
        return Response(
            {
                "valid": valid,
                "reason": "Documento autêntico." if valid else "A assinatura não confere com o documento emitido.",
                "verification_code": report.verification_code,
                "verification_hash": report.verification_hash,
                "report_id": report.id,
                "title": report.title,
                "type": report.type,
                "period": report.period,
                "generated_at": report.generated_at,
                "student_name": getattr(report.student, "name", None),
                "verification_version": report.verification_version,
            },
            status=status.HTTP_200_OK if valid else status.HTTP_409_CONFLICT,
        )

    @action(detail=True, methods=["get"])
    def export(self, request, pk=None):
        """Exporta relatório em HTML inline ou PDF para download."""
        report = self.get_object()
        export_format = (request.query_params.get("export_format") or "html").strip().lower()
        safe_serial = (report.serial_number or f"report-{report.pk}").replace("/", "-")

        if export_format == "pdf":
            response = HttpResponse(render_report_pdf(report), content_type="application/pdf")
            response["Content-Disposition"] = f'attachment; filename="{safe_serial}.pdf"'
            return response

        html_content = render_report_html(report)
        response = HttpResponse(html_content, content_type="text/html; charset=utf-8")
        response["Content-Disposition"] = f'inline; filename="{safe_serial}.html"'
        return response
