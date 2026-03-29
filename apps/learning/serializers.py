from rest_framework import serializers

from core.serializers import TenantAcademicYearField

from .models import (
    Assignment,
    Course,
    CourseOffering,
    Lesson,
    LessonMaterial,
    Submission,
    SubmissionAttachment,
)


class CourseSerializer(serializers.ModelSerializer):
    school_name = serializers.CharField(source="school.name", read_only=True)
    cycle_model_code = serializers.CharField(source="cycle_model.code", read_only=True)
    cycle_model_name = serializers.CharField(source="cycle_model.name", read_only=True)

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


class SubmissionAttachmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubmissionAttachment
        fields = "__all__"
        read_only_fields = ("tenant_id",)


class SubmissionSerializer(serializers.ModelSerializer):
    assignment_title = serializers.CharField(source="assignment.title", read_only=True)
    student_name = serializers.CharField(source="student.name", read_only=True)
    attachments = SubmissionAttachmentSerializer(many=True, required=False)

    class Meta:
        model = Submission
        fields = "__all__"

    def create(self, validated_data):
        attachments_data = validated_data.pop("attachments", [])
        submission = super().create(validated_data)
        self._save_attachments(submission, attachments_data)
        return submission

    def update(self, instance, validated_data):
        attachments_data = validated_data.pop("attachments", None)
        submission = super().update(instance, validated_data)
        if attachments_data is not None:
            submission.attachments.all().delete()
            self._save_attachments(submission, attachments_data)
        return submission

    def _save_attachments(self, submission, attachments_data):
        for item in attachments_data:
            SubmissionAttachment.objects.create(submission=submission, tenant_id=submission.tenant_id, **item)
