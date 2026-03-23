from rest_framework import serializers

from core.serializers import TenantAcademicYearField

from .models import Assignment, Course, CourseOffering, Lesson, LessonMaterial, Submission


class CourseSerializer(serializers.ModelSerializer):
    school_name = serializers.CharField(source="school.name", read_only=True)

    class Meta:
        model = Course
        fields = "__all__"


class CourseOfferingSerializer(serializers.ModelSerializer):
    academic_year = TenantAcademicYearField()
    course_title = serializers.CharField(source="course.title", read_only=True)
    classroom_name = serializers.CharField(source="classroom.name", read_only=True)
    teacher_name = serializers.CharField(source="teacher.name", read_only=True)
    academic_year_code = serializers.CharField(source="academic_year.code", read_only=True)

    class Meta:
        model = CourseOffering
        fields = "__all__"


class LessonSerializer(serializers.ModelSerializer):
    offering_title = serializers.CharField(source="offering.course.title", read_only=True)

    class Meta:
        model = Lesson
        fields = "__all__"


class LessonMaterialSerializer(serializers.ModelSerializer):
    lesson_title = serializers.CharField(source="lesson.title", read_only=True)

    class Meta:
        model = LessonMaterial
        fields = "__all__"


class AssignmentSerializer(serializers.ModelSerializer):
    offering_title = serializers.CharField(source="offering.course.title", read_only=True)

    class Meta:
        model = Assignment
        fields = "__all__"


class SubmissionSerializer(serializers.ModelSerializer):
    assignment_title = serializers.CharField(source="assignment.title", read_only=True)
    student_name = serializers.CharField(source="student.name", read_only=True)

    class Meta:
        model = Submission
        fields = "__all__"
