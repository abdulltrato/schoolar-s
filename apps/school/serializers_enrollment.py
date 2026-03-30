from rest_framework import serializers
# Base de serializers do DRF.

from .models import Enrollment
# Modelo de matrícula.


class EnrollmentSummarySerializer(serializers.ModelSerializer):
    """Serializer compacto para listagens, com campos derivados legíveis."""

    student_name = serializers.CharField(source="student.name", read_only=True)
    enrollment_year = serializers.SerializerMethodField()
    course = serializers.SerializerMethodField()
    duration_days = serializers.SerializerMethodField()
    education_track = serializers.SerializerMethodField()
    cycle_band = serializers.SerializerMethodField()

    @staticmethod
    def _academic_year(obj):
        if obj.classroom_id and obj.classroom.academic_year_id:
            return obj.classroom.academic_year
        return None

    def get_enrollment_year(self, obj):
        academic_year = self._academic_year(obj)
        if academic_year and academic_year.code:
            return academic_year.code
        return obj.enrollment_date.year if obj.enrollment_date else None

    def get_course(self, obj):
        if obj.classroom_id:
            if obj.classroom.name:
                return obj.classroom.name
            if obj.classroom.grade_id and obj.classroom.grade.name:
                return obj.classroom.grade.name
        return None

    def get_duration_days(self, obj):
        academic_year = self._academic_year(obj)
        if academic_year and academic_year.start_date and academic_year.end_date:
            return (academic_year.end_date - academic_year.start_date).days
        return None

    @staticmethod
    def _track_and_band(obj):
        if not (obj.classroom_id and obj.classroom.grade_id):
            return None, None
        number = obj.classroom.grade.number
        track = "technical_professional" if number and number > 12 else ("primary" if number <= 6 else "secondary")

        if track == "primary":
            band = "primary_cycle_1" if number <= 3 else "primary_cycle_2"
        elif track == "secondary":
            band = "secondary_cycle_1" if number <= 9 else "secondary_cycle_2"
        else:
            if number <= 15:
                band = "technical_basic"
            elif number <= 18:
                band = "technical_medium"
            else:
                band = "technical_superior"
        return track, band

    def get_education_track(self, obj):
        track, _ = self._track_and_band(obj)
        return track

    def get_cycle_band(self, obj):
        _, band = self._track_and_band(obj)
        return band

    class Meta:
        model = Enrollment
        fields = [
            "id",
            "student_name",
            "enrollment_year",
            "course",
            "duration_days",
            "education_track",
            "cycle_band",
        ]


class EnrollmentSerializer(serializers.ModelSerializer):
    """Serializer completo de matrícula, incluindo planos de pagamento calculados."""

    student_name = serializers.CharField(source="student.name", read_only=True)
    classroom_name = serializers.CharField(source="classroom.name", read_only=True)
    school_name = serializers.CharField(source="classroom.school.name", read_only=True)
    academic_year_code = serializers.CharField(source="classroom.academic_year.code", read_only=True)
    grade_number = serializers.IntegerField(source="classroom.grade.number", read_only=True)
    payment_plans = serializers.SerializerMethodField(read_only=True)

    def get_payment_plans(self, obj):
        plans = getattr(obj, "payment_plans", None)
        if plans is None:
            return []
        return [
            {
                "id": plan.id,
                "type": plan.type,
                "type_label": plan.get_type_display(),
                "amount": str(plan.amount),
                "status": plan.status,
                "status_label": plan.get_status_display(),
                "due_date": plan.due_date,
                "invoice_id": plan.invoice_id,
            }
            for plan in plans.all().order_by("due_date", "type")
        ]

    class Meta:
        model = Enrollment
        fields = "__all__"
        read_only_fields = ("exam_fee", "exam_recurrence_fee", "exam_special_fee")

    def validate(self, attrs):
        # Bloqueia alteração/inclusão de taxas de exame via payload de matrícula.
        attrs.pop("exam_fee", None)
        attrs.pop("exam_recurrence_fee", None)
        attrs.pop("exam_special_fee", None)
        return super().validate(attrs)
