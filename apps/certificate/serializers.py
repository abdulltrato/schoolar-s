from rest_framework import serializers
# Base de serializers do DRF.

from apps.certificate.services import CertificateError, create_certificate
# Serviço de criação e exceção específica.
from .models import Certificate, CertificateExamRecord
# Modelos serializados.


class CertificateExamRecordSerializer(serializers.ModelSerializer):
    """Serializa registros de exames vinculados a um certificado."""

    # Exibe nome da disciplina apenas para leitura.
    subject_name = serializers.CharField(source="subject.name", read_only=True)

    class Meta:
        # Modelo de origem.
        model = CertificateExamRecord
        # Serializa todos os campos.
        fields = "__all__"


class CertificateSerializer(serializers.ModelSerializer):
    """Serializa certificados incluindo dados derivados e registros de exame."""

    # Nome do aluno para exibição.
    student_name = serializers.CharField(source="student.name", read_only=True)
    # Título do curso concluído.
    course_title = serializers.CharField(source="course.title", read_only=True)
    # Lista de registros de exames, somente leitura.
    records = CertificateExamRecordSerializer(many=True, read_only=True)

    class Meta:
        # Modelo de origem.
        model = Certificate
        # Serializa todos os campos.
        fields = "__all__"

    def create(self, validated_data):
        """Cria certificado via serviço, convertendo erros em ValidationError."""
        try:
            return create_certificate(
                student=validated_data["student"],
                course=validated_data["course"],
                notes=validated_data.get("notes", ""),
            )
        except CertificateError as exc:
            # Converte exceção de domínio em erro de validação DRF.
            raise serializers.ValidationError({"detail": str(exc)})
