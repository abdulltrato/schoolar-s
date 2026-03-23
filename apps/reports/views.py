from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from core.viewsets import RobustModelViewSet

from .models import Report
from .serializers import ReportGenerationSerializer, ReportSerializer
from .services import ReportGenerationService


class ReportViewSet(RobustModelViewSet):
    queryset = Report.objects.select_related("student").all()
    serializer_class = ReportSerializer
    search_fields = ("title", "type", "period", "student__name")
    ordering_fields = ("id", "title", "type", "period", "generated_at")
    ordering = ("-generated_at",)
    audit_resource = "report"
    http_method_names = ["get", "post", "head", "options"]

    def create(self, request, *args, **kwargs):
        return Response(
            {
                "detail": "A emissão manual de relatórios está desativada. Use o endpoint de geração assinado.",
            },
            status=status.HTTP_405_METHOD_NOT_ALLOWED,
        )

    @action(detail=False, methods=["get"])
    def catalog(self, request):
        return Response({"results": ReportGenerationService.get_catalog()})

    @action(detail=False, methods=["post"])
    def generate(self, request):
        serializer = ReportGenerationSerializer(data=request.data)
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
        )

        if not validated.get("persist", True):
            return Response(payload, status=status.HTTP_200_OK)

        title = validated.get("title") or payload.get("title") or service.default_title_for(validated["report_kind"], payload)
        report = Report.objects.create(
            title=title,
            type=service.report_type_for(validated["report_kind"]),
            period=service.default_period_for(payload),
            content=payload,
            student=validated.get("student") if validated["report_kind"] in service.STUDENT_KINDS else None,
        )
        data = self.get_serializer(report).data
        return Response(data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=["get"], permission_classes=[AllowAny])
    def verify(self, request):
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
