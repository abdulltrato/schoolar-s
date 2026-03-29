from datetime import date

from rest_framework.test import APIClient

from apps.assessment.models import Assessment
from apps.assessment.tests.base import AssessmentTestCaseBase
from apps.certificate.pdf import generate_certificate_pdf
from apps.certificate.services import CertificateError, create_certificate
from apps.learning.models_courses import Course, CourseModule


class CertificateServiceTests(AssessmentTestCaseBase):
    def setUp(self):
        super().setUp()
        self.course = Course.objects.create(
            school=self.school,
            title="Curso de Certificação",
            description="Curso transdisciplinar",
            modality="online",
            tenant_id=self.school.tenant_id,
        )
        self.course.curriculum_areas.add(self.subject.area)
        CourseModule.objects.create(
            course=self.course,
            subject=self.subject,
            tenant_id=self.course.tenant_id,
        )
        self.student.courses.add(self.course)

    def test_gera_certificado_com_notas_de_exames(self):
        Assessment.objects.create(
            student=self.student,
            teaching_assignment=self.alocacao,
            period=self.period,
            component=self.componente_exame,
            tipo="exame",
            data=date(2026, 4, 1),
            score=15,
        )

        certificate = create_certificate(student=self.student, course=self.course)
        self.assertEqual(certificate.records.count(), 1)
        record = certificate.records.first()
        self.assertEqual(record.subject, self.subject)
        self.assertEqual(record.exam_type, "exam")

        pdf = generate_certificate_pdf(certificate)
        self.assertTrue(pdf.startswith(b"%PDF"))

    def test_falha_sem_exames(self):
        with self.assertRaises(CertificateError):
            create_certificate(student=self.student, course=self.course)

    def test_api_download_pdf(self):
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

        client = APIClient()
        client.force_authenticate(user=self.teacher.user)
        response = client.get(
            f"/api/v1/certificate/certificates/{certificate.pk}/pdf/",
            **{"HTTP_X_TENANT_ID": self.school.tenant_id},
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.content.startswith(b"%PDF"))
