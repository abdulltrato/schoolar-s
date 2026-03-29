from django.core.management.base import BaseCommand

from apps.school.management.demo_seed_users import ensure_academic_year, ensure_grades, ensure_school, ensure_users
from apps.school.management.demo_seed_curriculum import (
    ensure_classrooms,
    ensure_curriculum,
    ensure_grade_subjects,
    ensure_management_assignments,
    ensure_students,
    ensure_subject_plans,
    ensure_teacher,
    ensure_teaching_assignments,
)
from apps.school.management.demo_seed_assessment import ensure_components, ensure_period, seed_assessments


class Command(BaseCommand):
    help = "Cria dados mínimos de demonstração para integrar backend e frontend localmente."

    def handle(self, *args, **options):
        admin, professor_user = ensure_users()
        school = ensure_school()
        academic_year = ensure_academic_year()
        classe_2, classe_5 = ensure_grades()
        _, (matematica_1, _matematica_2), especialidade_matematica, (competencia_1, competencia_2) = ensure_curriculum()

        teacher = ensure_teacher(professor_user, school, especialidade_matematica)
        turma_a, turma_b = ensure_classrooms(classe_2, classe_5, academic_year, school, teacher)
        dc_2, dc_5 = ensure_grade_subjects(academic_year, classe_2, classe_5, matematica_1, _matematica_2)
        alocacao_2, alocacao_5 = ensure_teaching_assignments(teacher, turma_a, turma_b, dc_2, dc_5)
        aluno_1, aluno_2 = ensure_students(turma_a, turma_b)

        ensure_management_assignments(teacher, school, academic_year, classe_2)
        ensure_subject_plans(dc_2, dc_5, competencia_1, competencia_2)

        periodo_1 = ensure_period(academic_year)
        comp_acs, comp_exame = ensure_components(periodo_1, dc_2)
        seed_assessments(aluno_1, alocacao_2, periodo_1, comp_acs, comp_exame, competencia_1)

        self.stdout.write(self.style.SUCCESS("Dados de demonstração carregados com sucesso."))
