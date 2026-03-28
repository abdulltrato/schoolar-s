from datetime import date

import pytest
from django.contrib.auth import get_user_model
from django.core.management import call_command

from apps.academic.models import Student, StudentOutcome
from apps.assessment.models import Assessment, AssessmentComponent, AssessmentOutcomeMap, AssessmentPeriod
from apps.curriculum.models import CurriculumArea, LearningOutcome, Subject, SubjectSpecialty
from apps.school.models import AcademicYear, Classroom, Enrollment, Grade, GradeSubject, School, Teacher, TeachingAssignment


def _seed_context(tenant_id="tenant-z"):
    school = School.objects.create(code="ESC-Z", name="Escola Z", tenant_id=tenant_id)
    academic_year = AcademicYear.objects.create(
        code="2026-2027",
        tenant_id=tenant_id,
        start_date=date(2026, 1, 1),
        end_date=date(2027, 1, 1),
        active=True,
    )
    grade = Grade.objects.create(number=2, cycle=1, name="")
    area = CurriculumArea.objects.create(name="Humanidades")
    subject = Subject.objects.create(name="Historia", area=area, cycle=1)
    specialty = SubjectSpecialty.objects.create(subject=subject, name="Historia")
    grade_subject = GradeSubject.objects.create(
        academic_year=academic_year,
        grade=grade,
        subject=subject,
        weekly_workload=3,
        tenant_id=tenant_id,
    )

    user = get_user_model().objects.create_user(username="teacher_z", password="pass1234")
    teacher = Teacher.objects.create(user=user, school=school, name="Prof. Z", tenant_id=tenant_id, specialty_subject=specialty)
    classroom = Classroom.objects.create(
        name="2B",
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
        name="Aluno Z",
        tenant_id=tenant_id,
        birth_date=date(2016, 1, 1),
        grade=grade.number,
        cycle=grade.cycle,
        estado="active",
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
        code="LO-HIS-01",
        description="Descrever eventos locais.",
        subject=subject,
        grade=grade,
        cycle=1,
        taxonomy_level="remember",
        knowledge_dimension="factual",
        active=True,
    )
    AssessmentOutcomeMap.objects.create(
        component=component,
        outcome=outcome,
        tenant_id=tenant_id,
        weight=100,
        active=True,
    )

    Assessment.objects.create(
        student=student,
        teaching_assignment=teaching_assignment,
        period=period,
        component=component,
        type="test",
        date=date(2026, 3, 15),
        score=12,
    )

    return student, outcome


@pytest.mark.django_db
def test_recalculate_student_outcomes_command():
    student, outcome = _seed_context()
    StudentOutcome.objects.filter(student=student, outcome=outcome).update(
        mastery_level=0,
        status="not_started",
        evidence_count=0,
    )

    call_command("recalculate_student_outcomes", student_id=student.id)

    refreshed = StudentOutcome.objects.get(student=student, outcome=outcome)
    assert float(refreshed.mastery_level) > 0
