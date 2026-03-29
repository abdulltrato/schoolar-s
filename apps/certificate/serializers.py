from rest_framework import serializers

from apps.certificate.services import CertificateError, create_certificate
from .models import Certificate, CertificateExamRecord


class CertificateExamRecordSerializer(serializers.ModelSerializer):
    subject_name = serializers.CharField(source="subject.name", read_only=True)

    class Meta:
        model = CertificateExamRecord
        fields = "__all__"


class CertificateSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source="student.name", read_only=True)
    course_title = serializers.CharField(source="course.title", read_only=True)
    records = CertificateExamRecordSerializer(many=True, read_only=True)

    class Meta:
        model = Certificate
        fields = "__all__"

    def create(self, validated_data):
        try:
            return create_certificate(
                student=validated_data["student"],
                course=validated_data["course"],
                notes=validated_data.get("notes", ""),
            )
        except CertificateError as exc:
            raise serializers.ValidationError({"detail": str(exc)})
