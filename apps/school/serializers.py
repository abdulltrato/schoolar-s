from rest_framework import serializers

from core.serializers import TenantAcademicYearField

from .models import (
    AcademicYear,
    AuditAlert,
    AuditEvent,
    Announcement,
    AttendanceRecord,
    Classroom,
    Enrollment,
    Grade,
    GradeSubject,
    Invoice,
    ManagementAssignment,
    Payment,
    School,
    Teacher,
    TeachingAssignment,
    UserProfile,
)


class AcademicYearSerializer(serializers.ModelSerializer):
    class Meta:
        model = AcademicYear
        fields = "__all__"


class AuditEventSerializer(serializers.ModelSerializer):
    tenant_name = serializers.CharField(read_only=True)

    class Meta:
        model = AuditEvent
        fields = "__all__"
        read_only_fields = ("tenant_name",)


class AuditAlertSerializer(serializers.ModelSerializer):
    tenant_name = serializers.CharField(read_only=True)

    class Meta:
        model = AuditAlert
        fields = "__all__"
        read_only_fields = ("tenant_name",)


class GradeSerializer(serializers.ModelSerializer):
    education_level = serializers.CharField(read_only=True)
    cycle_model_code = serializers.CharField(source="cycle_model.code", read_only=True)
    cycle_model_name = serializers.CharField(source="cycle_model.name", read_only=True)

    class Meta:
        model = Grade
        fields = [
            "id",
            "code",
            "number",
            "cycle",
            "cycle_model",
            "cycle_model_code",
            "cycle_model_name",
            "education_level",
            "name",
            "created_at",
            "updated_at",
            "deleted_at",
        ]


class SchoolSerializer(serializers.ModelSerializer):
    class Meta:
        model = School
        fields = "__all__"


class TeacherSerializer(serializers.ModelSerializer):
    school_name = serializers.CharField(source="school.name", read_only=True)

    class Meta:
        model = Teacher
        fields = "__all__"


class ClassroomSerializer(serializers.ModelSerializer):
    grade = serializers.SlugRelatedField(slug_field="number", queryset=Grade.objects.all())
    academic_year = TenantAcademicYearField(queryset=AcademicYear.objects.all())
    grade_name = serializers.CharField(source="grade.name", read_only=True)
    school_name = serializers.CharField(source="school.name", read_only=True)
    lead_teacher_name = serializers.CharField(source="lead_teacher.name", read_only=True)
    academic_year_code = serializers.CharField(source="academic_year.code", read_only=True)
    education_track = serializers.SerializerMethodField()
    cycle_model_code = serializers.CharField(source="cycle_model.code", read_only=True)
    cycle_model_name = serializers.CharField(source="cycle_model.name", read_only=True)

    @staticmethod
    def get_education_track(obj):
        if obj.grade_id and obj.grade.number:
            return "technical" if obj.grade.number > 12 else "general"
        return None

    class Meta:
        model = Classroom
        fields = "__all__"


class GradeSubjectSerializer(serializers.ModelSerializer):
    academic_year = TenantAcademicYearField(queryset=AcademicYear.objects.all())
    grade = serializers.SlugRelatedField(slug_field="number", queryset=Grade.objects.all())
    subject_name = serializers.CharField(source="subject.name", read_only=True)
    academic_year_code = serializers.CharField(source="academic_year.code", read_only=True)

    class Meta:
        model = GradeSubject
        fields = "__all__"


class TeachingAssignmentSerializer(serializers.ModelSerializer):
    teacher_name = serializers.CharField(source="teacher.name", read_only=True)
    classroom_name = serializers.CharField(source="classroom.name", read_only=True)
    school_name = serializers.CharField(source="classroom.school.name", read_only=True)
    subject_name = serializers.CharField(source="grade_subject.subject.name", read_only=True)
    academic_year_code = serializers.CharField(source="grade_subject.academic_year.code", read_only=True)
    grade_number = serializers.IntegerField(source="grade_subject.grade.number", read_only=True)

    class Meta:
        model = TeachingAssignment
        fields = "__all__"


class EnrollmentSummarySerializer(serializers.ModelSerializer):
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
            # Prefer the explicit classroom name; fall back to the grade name.
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
        else:  # technical_professional
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
    student_name = serializers.CharField(source="student.name", read_only=True)
    classroom_name = serializers.CharField(source="classroom.name", read_only=True)
    school_name = serializers.CharField(source="classroom.school.name", read_only=True)
    academic_year_code = serializers.CharField(source="classroom.academic_year.code", read_only=True)
    grade_number = serializers.IntegerField(source="classroom.grade.number", read_only=True)

    class Meta:
        model = Enrollment
        fields = "__all__"


class ManagementAssignmentSerializer(serializers.ModelSerializer):
    academic_year = TenantAcademicYearField(queryset=AcademicYear.objects.all())
    teacher_name = serializers.CharField(source="teacher.name", read_only=True)
    school_name = serializers.CharField(source="school.name", read_only=True)
    academic_year_code = serializers.CharField(source="academic_year.code", read_only=True)
    grade_number = serializers.IntegerField(source="grade.number", read_only=True)
    classroom_name = serializers.CharField(source="classroom.name", read_only=True)

    class Meta:
        model = ManagementAssignment
        fields = "__all__"


class UserProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="user.username", read_only=True)
    school_name = serializers.CharField(source="school.name", read_only=True)

    class Meta:
        model = UserProfile
        fields = "__all__"


class AttendanceRecordSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source="enrollment.student.name", read_only=True)
    classroom_name = serializers.CharField(source="enrollment.classroom.name", read_only=True)

    class Meta:
        model = AttendanceRecord
        fields = "__all__"


class AnnouncementSerializer(serializers.ModelSerializer):
    school_name = serializers.CharField(source="school.name", read_only=True)
    classroom_name = serializers.CharField(source="classroom.name", read_only=True)
    author_name = serializers.CharField(source="author.username", read_only=True)

    class Meta:
        model = Announcement
        fields = "__all__"


class InvoiceSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source="student.name", read_only=True)
    school_name = serializers.CharField(source="school.name", read_only=True)

    class Meta:
        model = Invoice
        fields = "__all__"


class PaymentSerializer(serializers.ModelSerializer):
    invoice_reference = serializers.CharField(source="invoice.reference", read_only=True)

    class Meta:
        model = Payment
        fields = "__all__"
