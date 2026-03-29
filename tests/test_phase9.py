from datetime import date

import pytest
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile

from decimal import Decimal

from apps.academic.models import Student, StudentOutcome
from apps.curriculum.models import CurriculumArea, LearningOutcome, Subject, SubjectSpecialty
from apps.reports.services import ReportGenerationService
from apps.school.models import AcademicYear, AuditAlert, Classroom, Enrollment, Grade, School, Teacher


@pytest.mark.django_db
def test_learning_intervention_emits_audit_alerts():
    tenant_id = "tenant-alerts"
    school = School.objects.create(code="ESC-A", name="Escola Alertas", tenant_id=tenant_id)
    academic_year = AcademicYear.objects.create(
        code="2026-2027",
        tenant_id=tenant_id,
        start_date=date(2026, 1, 1),
        end_date=date(2027, 1, 1),
        active=True,
    )
    grade = Grade.objects.create(number=3, cycle=1, name="")
    area = CurriculumArea.objects.create(name="Humanidades")
    subject = Subject.objects.create(name="Historia", area=area, cycle=grade.cycle)
    specialty = SubjectSpecialty.objects.create(subject=subject, name="Historia")

    user = get_user_model().objects.create_user(username="director_alerts", password="pass1234")
    profile = user.school_profile
    profile.role = "school_director"
    profile.school = school
    profile.tenant_id = tenant_id
    profile.save(update_fields=["role", "school", "tenant_id"])

    teacher = Teacher.objects.create(user=user, school=school, name="Prof. A", tenant_id=tenant_id, specialty_subject=specialty)
    classroom = Classroom.objects.create(
        name="3A",
        tenant_id=tenant_id,
        school=school,
        grade=grade,
        cycle=grade.cycle,
        academic_year=academic_year,
        lead_teacher=teacher,
    )

    student = Student.objects.create(
        name="Aluno Alerta",
        tenant_id=tenant_id,
        birth_date=date(2015, 1, 1),
        grade=grade.number,
        cycle=grade.cycle,
        estado="active",
        identification_document=SimpleUploadedFile("id.pdf", b"pdf"),
    )
    Enrollment.objects.create(student=student, classroom=classroom, tenant_id=tenant_id)

    outcome = LearningOutcome.objects.create(
        tenant_id=tenant_id,
        code="LO-HIS-01",
        description="Identificar eventos basicos.",
        subject=subject,
        grade=grade,
        cycle=grade.cycle,
        taxonomy_level="remember",
        knowledge_dimension="factual",
        active=True,
    )
    StudentOutcome.objects.create(
        student=student,
        outcome=outcome,
        tenant_id=tenant_id,
        mastery_level=Decimal("0.2"),
        status="not_started",
        evidence_count=0,
    )

    service = ReportGenerationService(user=user)
    service.generate(
        report_kind="learning_intervention_plan",
        academic_year=academic_year,
        grade=grade,
        emit_alerts=True,
    )

    assert AuditAlert.objects.filter(alert_type="learning_risk_tier3").count() == 1

    service.generate(
        report_kind="learning_intervention_plan",
        academic_year=academic_year,
        grade=grade,
        emit_alerts=True,
    )

    assert AuditAlert.objects.filter(alert_type="learning_risk_tier3").count() == 1
