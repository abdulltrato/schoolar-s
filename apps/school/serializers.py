from rest_framework import serializers

from .models import (
    AcademicYear,
    Classroom,
    Enrollment,
    Grade,
    GradeSubject,
    ManagementAssignment,
    School,
    Teacher,
    TeachingAssignment,
)


class AcademicYearSerializer(serializers.ModelSerializer):
    class Meta:
        model = AcademicYear
        fields = "__all__"


class GradeSerializer(serializers.ModelSerializer):
    education_level = serializers.CharField(read_only=True)

    class Meta:
        model = Grade
        fields = ["id", "number", "cycle", "education_level", "name"]


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
    academic_year = serializers.SlugRelatedField(slug_field="code", queryset=AcademicYear.objects.all())
    grade_name = serializers.CharField(source="grade.name", read_only=True)
    school_name = serializers.CharField(source="school.name", read_only=True)
    lead_teacher_name = serializers.CharField(source="lead_teacher.name", read_only=True)

    class Meta:
        model = Classroom
        fields = "__all__"


class GradeSubjectSerializer(serializers.ModelSerializer):
    academic_year = serializers.SlugRelatedField(slug_field="code", queryset=AcademicYear.objects.all())
    grade = serializers.SlugRelatedField(slug_field="number", queryset=Grade.objects.all())
    subject_name = serializers.CharField(source="subject.name", read_only=True)

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
    teacher_name = serializers.CharField(source="teacher.name", read_only=True)
    school_name = serializers.CharField(source="school.name", read_only=True)
    academic_year_code = serializers.CharField(source="academic_year.code", read_only=True)
    grade_number = serializers.IntegerField(source="grade.number", read_only=True)
    classroom_name = serializers.CharField(source="classroom.name", read_only=True)

    class Meta:
        model = ManagementAssignment
        fields = "__all__"
