from datetime import date
from typing import Tuple

from apps.academic.models import Student
from apps.curriculum.models import (
    CurriculumArea,
    Competency,
    Subject,
    SubjectSpecialty,
    SubjectCurriculumPlan,
)
from apps.school.models import (
    Classroom,
    Grade,
    GradeSubject,
    ManagementAssignment,
    Teacher,
    TeachingAssignment,
)


def ensure_curriculum(area_name="Ciencias Naturais e Matematica"):
    area, _ = CurriculumArea.objects.get_or_create(name=area_name)
    matematica_1, _ = Subject.objects.get_or_create(name="Matematica", area=area, cycle=1)
    matematica_2, _ = Subject.objects.get_or_create(name="Matematica Avancada", area=area, cycle=2)
    especialidade_matematica, _ = SubjectSpecialty.objects.get_or_create(subject=matematica_1, name="Matematica")

    competencia_1, _ = Competency.objects.get_or_create(
        name="Resolver operacoes basicas",
        defaults={"cycle": 1, "subject": matematica_1},
    )
    competencia_2, _ = Competency.objects.get_or_create(
        name="Resolver problemas fraccionarios",
        defaults={"cycle": 2, "subject": matematica_2},
    )
    return (
        area,
        (matematica_1, matematica_2),
        especialidade_matematica,
        (competencia_1, competencia_2),
    )


def ensure_teacher(user, school, specialty):
    teacher, _ = Teacher.objects.get_or_create(
        user=user,
        defaults={
            "name": "Prof. Ana Lemos",
            "specialty": specialty,
            "school": school,
        },
    )
    if teacher.school_id != school.id:
        teacher.school = school
        teacher.save()
    if teacher.specialty_id != specialty.id:
        teacher.specialty = specialty
        teacher.save()
    return teacher


def ensure_classrooms(grade_2: Grade, grade_5: Grade, academic_year, school, teacher):
    turma_a, _ = Classroom.objects.get_or_create(
        name="Classroom A",
        grade=grade_2,
        academic_year=academic_year,
        defaults={
            "school": school,
            "cycle": grade_2.cycle,
            "lead_teacher": teacher,
        },
    )
    turma_b, _ = Classroom.objects.get_or_create(
        name="Classroom B",
        grade=grade_5,
        academic_year=academic_year,
        defaults={
            "school": school,
            "cycle": grade_5.cycle,
            "lead_teacher": teacher,
        },
    )
    for classroom in (turma_a, turma_b):
        changed = False
        if classroom.school_id != school.id:
            classroom.school = school
            changed = True
        if classroom.lead_teacher_id != teacher.id:
            classroom.lead_teacher = teacher
            changed = True
        if changed:
            classroom.save()
    return turma_a, turma_b


def ensure_grade_subjects(academic_year, classe_2, classe_5, matematica_1, matematica_2):
    dc_2, _ = GradeSubject.objects.get_or_create(
        academic_year=academic_year,
        grade=classe_2,
        subject=matematica_1,
        defaults={"weekly_workload": 5},
    )
    dc_5, _ = GradeSubject.objects.get_or_create(
        academic_year=academic_year,
        grade=classe_5,
        subject=matematica_2,
        defaults={"weekly_workload": 5},
    )
    return dc_2, dc_5


def ensure_teaching_assignments(teacher, turma_a, turma_b, dc_2, dc_5):
    alocacao_2, _ = TeachingAssignment.objects.get_or_create(
        teacher=teacher,
        classroom=turma_a,
        grade_subject=dc_2,
    )
    alocacao_5, _ = TeachingAssignment.objects.get_or_create(
        teacher=teacher,
        classroom=turma_b,
        grade_subject=dc_5,
    )
    return alocacao_2, alocacao_5


def ensure_students(turma_a, turma_b):
    aluno_1, _ = Student.objects.get_or_create(
        name="Ana Silva",
        defaults={
            "birth_date": date(2016, 3, 10),
            "grade": 2,
            "cycle": 1,
            "estado": "active",
        },
    )
    aluno_2, _ = Student.objects.get_or_create(
        name="Beto Mussa",
        defaults={
            "birth_date": date(2013, 5, 4),
            "grade": 5,
            "cycle": 2,
            "estado": "active",
        },
    )
    for student, classroom in ((aluno_1, turma_a), (aluno_2, turma_b)):
        from apps.school.models import Enrollment

        Enrollment.objects.get_or_create(student=student, classroom=classroom)
    return aluno_1, aluno_2


def ensure_management_assignments(teacher, school, academic_year, grade: Grade):
    for role, extra in (
        ("director_escola", {}),
        ("director_adjunto_pedagogico", {}),
        ("director_ciclo", {"cycle": 1}),
        ("coordenador_classe", {"grade": grade}),
        ("director_turma", {"classroom": grade.classroom_set.first()}),
    ):
        ManagementAssignment.objects.get_or_create(
            teacher=teacher,
            school=school,
            academic_year=academic_year,
            role=role,
            defaults=extra,
        )


def ensure_subject_plans(dc_2, dc_5, competencia_1, competencia_2) -> Tuple[SubjectCurriculumPlan, SubjectCurriculumPlan]:
    plano_2, _ = SubjectCurriculumPlan.objects.get_or_create(
        grade_subject=dc_2,
        defaults={
            "objectives": "Consolidar operacoes basicas e numeracao.",
            "methodology": "Aulas praticas com resolucao guiada.",
            "assessment_criteria": "Participacao, testes e trabalhos individuais.",
            "active": True,
        },
    )
    plano_2.planned_competencies.set([competencia_1])

    plano_5, _ = SubjectCurriculumPlan.objects.get_or_create(
        grade_subject=dc_5,
        defaults={
            "objectives": "Desenvolver fraccoes e problemas compostos.",
            "methodology": "Aprendizagem orientada por problemas.",
            "assessment_criteria": "ACS, ACP, teste e exame.",
            "active": True,
        },
    )
    plano_5.planned_competencies.set([competencia_2])
    return plano_2, plano_5
