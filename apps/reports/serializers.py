from rest_framework import serializers
from rest_framework.reverse import reverse

from apps.academic.models import Student
from apps.school.models import AcademicYear, Classroom, Grade
from core.serializers import TenantAcademicYearField

from .models import Report


class ReportSerializer(serializers.ModelSerializer):
    titulo = serializers.CharField(source="title", write_only=True, required=False)
    tipo = serializers.CharField(source="type", write_only=True, required=False)
    conteudo = serializers.JSONField(source="content", write_only=True, required=False)
    verification_url = serializers.SerializerMethodField()
    verification_status = serializers.SerializerMethodField()

    class Meta:
        model = Report
        fields = "__all__"
        read_only_fields = ("serial_number", "verification_code", "verification_hash", "verification_version", "verification_url", "verification_status")

    def get_verification_url(self, obj):
        request = self.context.get("request")
        path = reverse("report-verify", request=request)
        if request is None:
            return f"{path}?code={obj.verification_code}&hash={obj.verification_hash}"
        return request.build_absolute_uri(f"{path}?code={obj.verification_code}&hash={obj.verification_hash}")

    def get_verification_status(self, obj):
        return "valid" if obj.verify_integrity() else "invalid"


class ReportGenerationSerializer(serializers.Serializer):
    REPORT_KIND_CHOICES = [
        ("student_declaration", "Declaração do estudante"),
        ("student_certificate", "Certificado do estudante"),
        ("student_diploma", "Diploma do estudante"),
        ("student_progress_report", "Relatório de aproveitamento do estudante"),
        ("school_statistics", "Relatório estatístico da escola"),
        ("quarterly_grade_sheet", "Pauta trimestral"),
        ("semester_grade_sheet", "Pauta semestral"),
        ("annual_grade_sheet", "Pauta anual"),
        ("students_list", "Lista de estudantes"),
        ("teachers_list", "Lista de professores"),
        ("directors_list", "Lista de diretores e coordenadores"),
        ("students_by_grade_year", "Lista de estudantes por classe e ano"),
        ("students_by_grade_year_classroom", "Lista de estudantes por classe, ano e turma"),
        ("bloom_distribution", "Distribuição por Taxonomia de Bloom"),
        ("learning_risk_alerts", "Alertas de risco de aprendizagem"),
        ("learning_intervention_plan", "Plano de intervenção pedagógica"),
    ]
    PERIOD_SCOPE_CHOICES = [
        ("quarterly", "Trimestral"),
        ("semester", "Semestral"),
        ("annual", "Anual"),
    ]

    report_kind = serializers.ChoiceField(choices=REPORT_KIND_CHOICES)
    student = serializers.PrimaryKeyRelatedField(queryset=Student.objects.all(), required=False, allow_null=True)
    academic_year = TenantAcademicYearField(queryset=AcademicYear.objects.all(), required=False, allow_null=True)
    grade = serializers.PrimaryKeyRelatedField(queryset=Grade.objects.all(), required=False, allow_null=True)
    classroom = serializers.PrimaryKeyRelatedField(queryset=Classroom.objects.select_related("academic_year", "grade"), required=False, allow_null=True)
    period_scope = serializers.ChoiceField(choices=PERIOD_SCOPE_CHOICES, required=False, allow_null=True)
    period_order = serializers.IntegerField(required=False, allow_null=True, min_value=1, max_value=4)
    persist = serializers.BooleanField(required=False, default=True)
    title = serializers.CharField(required=False, allow_blank=True, max_length=200)
    emit_alerts = serializers.BooleanField(required=False, default=False)

    def validate(self, attrs):
        request = self.context.get("request")
        profile = getattr(getattr(request, "user", None), "school_profile", None) if request else None
        tenant_id = getattr(request, "tenant_id", None)
        if not tenant_id and profile and profile.role not in {"national_admin", "provincial_admin", "district_admin"}:
            tenant_id = (profile.tenant_id or "").strip() or None

        report_kind = attrs["report_kind"]
        student = attrs.get("student")
        academic_year = attrs.get("academic_year")
        grade = attrs.get("grade")
        classroom = attrs.get("classroom")
        period_scope = attrs.get("period_scope")

        student_required = {
            "student_declaration",
            "student_certificate",
            "student_diploma",
            "student_progress_report",
        }
        grade_sheet_kinds = {
            "quarterly_grade_sheet",
            "semester_grade_sheet",
            "annual_grade_sheet",
        }

        if report_kind in student_required and not student:
            raise serializers.ValidationError({"student": "Este documento exige um estudante."})

        if report_kind in grade_sheet_kinds and not academic_year:
            raise serializers.ValidationError({"academic_year": "A pauta exige um ano letivo."})

        if report_kind in grade_sheet_kinds and not (grade or classroom):
            raise serializers.ValidationError({"classroom": "A pauta exige pelo menos uma classe ou uma turma."})

        if report_kind == "students_by_grade_year":
            if not academic_year:
                raise serializers.ValidationError({"academic_year": "Este relatório exige um ano letivo."})
            if not grade:
                raise serializers.ValidationError({"grade": "Este relatório exige uma classe."})

        if report_kind == "students_by_grade_year_classroom":
            if not academic_year:
                raise serializers.ValidationError({"academic_year": "Este relatório exige um ano letivo."})
            if not classroom:
                raise serializers.ValidationError({"classroom": "Este relatório exige uma turma."})

        if report_kind == "bloom_distribution":
            if not academic_year:
                raise serializers.ValidationError({"academic_year": "Este relatório exige um ano letivo."})

        if report_kind == "learning_risk_alerts":
            if not academic_year:
                raise serializers.ValidationError({"academic_year": "Este relatório exige um ano letivo."})

        if report_kind == "learning_intervention_plan":
            if not academic_year:
                raise serializers.ValidationError({"academic_year": "Este relatório exige um ano letivo."})
            if "emit_alerts" not in self.initial_data:
                attrs["emit_alerts"] = True

        if classroom and academic_year and classroom.academic_year_id != academic_year.id:
            raise serializers.ValidationError({"classroom": "A turma deve pertencer ao ano letivo selecionado."})

        if classroom and grade and classroom.grade_id != grade.id:
            raise serializers.ValidationError({"classroom": "A turma deve pertencer à classe selecionada."})

        if report_kind == "quarterly_grade_sheet" and period_scope and period_scope != "quarterly":
            raise serializers.ValidationError({"period_scope": "A pauta trimestral usa escopo trimestral."})

        if report_kind == "semester_grade_sheet" and period_scope and period_scope != "semester":
            raise serializers.ValidationError({"period_scope": "A pauta semestral usa escopo semestral."})

        if report_kind == "annual_grade_sheet" and period_scope and period_scope != "annual":
            raise serializers.ValidationError({"period_scope": "A pauta anual usa escopo anual."})

        if tenant_id:
            if student and (student.tenant_id or "").strip() != tenant_id:
                raise serializers.ValidationError({"student": "O estudante deve pertencer ao mesmo tenant."})
            if academic_year and (academic_year.tenant_id or "").strip() != tenant_id:
                raise serializers.ValidationError({"academic_year": "O ano letivo deve pertencer ao mesmo tenant."})
            if classroom and (classroom.tenant_id or "").strip() != tenant_id:
                raise serializers.ValidationError({"classroom": "A turma deve pertencer ao mesmo tenant."})

        return attrs
