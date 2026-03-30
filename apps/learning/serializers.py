from rest_framework import serializers
# Base de serializers do DRF.

from core.serializers import TenantAcademicYearField
# Campo custom para aplicar validação de tenant em anos letivos.

from .models import (
    Assignment,
    Course,
    CourseModule,
    CourseOffering,
    Lesson,
    LessonMaterial,
    Submission,
    SubmissionAttachment,
)
# Modelos de ensino.
from apps.curriculum.serializers import CurriculumAreaSerializer
# Serializer de áreas curriculares.
from apps.curriculum.models import CurriculumArea
# Modelo de área curricular.


class CourseModuleSerializer(serializers.ModelSerializer):
    """Serializa módulos de curso exibindo o nome da disciplina."""

    subject_name = serializers.CharField(source="subject.name", read_only=True)

    class Meta:
        model = CourseModule
        fields = "__all__"
        read_only_fields = ("tenant_id",)


class CourseSerializer(serializers.ModelSerializer):
    """Serializa cursos com módulos embutidos e áreas curriculares."""

    school_name = serializers.CharField(source="school.name", read_only=True)
    cycle_model_code = serializers.CharField(source="cycle_model.code", read_only=True)
    cycle_model_name = serializers.CharField(source="cycle_model.name", read_only=True)
    modules = CourseModuleSerializer(many=True, required=False)
    curriculum_areas = CurriculumAreaSerializer(many=True, read_only=True)
    curriculum_area_ids = serializers.PrimaryKeyRelatedField(
        queryset=CurriculumArea.objects.all(), many=True, write_only=True, required=False
    )

    class Meta:
        model = Course
        fields = "__all__"

    def create(self, validated_data):
        modules_data = validated_data.pop("modules", [])
        area_ids = validated_data.pop("curriculum_area_ids", [])
        course = super().create(validated_data)
        course.curriculum_areas.set(area_ids)
        self._save_modules(course, modules_data)
        return course

    def update(self, instance, validated_data):
        modules_data = validated_data.pop("modules", None)
        area_ids = validated_data.pop("curriculum_area_ids", None)
        course = super().update(instance, validated_data)
        if modules_data is not None:
            course.modules.all().delete()
            self._save_modules(course, modules_data)
        if area_ids is not None:
            course.curriculum_areas.set(area_ids)
        return course

    def _save_modules(self, course, modules_data):
        for module in modules_data:
            CourseModule.objects.create(course=course, tenant_id=course.tenant_id, **module)

    def validate(self, data):
        areas = data.get("curriculum_area_ids")
        if not self.instance and not areas:
            raise serializers.ValidationError({"curriculum_area_ids": "Selecione ao menos uma área curricular."})
        if self.instance and areas is not None and not areas:
            raise serializers.ValidationError({"curriculum_area_ids": "Selecione ao menos uma área curricular."})
        return super().validate(data)


class CourseOfferingSerializer(serializers.ModelSerializer):
    """Serializa ofertas de curso com metadados de ano, turma e professor."""

    academic_year = TenantAcademicYearField()
    course_title = serializers.CharField(source="course.title", read_only=True)
    classroom_name = serializers.CharField(source="classroom.name", read_only=True)
    teacher_name = serializers.CharField(source="teacher.name", read_only=True)
    academic_year_code = serializers.CharField(source="academic_year.code", read_only=True)

    class Meta:
        model = CourseOffering
        fields = "__all__"


class LessonSerializer(serializers.ModelSerializer):
    """Serializa aulas, expondo títulos da oferta e turma."""

    offering_title = serializers.CharField(source="offering.course.title", read_only=True)
    nome = serializers.CharField(source="title", read_only=True)
    classroom_name = serializers.CharField(source="offering.classroom.name", read_only=True)

    class Meta:
        model = Lesson
        fields = "__all__"


class LessonMaterialSerializer(serializers.ModelSerializer):
    """Serializa materiais de aula, incluindo IDs relacionados para client-side."""

    lesson_title = serializers.CharField(source="lesson.title", read_only=True)
    lesson_id = serializers.IntegerField(source="lesson.id", read_only=True)
    offering_id = serializers.IntegerField(source="lesson.offering.id", read_only=True)
    course_id = serializers.IntegerField(source="lesson.offering.course.id", read_only=True)
    course_title = serializers.CharField(source="lesson.offering.course.title", read_only=True)
    classroom_id = serializers.IntegerField(source="lesson.offering.classroom.id", read_only=True)
    classroom_name = serializers.CharField(source="lesson.offering.classroom.name", read_only=True)

    def to_internal_value(self, data):
        mutable = data.copy()
        mutable.setdefault("deleted_at", None)
        return super().to_internal_value(mutable)

    class Meta:
        model = LessonMaterial
        fields = "__all__"


class AssignmentSerializer(serializers.ModelSerializer):
    """Serializa tarefas exibindo título do curso da oferta."""

    offering_title = serializers.CharField(source="offering.course.title", read_only=True)

    class Meta:
        model = Assignment
        fields = "__all__"


class SubmissionAttachmentSerializer(serializers.ModelSerializer):
    """Serializa anexos de submissão."""

    class Meta:
        model = SubmissionAttachment
        fields = "__all__"
        read_only_fields = ("tenant_id",)


class SubmissionSerializer(serializers.ModelSerializer):
    """Serializa submissões com anexos embutidos e nomes legíveis."""

    assignment_title = serializers.CharField(source="assignment.title", read_only=True)
    student_name = serializers.CharField(source="student.name", read_only=True)
    attachments = SubmissionAttachmentSerializer(many=True, required=False)

    def to_internal_value(self, data):
        mutable = data.copy()
        mutable.setdefault("deleted_at", None)
        return super().to_internal_value(mutable)

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
