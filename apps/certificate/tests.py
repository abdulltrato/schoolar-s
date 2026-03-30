from datetime import date
# Usado para datas de exames fictícias.

from rest_framework.test import APIClient
# Cliente de teste do DRF.

from apps.assessment.models import Assessment
# Modelo de avaliação.
from apps.assessment.tests.base import AssessmentTestCaseBase
# Base de testes que prepara fixtures de avaliação.
from apps.certificate.pdf import generate_certificate_pdf
# Função que gera o PDF.
from apps.certificate.services import CertificateError, create_certificate
# Serviço de criação e erro esperado.
from apps.learning.models_courses import Course, CourseModule
# Modelos de curso e módulos.


class CertificateServiceTests(AssessmentTestCaseBase):
    """Testa geração de certificados, registros e endpoint de PDF."""

    def setUp(self):
        """Prepara curso, módulo e vincula aluno antes de cada teste."""
        super().setUp()
        # Cria curso básico para associar ao aluno.
        self.course = Course.objects.create(
            school=self.school,
            title="Curso de Certificação",
            description="Curso transdisciplinar",
            modality="online",
            tenant_id=self.school.tenant_id,
        )
        # Vincula área curricular ao curso.
        self.course.curriculum_areas.add(self.subject.area)
        # Cria módulo ligando curso à disciplina usada nos exames.
        CourseModule.objects.create(
            course=self.course,
            subject=self.subject,
            tenant_id=self.course.tenant_id,
        )
        # Matricula aluno no curso.
        self.student.courses.add(self.course)

    def test_gera_certificado_com_notas_de_exames(self):
        """Gera certificado quando há avaliação de exame válida."""
        # Cria avaliação de exame com nota.
        Assessment.objects.create(
            student=self.student,
            teaching_assignment=self.alocacao,
            period=self.period,
            component=self.componente_exame,
            tipo="exame",
            data=date(2026, 4, 1),
            score=15,
        )

        # Gera certificado e valida registros.
        certificate = create_certificate(student=self.student, course=self.course)
        self.assertEqual(certificate.records.count(), 1)
        record = certificate.records.first()
        self.assertEqual(record.subject, self.subject)
        self.assertEqual(record.exam_type, "exam")

        # PDF deve ser criado corretamente.
        pdf = generate_certificate_pdf(certificate)
        self.assertTrue(pdf.startswith(b"%PDF"))

    def test_falha_sem_exames(self):
        """Deve lançar erro se não houver exames elegíveis."""
        with self.assertRaises(CertificateError):
            create_certificate(student=self.student, course=self.course)

    def test_api_download_pdf(self):
        """Endpoint deve retornar PDF quando certificado existe."""
        # Cria avaliação de exame para habilitar certificado.
        Assessment.objects.create(
            student=self.student,
            teaching_assignment=self.alocacao,
            period=self.period,
            component=self.componente_exame,
            tipo="exame",
            data=date(2026, 4, 1),
            score=18,
        )
        certificate = create_certificate(student=self.student, course=self.course)

        # Cliente autenticado baixa o PDF.
        client = APIClient()
        client.force_authenticate(user=self.teacher.user)
        response = client.get(
            f"/api/v1/certificate/certificates/{certificate.pk}/pdf/",
            **{"HTTP_X_TENANT_ID": self.school.tenant_id},
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.content.startswith(b"%PDF"))
