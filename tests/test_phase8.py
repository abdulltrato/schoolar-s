from datetime import date

import pytest
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile

from apps.academic.models import Student, StudentOutcome
from apps.curriculum.models import CurriculumArea, LearningOutcome, Subject, SubjectSpecialty
from apps.reports.services import ReportGenerationService
from apps.school.models import AcademicYear, Classroom, Enrollment, Grade, School, Teacher


@pytest.mark.django_db
def test_learning_intervention_plan_report():
    tenant_id = "tenant-intervention"
    school = School.objects.create(code="ESC-I", name="Escola Intervencao", tenant_id=tenant_id)
    academic_year = AcademicYear.objects.create(
        code="2026-2027",
        tenant_id=tenant_id,
        start_date=date(2026, 1, 1),
        end_date=date(2027, 1, 1),
        active=True,
    )
    grade = Grade.objects.create(number=5, cycle=1, name="")
    area = CurriculumArea.objects.create(name="Matematica")
    subject = Subject.objects.create(name="Matematica", area=area, cycle=grade.cycle)
    specialty = SubjectSpecialty.objects.create(subject=subject, name="Matematica")

    user = get_user_model().objects.create_user(username="director_intervention", password="pass1234")
    profile = user.school_profile
    profile.role = "school_director"
    profile.school = school
    profile.tenant_id = tenant_id
    profile.save(update_fields=["role", "school", "tenant_id"])

    teacher = Teacher.objects.create(user=user, school=school, name="Prof. I", tenant_id=tenant_id, specialty_subject=specialty)
    classroom = Classroom.objects.create(
        name="5B",
        tenant_id=tenant_id,
        school=school,
        grade=grade,
        cycle=grade.cycle,
        academic_year=academic_year,
        lead_teacher=teacher,
    )

    student = Student.objects.create(
        name="Aluno Intervencao",
        tenant_id=tenant_id,
        birth_date=date(2014, 1, 1),
        grade=grade.number,
        cycle=grade.cycle,
        estado="active",
        identification_document=SimpleUploadedFile("id.pdf", b"pdf"),
    )
    Enrollment.objects.create(student=student, classroom=classroom, tenant_id=tenant_id)

    outcome = LearningOutcome.objects.create(
        tenant_id=tenant_id,
        code="LO-MAT-01",
        description="Resolver operacoes basicas.",
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
        mastery_level=0.5,
        status="not_started",
        evidence_count=0,
    )

    payload = ReportGenerationService(user=user).generate(
        report_kind="learning_intervention_plan",
        academic_year=academic_year,
        grade=grade,
    )

    assert payload["summary"]["students_count"] == 1
    assert payload["summary"]["tiers"]["tier3"] == 1
    assert payload["rows"][0]["tier"] == "tier3"
    assert payload["rows"][0]["recommendations"]
