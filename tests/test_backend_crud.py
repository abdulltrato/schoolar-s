from datetime import date, datetime, timedelta
from decimal import Decimal

import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from apps.academic.models import Student
from apps.assessment.models import AssessmentComponent
from apps.curriculum.models import Competency, CurriculumArea, LearningOutcome, Subject
from apps.school.models import AcademicYear, Classroom, Enrollment, Grade, GradeSubject, School, Teacher, TeachingAssignment


@pytest.fixture
def admin_client(db):
    user = get_user_model().objects.create_user(username="admin_smoke", password="pass1234")
    profile = user.school_profile
    profile.role = "national_admin"
    profile.active = True
    profile.save(update_fields=["role", "active"])
    client = APIClient()
    client.force_authenticate(user=user)
    return client


@pytest.fixture
def tenant_header():
    return {"HTTP_X_TENANT_ID": "tenant-smoke"}


@pytest.fixture
def base_data(db, tenant_header):
    tenant_id = tenant_header["HTTP_X_TENANT_ID"]
    school = School.objects.create(code="ESC-SM-01", name="Escola Smoke", tenant_id=tenant_id)
    academic_year = AcademicYear.objects.create(
        code="2026-2027",
        tenant_id=tenant_id,
        start_date=date(2026, 1, 1),
        end_date=date(2027, 1, 1),
        active=True,
    )
    grade = Grade.objects.create(number=1, cycle=1, name="")
    area = CurriculumArea.objects.create(name="Area Smoke")
    subject = Subject.objects.create(name="Disciplina Smoke", area=area, cycle=grade.cycle)
    grade_subject = GradeSubject.objects.create(
        academic_year=academic_year,
        grade=grade,
        subject=subject,
        weekly_workload=4,
        tenant_id=tenant_id,
    )
    teacher_user = get_user_model().objects.create_user(username="teacher_smoke", password="pass1234")
    teacher = Teacher.objects.create(user=teacher_user, school=school, name="Prof. Smoke", tenant_id=tenant_id)
    classroom = Classroom.objects.create(
        name="1A",
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
        name="Aluno Smoke",
        tenant_id=tenant_id,
        birth_date=date(2015, 1, 1),
        grade=grade.number,
        cycle=grade.cycle,
        estado="active",
    )
    enrollment = Enrollment.objects.create(student=student, classroom=classroom, tenant_id=tenant_id)
    competency = Competency.objects.create(
        name="Competencia Smoke",
        area="language_communication",
        cycle=grade.cycle,
        subject=subject,
        grade=grade,
    )
    outcome = LearningOutcome.objects.create(
        tenant_id=tenant_id,
        code="LO-SM-01",
        description="Resultado Smoke",
        subject=subject,
        grade=grade,
        cycle=grade.cycle,
        taxonomy_level="understand",
        knowledge_dimension="conceptual",
        active=True,
    )
    period = AssessmentComponent.objects.create(
        period=AssessmentComponent._meta.get_field("period").related_model.objects.create(
            academic_year=academic_year,
            tenant_id=tenant_id,
            name="Periodo 1",
            order=1,
            start_date=date(2026, 2, 1),
            end_date=date(2026, 4, 30),
            active=True,
        ),
        grade_subject=grade_subject,
        tenant_id=tenant_id,
        type="test",
        name="Componente 1",
        weight=50,
        max_score=20,
        mandatory=True,
    )
    return {
        "tenant_id": tenant_id,
        "school": school,
        "academic_year": academic_year,
        "grade": grade,
        "area": area,
        "subject": subject,
        "grade_subject": grade_subject,
        "teacher": teacher,
        "classroom": classroom,
        "teaching_assignment": teaching_assignment,
        "student": student,
        "enrollment": enrollment,
        "competency": competency,
        "outcome": outcome,
        "component": period,
    }


def _crud(client, url, payload, update_payload, headers):
    create = client.post(url, payload, format="json", **headers)
    assert create.status_code in {200, 201}, create.data
    obj_id = create.data.get("id")
    assert obj_id

    listing = client.get(url, **headers)
    assert listing.status_code == 200

    retrieve = client.get(f"{url}{obj_id}/", **headers)
    assert retrieve.status_code == 200

    update = client.patch(f"{url}{obj_id}/", update_payload, format="json", **headers)
    assert update.status_code in {200, 202}, update.data

    delete = client.delete(f"{url}{obj_id}/", **headers)
    assert delete.status_code in {200, 204}, delete.data if hasattr(delete, "data") else delete.status_code


@pytest.mark.django_db
def test_academic_crud(admin_client, tenant_header, base_data):
    student_payload = {
        "name": "Aluno CRUD",
        "tenant_id": base_data["tenant_id"],
        "birth_date": "2014-02-02",
        "grade": base_data["grade"].number,
        "status": "active",
    }
    _crud(
        admin_client,
        "/api/v1/academic/students/",
        student_payload,
        {"name": "Aluno CRUD Atualizado"},
        tenant_header,
    )

    guardian_payload = {
        "name": "Encarregado CRUD",
        "phone": "841234567",
        "email": "guardian@example.com",
        "relationship": "Pai",
        "active": True,
    }
    _crud(
        admin_client,
        "/api/v1/academic/guardians/",
        guardian_payload,
        {"phone": "841234568"},
        tenant_header,
    )

    guardian = admin_client.post("/api/v1/academic/guardians/", guardian_payload, format="json", **tenant_header).data
    student = admin_client.post("/api/v1/academic/students/", student_payload, format="json", **tenant_header).data

    _crud(
        admin_client,
        "/api/v1/academic/student-guardians/",
        {
            "student": student["id"],
            "guardian": guardian["id"],
            "primary_contact": True,
            "tenant_id": base_data["tenant_id"],
        },
        {"primary_contact": False},
        tenant_header,
    )

    _crud(
        admin_client,
        "/api/v1/academic/student-outcomes/",
        {
            "student": base_data["student"].id,
            "outcome": base_data["outcome"].id,
            "mastery_level": "2.0",
            "status": "developing",
            "evidence_count": 1,
            "tenant_id": base_data["tenant_id"],
        },
        {"mastery_level": "3.0"},
        tenant_header,
    )


@pytest.mark.django_db
def test_curriculum_crud(admin_client, tenant_header, base_data):
    _crud(
        admin_client,
        "/api/v1/curriculum/areas/",
        {"name": "Area CRUD"},
        {"name": "Area CRUD 2"},
        tenant_header,
    )

    area = admin_client.post("/api/v1/curriculum/areas/", {"name": "Area CRUD Sub"}, format="json", **tenant_header).data
    _crud(
        admin_client,
        "/api/v1/curriculum/subjects/",
        {"name": "Disciplina CRUD", "area_id": area["id"], "cycle": base_data["grade"].cycle},
        {"name": "Disciplina CRUD 2"},
        tenant_header,
    )

    subject = admin_client.post(
        "/api/v1/curriculum/subjects/",
        {"name": "Disciplina CRUD Sub", "area_id": area["id"], "cycle": base_data["grade"].cycle},
        format="json",
        **tenant_header,
    ).data

    _crud(
        admin_client,
        "/api/v1/curriculum/competencies/",
        {
            "name": "Competencia CRUD",
            "area": "language_communication",
            "cycle": base_data["grade"].cycle,
            "subject_id": subject["id"],
            "grade": base_data["grade"].id,
        },
        {"name": "Competencia CRUD 2"},
        tenant_header,
    )

    competency = admin_client.post(
        "/api/v1/curriculum/competencies/",
        {
            "name": "Competencia CRUD Sub",
            "area": "language_communication",
            "cycle": base_data["grade"].cycle,
            "subject_id": subject["id"],
            "grade": base_data["grade"].id,
        },
        format="json",
        **tenant_header,
    ).data

    _crud(
        admin_client,
        "/api/v1/curriculum/base-curricula/",
        {"cycle": base_data["grade"].cycle, "competency_ids": [competency["id"]]},
        {"cycle": base_data["grade"].cycle},
        tenant_header,
    )

    _crud(
        admin_client,
        "/api/v1/curriculum/local-curricula/",
        {
            "tenant_id": base_data["tenant_id"],
            "cycle": base_data["grade"].cycle,
            "competency_ids": [competency["id"]],
        },
        {"cycle": base_data["grade"].cycle},
        tenant_header,
    )

    _crud(
        admin_client,
        "/api/v1/curriculum/learning-outcomes/",
        {
            "tenant_id": base_data["tenant_id"],
            "code": "LO-CRUD-01",
            "description": "Resultado CRUD",
            "subject": subject["id"],
            "grade": base_data["grade"].id,
            "cycle": base_data["grade"].cycle,
            "taxonomy_level": "remember",
            "knowledge_dimension": "factual",
            "active": True,
        },
        {"description": "Resultado CRUD 2"},
        tenant_header,
    )

    outcome = admin_client.post(
        "/api/v1/curriculum/learning-outcomes/",
        {
            "tenant_id": base_data["tenant_id"],
            "code": "LO-CRUD-02",
            "description": "Resultado CRUD 2",
            "subject": subject["id"],
            "grade": base_data["grade"].id,
            "cycle": base_data["grade"].cycle,
            "taxonomy_level": "understand",
            "knowledge_dimension": "conceptual",
            "active": True,
        },
        format="json",
        **tenant_header,
    ).data

    _crud(
        admin_client,
        "/api/v1/curriculum/competency-outcomes/",
        {
            "competency": competency["id"],
            "outcome": outcome["id"],
            "weight": "80",
            "tenant_id": base_data["tenant_id"],
        },
        {"weight": "70"},
        tenant_header,
    )

    _crud(
        admin_client,
        "/api/v1/curriculum/subject-plans/",
        {
            "grade_subject": base_data["grade_subject"].id,
            "objectives": "Objetivos",
            "methodology": "Metodologia",
            "assessment_criteria": "Critérios",
            "active": True,
            "competency_ids": [base_data["competency"].id],
        },
        {"objectives": "Objetivos 2"},
        tenant_header,
    )


@pytest.mark.django_db
def test_school_crud(admin_client, tenant_header, base_data):
    _crud(
        admin_client,
        "/api/v1/school/academic-years/",
        {
            "code": "2027-2028",
            "tenant_id": base_data["tenant_id"],
            "start_date": "2027-01-01",
            "end_date": "2028-01-01",
            "active": True,
        },
        {"active": False},
        tenant_header,
    )

    _crud(
        admin_client,
        "/api/v1/school/grades/",
        {"number": 12, "cycle": 2, "name": "Classe 12"},
        {"name": "Classe 12 Atualizada"},
        tenant_header,
    )

    _crud(
        admin_client,
        "/api/v1/school/schools/",
        {"code": "ESC-CRUD-01", "name": "Escola CRUD", "district": "Centro", "province": "Maputo", "active": True},
        {"name": "Escola CRUD 2"},
        {"HTTP_X_TENANT_ID": "tenant-school-crud"},
    )

    user = get_user_model().objects.create_user(username="teacher_crud", password="pass1234")
    _crud(
        admin_client,
        "/api/v1/school/teachers/",
        {
            "user": user.id,
            "school": base_data["school"].id,
            "name": "Professor CRUD",
            "specialty": "Matematica",
        },
        {"specialty": "Fisica"},
        tenant_header,
    )

    teacher = Teacher.objects.create(
        user=get_user_model().objects.create_user(username="teacher_crud2", password="pass1234"),
        school=base_data["school"],
        name="Professor CRUD 2",
        tenant_id=base_data["tenant_id"],
    )
    _crud(
        admin_client,
        "/api/v1/school/classrooms/",
        {
            "name": "1B",
            "tenant_id": base_data["tenant_id"],
            "school": base_data["school"].id,
            "grade": base_data["grade"].number,
            "cycle": base_data["grade"].cycle,
            "academic_year": base_data["academic_year"].id,
            "lead_teacher": teacher.id,
        },
        {"name": "1B Atualizada"},
        tenant_header,
    )

    area = CurriculumArea.objects.create(name="Area CRUD School")
    subject = Subject.objects.create(name="Disciplina CRUD School", area=area, cycle=base_data["grade"].cycle)
    _crud(
        admin_client,
        "/api/v1/school/grade-subjects/",
        {
            "academic_year": base_data["academic_year"].id,
            "grade": base_data["grade"].number,
            "subject": subject.id,
            "weekly_workload": 3,
            "tenant_id": base_data["tenant_id"],
        },
        {"weekly_workload": 4},
        tenant_header,
    )

    grade_subject = GradeSubject.objects.create(
        academic_year=base_data["academic_year"],
        grade=base_data["grade"],
        subject=subject,
        weekly_workload=2,
        tenant_id=base_data["tenant_id"],
    )
    _crud(
        admin_client,
        "/api/v1/school/teaching-assignments/",
        {
            "teacher": base_data["teacher"].id,
            "classroom": base_data["classroom"].id,
            "grade_subject": grade_subject.id,
        },
        {"teacher": base_data["teacher"].id},
        tenant_header,
    )

    student = Student.objects.create(
        name="Aluno CRUD School",
        tenant_id=base_data["tenant_id"],
        birth_date=date(2014, 1, 1),
        grade=base_data["grade"].number,
        cycle=base_data["grade"].cycle,
        estado="active",
    )
    _crud(
        admin_client,
        "/api/v1/school/enrollments/",
        {"student": student.id, "classroom": base_data["classroom"].id},
        {"classroom": base_data["classroom"].id},
        tenant_header,
    )

    _crud(
        admin_client,
        "/api/v1/school/management-assignments/",
        {
            "teacher": base_data["teacher"].id,
            "school": base_data["school"].id,
            "academic_year": base_data["academic_year"].id,
            "role": "school_director",
            "active": True,
        },
        {"active": False},
        tenant_header,
    )

    profile = base_data["teacher"].user.school_profile
    update_profile = admin_client.patch(
        f"/api/v1/school/user-profiles/{profile.id}/",
        {"district": "Centro"},
        format="json",
        **tenant_header,
    )
    assert update_profile.status_code in {200, 202}

    _crud(
        admin_client,
        "/api/v1/school/attendance-records/",
        {
            "enrollment": base_data["enrollment"].id,
            "lesson_date": "2026-03-01",
            "status": "present",
            "notes": "ok",
        },
        {"status": "late"},
        tenant_header,
    )

    _crud(
        admin_client,
        "/api/v1/school/announcements/",
        {
            "school": base_data["school"].id,
            "classroom": base_data["classroom"].id,
            "title": "Comunicado CRUD",
            "message": "Mensagem",
            "audience": "school",
            "active": True,
        },
        {"title": "Comunicado CRUD 2"},
        tenant_header,
    )

    _crud(
        admin_client,
        "/api/v1/school/invoices/",
        {
            "student": base_data["student"].id,
            "school": base_data["school"].id,
            "reference": "INV-CRUD-01",
            "description": "Mensalidade",
            "amount": "100.00",
            "due_date": "2026-04-01",
            "status": "issued",
        },
        {"status": "paid"},
        tenant_header,
    )

    invoice = admin_client.post(
        "/api/v1/school/invoices/",
        {
            "student": base_data["student"].id,
            "school": base_data["school"].id,
            "reference": "INV-CRUD-02",
            "description": "Mensalidade 2",
            "amount": "120.00",
            "due_date": "2026-05-01",
            "status": "issued",
        },
        format="json",
        **tenant_header,
    ).data
    _crud(
        admin_client,
        "/api/v1/school/payments/",
        {
            "invoice": invoice["id"],
            "amount": "120.00",
            "payment_date": "2026-05-05",
            "method": "cash",
            "reference": "PAY-01",
        },
        {"method": "bank_transfer"},
        tenant_header,
    )

    _crud(
        admin_client,
        "/api/v1/school/audit-events/",
        {
            "resource": "student",
            "action": "create",
            "object_id": 999,
            "object_repr": "Aluno",
        },
        {"object_repr": "Aluno 2"},
        tenant_header,
    )

    _crud(
        admin_client,
        "/api/v1/school/audit-alerts/",
        {
            "alert_type": "manual_alert",
            "severity": "watch",
            "summary": "Alerta manual",
        },
        {"severity": "elevated"},
        tenant_header,
    )


@pytest.mark.django_db
def test_assessment_crud(admin_client, tenant_header, base_data):
    _crud(
        admin_client,
        "/api/v1/assessment/periods/",
        {
            "academic_year": base_data["academic_year"].id,
            "name": "Periodo CRUD",
            "order": 2,
            "start_date": "2026-05-01",
            "end_date": "2026-06-30",
            "active": True,
        },
        {"name": "Periodo CRUD 2"},
        tenant_header,
    )

    period = admin_client.post(
        "/api/v1/assessment/periods/",
        {
            "academic_year": base_data["academic_year"].id,
            "name": "Periodo CRUD Sub",
            "order": 3,
            "start_date": "2026-07-01",
            "end_date": "2026-08-30",
            "active": True,
        },
        format="json",
        **tenant_header,
    ).data

    _crud(
        admin_client,
        "/api/v1/assessment/components/",
        {
            "period": period["id"],
            "grade_subject": base_data["grade_subject"].id,
            "type": "test",
            "name": "Componente CRUD",
            "weight": "40",
            "max_score": "20",
            "mandatory": True,
        },
        {"weight": "35"},
        tenant_header,
    )

    component = admin_client.post(
        "/api/v1/assessment/components/",
        {
            "period": period["id"],
            "grade_subject": base_data["grade_subject"].id,
            "type": "test",
            "name": "Componente CRUD Sub",
            "weight": "50",
            "max_score": "20",
            "mandatory": True,
        },
        format="json",
        **tenant_header,
    ).data

    _crud(
        admin_client,
        "/api/v1/assessment/component-outcomes/",
        {
            "component": component["id"],
            "outcome": base_data["outcome"].id,
            "weight": "100",
            "tenant_id": base_data["tenant_id"],
        },
        {"weight": "90"},
        tenant_header,
    )

    _crud(
        admin_client,
        "/api/v1/assessment/assessments/",
        {
            "student": base_data["student"].id,
            "teaching_assignment": base_data["teaching_assignment"].id,
            "period": period["id"],
            "component": component["id"],
            "type": "test",
            "date": "2026-07-10",
            "score": "15",
        },
        {"score": "16"},
        tenant_header,
    )

    _crud(
        admin_client,
        "/api/v1/assessment/subject-period-results/",
        {
            "student": base_data["student"].id,
            "teaching_assignment": base_data["teaching_assignment"].id,
            "period": period["id"],
            "final_average": "14.5",
            "assessments_counted": 1,
        },
        {"final_average": "15.0"},
        tenant_header,
    )


@pytest.mark.django_db
def test_learning_crud(admin_client, tenant_header, base_data):
    _crud(
        admin_client,
        "/api/v1/learning/courses/",
        {
            "school": base_data["school"].id,
            "title": "Curso CRUD",
            "description": "Descricao",
            "modality": "online",
            "active": True,
        },
        {"title": "Curso CRUD 2"},
        tenant_header,
    )

    course = admin_client.post(
        "/api/v1/learning/courses/",
        {
            "school": base_data["school"].id,
            "title": "Curso CRUD Sub",
            "description": "Descricao",
            "modality": "online",
            "active": True,
        },
        format="json",
        **tenant_header,
    ).data

    _crud(
        admin_client,
        "/api/v1/learning/offerings/",
        {
            "course": course["id"],
            "classroom": base_data["classroom"].id,
            "teacher": base_data["teacher"].id,
            "academic_year": base_data["academic_year"].id,
            "start_date": "2026-02-01",
            "end_date": "2026-06-01",
            "active": True,
        },
        {"end_date": "2026-06-15"},
        tenant_header,
    )

    offering = admin_client.post(
        "/api/v1/learning/offerings/",
        {
            "course": course["id"],
            "classroom": base_data["classroom"].id,
            "teacher": base_data["teacher"].id,
            "academic_year": base_data["academic_year"].id,
            "start_date": "2026-02-15",
            "end_date": "2026-05-20",
            "active": True,
        },
        format="json",
        **tenant_header,
    ).data

    _crud(
        admin_client,
        "/api/v1/learning/lessons/",
        {
            "offering": offering["id"],
            "title": "Aula CRUD",
            "description": "Descricao",
            "scheduled_at": datetime(2026, 3, 10, 9, 0).isoformat(),
            "duration_minutes": 45,
            "meeting_url": "https://example.com/aula",
            "published": True,
        },
        {"title": "Aula CRUD 2"},
        tenant_header,
    )

    lesson = admin_client.post(
        "/api/v1/learning/lessons/",
        {
            "offering": offering["id"],
            "title": "Aula CRUD Sub",
            "description": "Descricao",
            "scheduled_at": datetime(2026, 3, 11, 9, 0).isoformat(),
            "duration_minutes": 45,
            "meeting_url": "https://example.com/aula2",
            "published": False,
        },
        format="json",
        **tenant_header,
    ).data

    _crud(
        admin_client,
        "/api/v1/learning/lesson-materials/",
        {
            "lesson": lesson["id"],
            "title": "Material CRUD",
            "material_type": "link",
            "url": "https://example.com/material",
            "required": True,
        },
        {"title": "Material CRUD 2"},
        tenant_header,
    )

    _crud(
        admin_client,
        "/api/v1/learning/assignments/",
        {
            "offering": offering["id"],
            "title": "Tarefa CRUD",
            "instructions": "Instrucoes",
            "opens_at": datetime(2026, 3, 12, 8, 0).isoformat(),
            "due_at": datetime(2026, 3, 20, 23, 0).isoformat(),
            "max_score": "20",
            "published": True,
        },
        {"title": "Tarefa CRUD 2"},
        tenant_header,
    )

    assignment = admin_client.post(
        "/api/v1/learning/assignments/",
        {
            "offering": offering["id"],
            "title": "Tarefa CRUD Sub",
            "instructions": "Instrucoes",
            "opens_at": datetime(2026, 3, 13, 8, 0).isoformat(),
            "due_at": datetime(2026, 3, 22, 23, 0).isoformat(),
            "max_score": "20",
            "published": True,
        },
        format="json",
        **tenant_header,
    ).data

    _crud(
        admin_client,
        "/api/v1/learning/submissions/",
        {
            "assignment": assignment["id"],
            "student": base_data["student"].id,
            "submitted_at": datetime(2026, 3, 14, 10, 0).isoformat(),
            "text_response": "Resposta",
            "status": "submitted",
        },
        {"status": "graded"},
        tenant_header,
    )


@pytest.mark.django_db
def test_progress_and_events(admin_client, tenant_header, base_data):
    _crud(
        admin_client,
        "/api/v1/progress/progressions/",
        {
            "student": base_data["student"].id,
            "cycle": base_data["grade"].cycle,
            "academic_year": "2026-2027",
            "decision_date": "2026-12-10",
            "decision": "approved",
            "comment": "Ok",
        },
        {"decision": "retained"},
        tenant_header,
    )

    _crud(
        admin_client,
        "/api/v1/events/events/",
        {
            "type": "student_registered",
            "payload": {"student_id": base_data["student"].id},
            "tenant_id": base_data["tenant_id"],
        },
        {"payload": {"student_id": base_data["student"].id, "note": "updated"}},
        tenant_header,
    )


@pytest.mark.django_db
def test_reports_generate(admin_client, tenant_header, base_data):
    response = admin_client.post(
        "/api/v1/reports/reports/generate/",
        {
            "report_kind": "learning_intervention_plan",
            "academic_year": base_data["academic_year"].id,
            "grade": base_data["grade"].id,
            "persist": False,
            "emit_alerts": False,
        },
        format="json",
        **tenant_header,
    )
    assert response.status_code == 200
