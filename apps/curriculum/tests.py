from datetime import date
# Datas para criar anos letivos.

from django.contrib.auth import get_user_model
# Helper para obter model User customizado.
from django.core.exceptions import ValidationError
# Exceção usada em validação de modelos.
from django.test import TestCase
# Base de testes do Django.
from rest_framework.test import APIClient
# Cliente de testes para DRF.

from apps.school.models import AcademicYear, Grade, GradeSubject
# Modelos escolares usados nos testes.
from .models import CurriculumArea, Competency, BaseCurriculum, Subject, SubjectCurriculumPlan
# Modelos de currículo usados nos cenários.


class CurriculoApiTests(TestCase):
    """Testes de integração da API de currículo."""

    def setUp(self):
        """Autentica um usuário padrão para chamadas protegidas."""
        self.user = get_user_model().objects.create_user(username="admin", password="secret")
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_cria_disciplina_usando_area_id(self):
        """Disciplina é criada e vinculada à área ao usar area_id."""
        area = CurriculumArea.objects.create(name="Ciências")

        response = self.client.post(
            "/api/v1/curriculum/disciplinas/",
            {"name": "Matemática", "area_id": area.id, "cycle": 1},
            format="json",
        )

        self.assertEqual(response.status_code, 201)
        subject = Subject.objects.get(name="Matemática")
        self.assertEqual(subject.area, area)

    def test_cria_curriculo_base_usando_lista_de_competencias(self):
        """Currículo base aceita ids de competências no payload."""
        area = CurriculumArea.objects.create(name="Comunicação")
        subject = Subject.objects.create(name="Português", area=area, cycle=1)
        competency = subject.competencia_set.create(
            name="Ler textos curtos",
            cycle=1,
        )

        response = self.client.post(
            "/api/v1/curriculum/curriculos-base/",
            {"cycle": 1, "competencia_ids": [competency.id]},
            format="json",
        )

        self.assertEqual(response.status_code, 201)
        curriculum = BaseCurriculum.objects.get(pk=response.data["id"])
        self.assertEqual(list(curriculum.competencies.all()), [competency])

    def test_curriculo_local_respeita_tenant_do_header(self):
        """Header X-Tenant-ID deve prevalecer sobre payload em currículo local."""
        response = self.client.post(
            "/api/v1/curriculum/curriculos-local/",
            {"tenant_id": "payload-a", "cycle": 1},
            format="json",
            HTTP_X_TENANT_ID="school-central",
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()["tenant_id"], "school-central")

    def test_cria_plano_curricular_para_disciplina_da_classe(self):
        """Cria plano curricular vinculado a GradeSubject."""
        area = CurriculumArea.objects.create(name="Ciências Exatas")
        subject = Subject.objects.create(name="Matemática", area=area, cycle=1)
        academic_year = AcademicYear.objects.create(
            code="2026-2027",
            tenant_id="tenant-esc-1",
            start_date=date(2026, 2, 1),
            end_date=date(2026, 12, 15),
            active=True,
        )
        grade = Grade.objects.create(number=2, cycle=1)
        grade_subject = GradeSubject.objects.create(
            academic_year=academic_year,
            grade=grade,
            subject=subject,
        )

        plano = SubjectCurriculumPlan.objects.create(
            grade_subject=grade_subject,
            objectives="Consolidar operacoes basicas.",
            methodology="Aulas praticas e resolucao de problemas.",
        )

        self.assertEqual(plano.grade_subject, grade_subject)

    def test_rejeita_competencia_de_outra_disciplina_no_plano(self):
        """Impede adicionar competência de disciplina diferente no plano."""
        area = CurriculumArea.objects.create(name="Ciências Integradas")
        subject = Subject.objects.create(name="Matemática", area=area, cycle=1)
        outra_disciplina = Subject.objects.create(name="História", area=area, cycle=1)
        academic_year = AcademicYear.objects.create(
            code="2027-2028",
            tenant_id="tenant-esc-2",
            start_date=date(2027, 2, 1),
            end_date=date(2027, 12, 15),
            active=True,
        )
        grade = Grade.objects.create(number=3, cycle=1)
        grade_subject = GradeSubject.objects.create(
            academic_year=academic_year,
            grade=grade,
            subject=subject,
        )
        plano = SubjectCurriculumPlan.objects.create(grade_subject=grade_subject)
        competencia_invalida = Competency.objects.create(
            name="Interpretar contextos históricos",
            cycle=1,
            subject=outra_disciplina,
        )

        with self.assertRaises(ValidationError):
            plano.planned_competencies.add(competencia_invalida)
