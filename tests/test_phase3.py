from datetime import date

import pytest
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile

from apps.academic.models import Student, StudentOutcome
from apps.curriculum.models import Competency, CompetencyOutcome, CurriculumArea, LearningOutcome, Subject
from apps.school.models import AcademicYear, Grade, School


@pytest.mark.django_db
def test_learning_outcome_validates_cycle_alignment():
    grade = Grade.objects.create(number=4, cycle=2, name="")
    area = CurriculumArea.objects.create(name="Ciencias Exatas")
    subject = Subject.objects.create(name="Matematica", area=area, cycle=1)

    outcome = LearningOutcome(
        tenant_id="tenant-a",
        code="LO-MAT-01",
        description="Resolver problemas simples.",
        subject=subject,
        grade=grade,
        cycle=1,
        taxonomy_level="apply",
        knowledge_dimension="procedural",
    )

    with pytest.raises(ValidationError):
        outcome.full_clean()


@pytest.mark.django_db
def test_competency_outcome_infers_tenant():
    school = School.objects.create(code="ESC-01", name="Escola Primaria Central", tenant_id="tenant-esc-01")
    AcademicYear.objects.create(
        code="2026-2027",
        tenant_id=school.tenant_id,
        start_date=date(2026, 1, 1),
        end_date=date(2027, 1, 1),
        active=True,
    )
    grade = Grade.objects.create(number=1, cycle=1, name="")
    area = CurriculumArea.objects.create(name="Ciencias Naturais")
    subject = Subject.objects.create(name="Ciencias", area=area, cycle=1)
    competency = Competency.objects.create(name="Compreender conceitos basicos", area="language_communication", cycle=1, subject=subject, grade=grade)

    outcome = LearningOutcome.objects.create(
        tenant_id=school.tenant_id,
        code="LO-CIE-01",
        description="Explicar conceitos basicos.",
        subject=subject,
        grade=grade,
        cycle=1,
        taxonomy_level="understand",
        knowledge_dimension="conceptual",
    )

    link = CompetencyOutcome.objects.create(
        outcome=outcome,
        competency=competency,
        weight=60,
    )

    assert link.tenant_id == school.tenant_id


@pytest.mark.django_db
def test_student_outcome_requires_matching_tenant():
    school = School.objects.create(code="ESC-02", name="Escola Secundaria", tenant_id="tenant-esc-02")
    student = Student.objects.create(
        name="Aluno A",
        tenant_id=school.tenant_id,
        birth_date=date(2012, 1, 1),
        grade=5,
        cycle=1,
        estado="active",
        identification_document=SimpleUploadedFile("id.pdf", b"pdf"),
    )
    grade = Grade.objects.create(number=5, cycle=2, name="")
    outcome = LearningOutcome.objects.create(
        tenant_id="tenant-other",
        code="LO-HIS-01",
        description="Descrever eventos historicos.",
        grade=grade,
        cycle=1,
        taxonomy_level="remember",
        knowledge_dimension="factual",
        active=True,
    )

    with pytest.raises(ValidationError):
        StudentOutcome.objects.create(
            student=student,
            outcome=outcome,
            mastery_level=2.0,
        )
