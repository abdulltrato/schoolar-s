from datetime import date
from decimal import Decimal
from typing import Tuple

from apps.assessment.models import Assessment, AssessmentComponent, AssessmentPeriod, SubjectPeriodResult
from apps.curriculum.models import Competency
from apps.school.models import GradeSubject, TeachingAssignment


def ensure_period(academic_year) -> AssessmentPeriod:
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
    return periodo_1


def ensure_components(periodo_1: AssessmentPeriod, dc_2: GradeSubject) -> Tuple[AssessmentComponent, AssessmentComponent]:
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
    return componente_acs, componente_exame


def seed_assessments(aluno_1, alocacao_2: TeachingAssignment, periodo_1: AssessmentPeriod, comp_acs, comp_exame, competencia_1: Competency):
    Assessment.objects.get_or_create(
        student=aluno_1,
        teaching_assignment=alocacao_2,
        period=periodo_1,
        component=comp_acs,
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
        component=comp_exame,
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
