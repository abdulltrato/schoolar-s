from datetime import date

import pytest
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile

from apps.academic.models import Student, StudentOutcome
from apps.assessment.models import Assessment, AssessmentComponent, AssessmentOutcomeMap, AssessmentPeriod
from apps.curriculum.models import CurriculumArea, LearningOutcome, Subject, SubjectSpecialty
from apps.school.models import AcademicYear, Classroom, Enrollment, Grade, GradeSubject, School, Teacher, TeachingAssignment


def _build_assessment_context(*, tenant_id="tenant-x"):
    school = School.objects.create(code="ESC-CTX", name="Escola Contexto", tenant_id=tenant_id)
    academic_year = AcademicYear.objects.create(
        code="2026-2027",
        tenant_id=tenant_id,
        start_date=date(2026, 1, 1),
        end_date=date(2027, 1, 1),
        active=True,
    )
    grade = Grade.objects.create(number=3, cycle=1, name="")
    area = CurriculumArea.objects.create(name="Linguagens")
    subject = Subject.objects.create(name="Portugues", area=area, cycle=1)
    specialty = SubjectSpecialty.objects.create(subject=subject, name="Portugues")
    grade_subject = GradeSubject.objects.create(
        academic_year=academic_year,
        grade=grade,
        subject=subject,
        weekly_workload=4,
        tenant_id=tenant_id,
    )

    user = get_user_model().objects.create_user(username="teacher_ctx", password="pass1234")
    teacher = Teacher.objects.create(user=user, school=school, name="Prof. Ana", tenant_id=tenant_id, specialty_subject=specialty)

    classroom = Classroom.objects.create(
        name="3A",
        tenant_id=tenant_id,
        school=school,
        grade=grade,
        cycle=grade.cycle,
        academic_year=academic_year,
        lead_teacher=teacher,
    )
    teaching_assignment = TeachingAssignment.objects.create(
        teacher=teacher,
        classroom=classroom,
        grade_subject=grade_subject,
        tenant_id=tenant_id,
    )

    student = Student.objects.create(
        name="Aluno 1",
        tenant_id=tenant_id,
        birth_date=date(2015, 1, 1),
        grade=grade.number,
        cycle=grade.cycle,
        estado="active",
        identification_document=SimpleUploadedFile("id.pdf", b"pdf"),
    )
    Enrollment.objects.create(student=student, classroom=classroom, tenant_id=tenant_id)

    period = AssessmentPeriod.objects.create(
        academic_year=academic_year,
        tenant_id=tenant_id,
        name="1º Trimestre",
        order=1,
        start_date=date(2026, 2, 1),
        end_date=date(2026, 4, 30),
        active=True,
    )
    component = AssessmentComponent.objects.create(
        period=period,
        grade_subject=grade_subject,
        tenant_id=tenant_id,
        type="test",
        name="Teste 1",
        weight=50,
        max_score=20,
        mandatory=True,
    )

    outcome = LearningOutcome.objects.create(
        tenant_id=tenant_id,
        code="LO-PT-01",
        description="Interpretar textos simples.",
        subject=subject,
        grade=grade,
        cycle=1,
        taxonomy_level="understand",
        knowledge_dimension="conceptual",
        active=True,
    )

    return student, teaching_assignment, period, component, outcome


@pytest.mark.django_db
def test_assessment_outcome_map_weight_cap():
    _, _, _, component, outcome = _build_assessment_context()
    AssessmentOutcomeMap.objects.create(
        component=component,
        outcome=outcome,
        tenant_id=component.tenant_id,
        weight=80,
        active=True,
    )

    second_outcome = LearningOutcome.objects.create(
        tenant_id=component.tenant_id,
        code="LO-PT-02",
        description="Identificar ideias principais.",
        subject=outcome.subject,
        grade=outcome.grade,
        cycle=1,
        taxonomy_level="remember",
        knowledge_dimension="factual",
        active=True,
    )

    map_over = AssessmentOutcomeMap(
        component=component,
        outcome=second_outcome,
        tenant_id=component.tenant_id,
        weight=30,
        active=True,
    )

    with pytest.raises(ValidationError):
        map_over.full_clean()


@pytest.mark.django_db
def test_assessment_updates_student_outcome_mastery():
    student, teaching_assignment, period, component, outcome = _build_assessment_context()
    AssessmentOutcomeMap.objects.create(
        component=component,
        outcome=outcome,
        tenant_id=component.tenant_id,
        weight=100,
        active=True,
    )

    Assessment.objects.create(
        student=student,
        teaching_assignment=teaching_assignment,
        period=period,
        component=component,
        type="test",
        date=date(2026, 3, 10),
        score=16,
    )

    result = StudentOutcome.objects.get(student=student, outcome=outcome)
    assert float(result.mastery_level) == 4.0
    assert result.status == "proficient"
