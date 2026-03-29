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

    class Meta:
        model = Grade
        fields = [
            "id",
            "code",
            "number",
            "cycle",
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
