import datetime

import pytest
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils import timezone

from apps.learning.models import Course, CourseOffering, Lesson
from apps.school.models import AcademicYear, Classroom, School, Teacher
from apps.curriculum.models import CurriculumArea, Subject, SubjectSpecialty
from apps.assessment.models import Assessment


def make_school(tenant="T-1"):
    return School.objects.create(code=f"S-{tenant}", name=f"School {tenant}", tenant_id=tenant)


def make_academic_year(tenant="T-1", start_year=2025):
    return AcademicYear.objects.create(
        code=f"{start_year}-{start_year + 1}",
        start_date=datetime.date(start_year, 1, 1),
        end_date=datetime.date(start_year, 12, 31),
        tenant_id=tenant,
    )


def make_grade(school, number=1):
    from apps.school.models import Grade

    cycle = Grade.cycle_for_grade(number)
    return Grade.objects.create(
        number=number,
        cycle=cycle,
        code=f"G-{number}",
        name=f"Classe {number}",
        tenant_id=school.tenant_id,
    )


def make_specialty(school, cycle):
    area = CurriculumArea.objects.create(code=f"CAR-{school.tenant_id}", name="Ciências", tenant_id=school.tenant_id)
    subject = Subject.objects.create(
        code=f"SUB-{school.tenant_id}",
        name="Matemática",
        area=area,
        cycle=cycle,
        tenant_id=school.tenant_id,
    )
    return SubjectSpecialty.objects.create(
        code=f"SSP-{school.tenant_id}",
        name="Matemática Geral",
        subject=subject,
        tenant_id=school.tenant_id,
    )


def make_classroom(school, grade, academic_year):
    return Classroom.objects.create(
        code="CR-1",
        name="Turma 1",
        tenant_id=school.tenant_id,
        school=school,
        grade=grade,
        academic_year=academic_year,
        cycle=grade.cycle,
    )


def make_teacher(school):
    User = get_user_model()
    user = User.objects.create_user(username=f"user-{school.tenant_id}", password="pass1234")
    specialty = make_specialty(school, cycle=1)
    return Teacher.objects.create(
        code=f"T-{school.tenant_id}",
        name="Prof A",
        user=user,
        school=school,
        tenant_id=school.tenant_id,
        specialty=specialty,
    )


def make_course(school):
    return Course.objects.create(
        code="CRS-1",
        title="Course 1",
        school=school,
        modality="online",
        tenant_id=school.tenant_id,
    )


def make_offering(course, classroom=None, teacher=None, start=None, end=None, academic_year=None):
    return CourseOffering.objects.create(
        code="OFF-1",
        course=course,
        classroom=classroom,
        teacher=teacher,
        academic_year=academic_year or make_academic_year(course.tenant_id, start_year=2026),
        start_date=start or datetime.date(2025, 2, 1),
        end_date=end or datetime.date(2025, 3, 1),
        tenant_id=course.tenant_id,
    )


def make_lesson(offering, when=None, duration=60):
    return Lesson.objects.create(
        code="LES-1",
        offering=offering,
        title="Lesson",
        scheduled_at=when or timezone.datetime(2025, 2, 10, 10, 0, tzinfo=timezone.utc),
        duration_minutes=duration,
        tenant_id=offering.tenant_id,
    )


@pytest.mark.django_db
def test_offering_conflict_same_classroom_same_period_raises():
    school = make_school("T-CLS")
    grade = make_grade(school, number=11)
    academic_year = make_academic_year(school.tenant_id)
    classroom = make_classroom(school, grade, academic_year)
    course = make_course(school)
    teacher = make_teacher(school)
    make_offering(course, classroom=classroom, teacher=teacher)

    with pytest.raises(ValidationError):
        make_offering(
            course,
            classroom=classroom,
            teacher=teacher,
            start=datetime.date(2025, 2, 15),
            end=datetime.date(2025, 3, 15),
        )


@pytest.mark.django_db
def test_lesson_conflict_same_teacher_same_time_raises():
    school = make_school("T-LSN")
    grade = make_grade(school, number=12)
    academic_year = make_academic_year(school.tenant_id)
    classroom = make_classroom(school, grade, academic_year)
    course = make_course(school)
    teacher = make_teacher(school)
    offering = make_offering(course, classroom=classroom, teacher=teacher)

    base = datetime.datetime(2025, 2, 10, 10, 0, tzinfo=datetime.timezone.utc)
    make_lesson(offering, when=base, duration=60)

    with pytest.raises(ValidationError):
        make_lesson(offering, when=base + datetime.timedelta(minutes=30), duration=45)


@pytest.mark.django_db
def test_lesson_no_conflict_with_gap_succeeds():
    school = make_school("T-GAP")
    grade = make_grade(school, number=10)
    academic_year = make_academic_year(school.tenant_id)
    classroom = make_classroom(school, grade, academic_year)
    course = make_course(school)
    teacher = make_teacher(school)
    offering = make_offering(course, classroom=classroom, teacher=teacher)

    base = datetime.datetime(2025, 2, 10, 10, 0, tzinfo=datetime.timezone.utc)
    make_lesson(offering, when=base, duration=60)

    # Adjacent but not overlapping
    lesson = make_lesson(offering, when=base + datetime.timedelta(minutes=60), duration=45)
    assert lesson.pk is not None


@pytest.mark.django_db
def test_assessment_conflict_same_teaching_assignment_same_date_raises():
    school = make_school("T-ASM")
    grade = make_grade(school, number=9)
    academic_year = make_academic_year(school.tenant_id, start_year=2026)
    classroom = make_classroom(school, grade, academic_year)
    course = make_course(school)
    teacher = make_teacher(school)
    offering = make_offering(
        course,
        classroom=classroom,
        teacher=teacher,
        academic_year=academic_year,
        start=datetime.date(2026, 1, 15),
        end=datetime.date(2026, 3, 15),
    )

    # TeachingAssignment is linked via offering; create a minimal TA
    from apps.school.models import GradeSubject, TeachingAssignment

    grade_subject = GradeSubject.objects.create(
        code="GS-1",
        grade=grade,
        subject=teacher.specialty.subject,
        academic_year=academic_year,
        tenant_id=school.tenant_id,
    )
    teaching_assignment = TeachingAssignment.objects.create(
        code="TA-1",
        classroom=classroom,
        grade_subject=grade_subject,
        teacher=teacher,
        tenant_id=school.tenant_id,
    )

    from apps.academic.models import Student

    student = Student.objects.create(
        code="STD-1",
        name="Aluno 1",
        tenant_id=school.tenant_id,
        grade=grade.number,
        cycle=grade.cycle,
        birth_date=datetime.date(2012, 6, 15),
        identification_document=SimpleUploadedFile("id.pdf", b"pdf"),
    )
    # Matricular aluno na turma para satisfazer validação
    from apps.school.models import Enrollment

    Enrollment.objects.create(
        code="ENR-1",
        student=student,
        classroom=classroom,
        tenant_id=school.tenant_id,
    )

    Assessment.objects.create(
        code="ASM-1",
        student=student,
        teaching_assignment=teaching_assignment,
        period=None,
        component=None,
        type="test",
        date=datetime.date(2026, 2, 10),
        tenant_id=school.tenant_id,
    )

    with pytest.raises(ValidationError):
        Assessment.objects.create(
            code="ASM-2",
            student=student,
            teaching_assignment=teaching_assignment,
            period=None,
            component=None,
            type="test",
            date=datetime.date(2026, 2, 10),
            tenant_id=school.tenant_id,
        )
