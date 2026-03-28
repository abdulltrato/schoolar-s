from datetime import date
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from apps.academic.models import Student
from apps.assessment.models import (
    Assessment,
    AssessmentComponent,
    AssessmentPeriod,
    SubjectPeriodResult,
)
from apps.curriculum.models import (
    CurriculumArea,
    Competency,
    Subject,
    SubjectSpecialty,
    SubjectCurriculumPlan,
)
from apps.school.models import (
    TeachingAssignment,
    AcademicYear,
    ManagementAssignment,
    Grade,
    GradeSubject,
    School,
    Enrollment,
    Teacher,
    Classroom,
)


class Command(BaseCommand):
    help = "Cria dados mínimos de demonstração para integrar backend e frontend localmente."

    def handle(self, *args, **options):
        user_model = get_user_model()

        admin, _ = user_model.objects.get_or_create(
            username="admin",
            defaults={"is_staff": True, "is_superuser": True},
        )
        admin.set_password("secret")
        admin.is_staff = True
        admin.is_superuser = True
        admin.save()

        professor_user, _ = user_model.objects.get_or_create(username="prof1")
        professor_user.set_password("secret")
        professor_user.save()

        school, _ = School.objects.get_or_create(
            code="ESC-CENTRAL",
            defaults={
                "name": "School Primaria Central",
                "district": "KaMpfumo",
                "province": "Maputo Cidade",
                "active": True,
            },
        )

        academic_year, _ = AcademicYear.objects.get_or_create(
            code="2026-2027",
            defaults={
                "start_date": date(2026, 2, 1),
                "end_date": date(2026, 12, 15),
                "active": True,
            },
        )

        classe_2, _ = Grade.objects.get_or_create(number=2, defaults={"cycle": 1, "name": "2a Grade"})
        classe_5, _ = Grade.objects.get_or_create(number=5, defaults={"cycle": 2, "name": "5a Grade"})

        area, _ = CurriculumArea.objects.get_or_create(name="Ciencias Naturais e Matematica")
        matematica_1, _ = Subject.objects.get_or_create(name="Matematica", area=area, cycle=1)
        matematica_2, _ = Subject.objects.get_or_create(name="Matematica Avancada", area=area, cycle=2)
        especialidade_matematica, _ = SubjectSpecialty.objects.get_or_create(subject=matematica_1, name="Matematica")

        teacher, _ = Teacher.objects.get_or_create(
            user=professor_user,
            defaults={
                "name": "Prof. Ana Lemos",
                "specialty": especialidade_matematica,
                "school": school,
            },
        )
        if teacher.school_id != school.id:
            teacher.school = school
            teacher.save()
        if teacher.specialty_id != especialidade_matematica.id:
            teacher.specialty = especialidade_matematica
            teacher.save()

        turma_a, _ = Classroom.objects.get_or_create(
            name="Classroom A",
            grade=classe_2,
            academic_year=academic_year,
            defaults={
                "school": school,
                "cycle": classe_2.cycle,
                "lead_teacher": teacher,
            },
        )
        turma_b, _ = Classroom.objects.get_or_create(
            name="Classroom B",
            grade=classe_5,
            academic_year=academic_year,
            defaults={
                "school": school,
                "cycle": classe_5.cycle,
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

        competencia_1, _ = Competency.objects.get_or_create(
            name="Resolver operacoes basicas",
            defaults={
                "cycle": 1,
                "subject": matematica_1,
            },
        )
        competencia_2, _ = Competency.objects.get_or_create(
            name="Resolver problemas fraccionarios",
            defaults={
                "cycle": 2,
                "subject": matematica_2,
            },
        )

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

        Enrollment.objects.get_or_create(student=aluno_1, classroom=turma_a)
        Enrollment.objects.get_or_create(student=aluno_2, classroom=turma_b)

        for role, extra in (
            ("director_escola", {}),
            ("director_adjunto_pedagogico", {}),
            ("director_ciclo", {"cycle": 1}),
            ("coordenador_classe", {"grade": classe_2}),
            ("director_turma", {"classroom": turma_a}),
        ):
            ManagementAssignment.objects.get_or_create(
                teacher=teacher,
                school=school,
                academic_year=academic_year,
                role=role,
                defaults=extra,
            )

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

        periodo_1, _ = AssessmentPeriod.objects.get_or_create(
            academic_year=academic_year,
            order=1,
            defaults={
                "name": "1o Trimestre",
                "start_date": date(2026, 2, 1),
                "end_date": date(2026, 4, 30),
                "active": True,
            },
        )

        componente_acs, _ = AssessmentComponent.objects.get_or_create(
            period=periodo_1,
            grade_subject=dc_2,
            name="ACS 1",
            defaults={
                "tipo": "acs",
                "weight": Decimal("40.00"),
                "max_score": Decimal("20.00"),
                "mandatory": True,
            },
        )
        componente_exame, _ = AssessmentComponent.objects.get_or_create(
            period=periodo_1,
            grade_subject=dc_2,
            name="Exame 1",
            defaults={
                "tipo": "exame",
                "weight": Decimal("60.00"),
                "max_score": Decimal("20.00"),
                "mandatory": True,
            },
        )

        Assessment.objects.get_or_create(
            student=aluno_1,
            teaching_assignment=alocacao_2,
            period=periodo_1,
            component=componente_acs,
            defaults={
                "competency": competencia_1,
                "tipo": "acs",
                "data": date(2026, 3, 15),
                "score": Decimal("14.0"),
                "comment": "Bom desempenho nas operacoes basicas.",
                "knowledge": True,
            },
        )
        Assessment.objects.get_or_create(
            student=aluno_1,
            teaching_assignment=alocacao_2,
            period=periodo_1,
            component=componente_exame,
            defaults={
                "competency": competencia_1,
                "tipo": "exame",
                "data": date(2026, 4, 20),
                "score": Decimal("16.0"),
                "comment": "Evolucao consistente no trimestre.",
                "skills": True,
            },
        )

        SubjectPeriodResult.recalcular(
            student=aluno_1,
            teaching_assignment=alocacao_2,
            period=periodo_1,
        )

        self.stdout.write(self.style.SUCCESS("Dados de demonstração carregados com sucesso."))
