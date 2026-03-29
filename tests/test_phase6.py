from datetime import date

import pytest
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile

from apps.assessment.models import Assessment, AssessmentComponent, AssessmentOutcomeMap, AssessmentPeriod
from apps.curriculum.models import CurriculumArea, LearningOutcome, Subject, SubjectSpecialty
from apps.reports.services import ReportGenerationService
from apps.school.models import AcademicYear, Classroom, Enrollment, Grade, GradeSubject, School, Teacher, TeachingAssignment
from apps.academic.models import Student


@pytest.mark.django_db
def test_bloom_distribution_report_counts():
    tenant_id = "tenant-bloom"
    school = School.objects.create(code="ESC-B", name="Escola Bloom", tenant_id=tenant_id)
    academic_year = AcademicYear.objects.create(
        code="2026-2027",
        tenant_id=tenant_id,
        start_date=date(2026, 1, 1),
        end_date=date(2027, 1, 1),
        active=True,
    )
    grade = Grade.objects.create(number=4, cycle=2, name="")
    area = CurriculumArea.objects.create(name="Linguagens")
    subject = Subject.objects.create(name="Portugues", area=area, cycle=2)
    specialty = SubjectSpecialty.objects.create(subject=subject, name="Portugues")
    grade_subject = GradeSubject.objects.create(
        academic_year=academic_year,
        grade=grade,
        subject=subject,
        weekly_workload=4,
        tenant_id=tenant_id,
    )

    user = get_user_model().objects.create_user(username="director_bloom", password="pass1234")
    profile = user.school_profile
    profile.role = "school_director"
    profile.school = school
    profile.tenant_id = tenant_id
    profile.save(update_fields=["role", "school", "tenant_id"])
    teacher = Teacher.objects.create(user=user, school=school, name="Prof. Bloom", tenant_id=tenant_id, specialty_subject=specialty)
    classroom = Classroom.objects.create(
        name="4A",
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
        name="Aluno Bloom",
        tenant_id=tenant_id,
        birth_date=date(2012, 1, 1),
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

    outcome_remember = LearningOutcome.objects.create(
        tenant_id=tenant_id,
        code="LO-PT-01",
        description="Recordar conceitos.",
        subject=subject,
        grade=grade,
        cycle=2,
        taxonomy_level="remember",
        knowledge_dimension="factual",
        active=True,
    )
    outcome_understand = LearningOutcome.objects.create(
        tenant_id=tenant_id,
        code="LO-PT-02",
        description="Compreender textos.",
        subject=subject,
        grade=grade,
        cycle=2,
        taxonomy_level="understand",
        knowledge_dimension="conceptual",
        active=True,
    )

    AssessmentOutcomeMap.objects.create(
        component=component,
        outcome=outcome_remember,
        tenant_id=tenant_id,
        weight=60,
        active=True,
    )
    AssessmentOutcomeMap.objects.create(
        component=component,
        outcome=outcome_understand,
        tenant_id=tenant_id,
        weight=40,
        active=True,
    )

    Assessment.objects.create(
        student=student,
        teaching_assignment=teaching_assignment,
        period=period,
        component=component,
        type="test",
        date=date(2026, 3, 12),
        score=14,
    )

    payload = ReportGenerationService(user=user).generate(
        report_kind="bloom_distribution",
        academic_year=academic_year,
        grade=grade,
    )

    assert payload["summary"]["total_outcomes"] == 2
    taxonomy = {item["level"]: item for item in payload["summary"]["taxonomy_levels"]}
    assert taxonomy["remember"]["total"] == 1
    assert taxonomy["understand"]["total"] == 1
