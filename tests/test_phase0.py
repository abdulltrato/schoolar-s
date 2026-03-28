from datetime import date, timedelta

import pytest
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from django.utils import timezone

from apps.academic.models import Student
from apps.assessment.models import AssessmentPeriod
from apps.curriculum.models import CurriculumArea, Subject, Competency, SubjectCurriculumPlan, SubjectSpecialty
from apps.learning.models import Course, CourseOffering, Assignment, Submission
from apps.school.models import AcademicYear, Grade, Classroom, Teacher, Enrollment, School, GradeSubject


@pytest.mark.django_db
def test_submission_requires_enrollment_when_classroom_present():
    school = School.objects.create(code="ESC-1", name="Escola Central", tenant_id="tenant-esc-1")
    area = CurriculumArea.objects.create(name="Ciencias")
    subject = Subject.objects.create(name="Matematica", area=area, cycle=1)
    specialty = SubjectSpecialty.objects.create(subject=subject, name="Matematica")
    grade = Grade.objects.create(number=1, cycle=1)
    academic_year = AcademicYear.objects.create(
        code="2026-2027",
        tenant_id=school.tenant_id,
        start_date=date(2026, 1, 1),
        end_date=date(2026, 12, 31),
        active=True,
    )
    teacher_user = User.objects.create_user(username="prof1", password="pass123")
    teacher = Teacher.objects.create(user=teacher_user, name="Prof. Maria", school=school, specialty_subject=specialty)
    classroom = Classroom.objects.create(
        name="Turma A",
        school=school,
        grade=grade,
        cycle=1,
        academic_year=academic_year,
        lead_teacher=teacher,
    )

    student = Student.objects.create(
        name="Joao Silva",
        birth_date=date(2010, 5, 15),
        grade=1,
        cycle=1,
        estado="active",
        tenant_id=school.tenant_id,
    )
    Enrollment.objects.create(student=student, classroom=classroom)

    other_student = Student.objects.create(
        name="Ana Paulo",
        birth_date=date(2011, 3, 10),
        grade=1,
        cycle=1,
        estado="active",
        tenant_id=school.tenant_id,
    )

    course = Course.objects.create(
        school=school,
        title="Matematica Basica",
        modality="online",
    )
    offering = CourseOffering.objects.create(
        course=course,
        classroom=classroom,
        teacher=teacher,
        academic_year=academic_year,
        start_date=date(2026, 2, 1),
        end_date=date(2026, 6, 30),
    )
    assignment = Assignment.objects.create(
        offering=offering,
        title="Tarefa 1",
        opens_at=timezone.now(),
        due_at=timezone.now() + timedelta(days=7),
    )

    Submission.objects.create(
        assignment=assignment,
        student=student,
        status="submitted",
    )

    with pytest.raises(ValidationError):
        Submission.objects.create(
            assignment=assignment,
            student=other_student,
            status="submitted",
        )


@pytest.mark.django_db
def test_assessment_period_within_academic_year_and_no_overlap():
    academic_year = AcademicYear.objects.create(
        code="2026-2027",
        tenant_id="tenant-esc-2",
        start_date=date(2026, 1, 1),
        end_date=date(2026, 12, 31),
        active=True,
    )

    with pytest.raises(ValidationError):
        AssessmentPeriod.objects.create(
            academic_year=academic_year,
            name="Periodo 1",
            order=1,
            start_date=date(2025, 12, 1),
            end_date=date(2026, 2, 1),
        )

    AssessmentPeriod.objects.create(
        academic_year=academic_year,
        name="Periodo 1",
        order=1,
        start_date=date(2026, 2, 1),
        end_date=date(2026, 3, 1),
    )

    with pytest.raises(ValidationError):
        AssessmentPeriod.objects.create(
            academic_year=academic_year,
            name="Periodo 2",
            order=2,
            start_date=date(2026, 2, 15),
            end_date=date(2026, 3, 15),
        )


@pytest.mark.django_db
def test_subject_curriculum_plan_validates_competencies_by_subject():
    area = CurriculumArea.objects.create(name="Ciencias Naturais")
    subject_a = Subject.objects.create(name="Matematica", area=area, cycle=1)
    subject_b = Subject.objects.create(name="Historia", area=area, cycle=1)

    grade = Grade.objects.create(number=1, cycle=1)
    academic_year = AcademicYear.objects.create(
        code="2026-2027",
        tenant_id="tenant-esc-3",
        start_date=date(2026, 1, 1),
        end_date=date(2026, 12, 31),
        active=True,
    )
    grade_subject = GradeSubject.objects.create(
        academic_year=academic_year,
        grade=grade,
        subject=subject_a,
        weekly_workload=4,
    )

    competency_ok = Competency.objects.create(
        name="Resolver problemas",
        description="Competencia de matematica",
        area="scientific_technological_knowledge",
        cycle=1,
        subject=subject_a,
        grade=grade,
    )
    competency_wrong = Competency.objects.create(
        name="Historia local",
        description="Competencia de historia",
        area="scientific_technological_knowledge",
        cycle=1,
        subject=subject_b,
    )

    plan = SubjectCurriculumPlan.objects.create(grade_subject=grade_subject)
    plan.planned_competencies.add(competency_ok)

    with pytest.raises(ValidationError):
        plan.planned_competencies.add(competency_wrong)


@pytest.mark.django_db
def test_course_offering_requires_school_alignment():
    school_a = School.objects.create(code="ESC-A", name="Escola A", tenant_id="tenant-esc-a")
    school_b = School.objects.create(code="ESC-B", name="Escola B", tenant_id="tenant-esc-b")
    grade = Grade.objects.create(number=1, cycle=1)
    academic_year = AcademicYear.objects.create(
        code="2026-2027",
        tenant_id=school_b.tenant_id,
        start_date=date(2026, 1, 1),
        end_date=date(2026, 12, 31),
        active=True,
    )
    classroom = Classroom.objects.create(
        name="Turma B",
        school=school_b,
        grade=grade,
        cycle=1,
        academic_year=academic_year,
    )
    course = Course.objects.create(
        school=school_a,
        title="Fisica",
        modality="online",
    )

    with pytest.raises(ValidationError):
        CourseOffering.objects.create(
            course=course,
            classroom=classroom,
            academic_year=academic_year,
            start_date=date(2026, 2, 1),
            end_date=date(2026, 3, 1),
        )
