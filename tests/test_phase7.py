from datetime import date

import pytest
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile

from apps.academic.models import Student, StudentOutcome
from apps.curriculum.models import CurriculumArea, LearningOutcome, Subject, SubjectSpecialty
from apps.reports.services import ReportGenerationService
from apps.school.models import AcademicYear, Classroom, Enrollment, Grade, School, Teacher, UserProfile


@pytest.mark.django_db
def test_learning_risk_alerts_report():
    tenant_id = "tenant-risk"
    school = School.objects.create(code="ESC-R", name="Escola Risco", tenant_id=tenant_id)
    academic_year = AcademicYear.objects.create(
        code="2026-2027",
        tenant_id=tenant_id,
        start_date=date(2026, 1, 1),
        end_date=date(2027, 1, 1),
        active=True,
    )
    grade = Grade.objects.create(number=6, cycle=1, name="")
    area = CurriculumArea.objects.create(name="Ciencias")
    subject = Subject.objects.create(name="Ciencias", area=area, cycle=grade.cycle)
    specialty = SubjectSpecialty.objects.create(subject=subject, name="Ciencias")

    user = get_user_model().objects.create_user(username="director_risk", password="pass1234")
    profile = user.school_profile
    profile.role = "school_director"
    profile.school = school
    profile.tenant_id = tenant_id
    profile.save(update_fields=["role", "school", "tenant_id"])

    teacher = Teacher.objects.create(user=user, school=school, name="Prof. R", tenant_id=tenant_id, specialty_subject=specialty)
    classroom = Classroom.objects.create(
        name="6A",
        tenant_id=tenant_id,
        school=school,
        grade=grade,
        cycle=grade.cycle,
        academic_year=academic_year,
        lead_teacher=teacher,
    )

    student = Student.objects.create(
        name="Aluno Risco",
        tenant_id=tenant_id,
        birth_date=date(2013, 1, 1),
        grade=grade.number,
        cycle=grade.cycle,
        estado="active",
        identification_document=SimpleUploadedFile("id.pdf", b"pdf"),
        previous_certificate=SimpleUploadedFile("cert.pdf", b"pdf"),
    )
    Enrollment.objects.create(student=student, classroom=classroom, tenant_id=tenant_id)

    outcome = LearningOutcome.objects.create(
        tenant_id=tenant_id,
        code="LO-CIE-01",
        description="Explicar fenomenos simples.",
        subject=subject,
        grade=grade,
        cycle=grade.cycle,
        taxonomy_level="understand",
        knowledge_dimension="conceptual",
        active=True,
    )
    outcome2 = LearningOutcome.objects.create(
        tenant_id=tenant_id,
        code="LO-CIE-02",
        description="Aplicar conceitos basicos.",
        subject=subject,
        grade=grade,
        cycle=grade.cycle,
        taxonomy_level="apply",
        knowledge_dimension="procedural",
        active=True,
    )

    StudentOutcome.objects.create(
        student=student,
        outcome=outcome,
        tenant_id=tenant_id,
        mastery_level=1.5,
        status="developing",
        evidence_count=1,
    )
    StudentOutcome.objects.create(
        student=student,
        outcome=outcome2,
        tenant_id=tenant_id,
        mastery_level=3.5,
        status="proficient",
        evidence_count=1,
    )

    payload = ReportGenerationService(user=user).generate(
        report_kind="learning_risk_alerts",
        academic_year=academic_year,
        grade=grade,
    )

    assert payload["summary"]["students_count"] == 1
    assert payload["summary"]["risk_levels"]["medium"] == 1
    assert payload["rows"][0]["risk_level"] == "medium"
