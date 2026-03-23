#!/usr/bin/env python
import os
import django
import sys

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'schoolar_s.settings')
django.setup()

from apps.academic.models import Student
from apps.curriculum.models import CurriculumArea, Subject, Competency, BaseCurriculum, LocalCurriculum
from apps.assessment.models import Assessment
from apps.progress.models import Progression
from apps.school.models import Teacher, Classroom, Enrollment
from apps.reports.models import Report
from apps.events.models import Event
from django.contrib.auth.models import User

def test_models():
    print("Iniciando testes dos modelos...")

    # Teste Academico
    try:
        student = Student.objects.create(
            name="Joao Silva",
            birth_date="2010-05-15",
            grade=1,
            cycle=1,
            estado="active"
        )
        print(f"✓ Student criado: {student}")
    except Exception as e:
        print(f"✗ Erro em Student: {e}")

    # Teste Curriculo
    try:
        area = CurriculumArea.objects.create(name="Ciencias Naturais")
        print(f"✓ Area Curricular criada: {area}")

        subject = Subject.objects.create(
            name="Matematica",
            area=area,
            cycle=1
        )
        print(f"✓ Subject criada: {subject}")

        competency = Competency.objects.create(
            name="Resolver problemas matematicos",
            description="Competency em matematica basica",
            area="saber_cientifico_tecnologico",
            cycle=1,
            subject=subject
        )
        print(f"✓ Competency criada: {competency}")

        curriculo_base = BaseCurriculum.objects.create(cycle=1)
        curriculo_base.competencies.add(competency)
        print(f"✓ Curriculo Base criado: {curriculo_base}")

        curriculo_local = LocalCurriculum.objects.create(
            tenant_id="escola1",
            cycle=1
        )
        print(f"✓ Curriculo Local criado: {curriculo_local}")

    except Exception as e:
        print(f"✗ Erro em Curriculo: {e}")

    # Teste Assessment
    try:
        assessment = Assessment.objects.create(
            student=student,
            competency=competency,
            tipo="formativa",
            data="2023-10-01",
            comment="Bom desempenho",
            knowledge=True,
            skills=True,
            attitudes=False
        )
        print(f"✓ Assessment criada: {assessment}")
    except Exception as e:
        print(f"✗ Erro em Assessment: {e}")

    # Teste Progresso
    try:
        progress = Progression.objects.create(
            student=student,
            cycle=1,
            academic_year="2023-2024",
            data_decisao="2024-06-15",
            decisao="aprovado",
            comment="Aprovado com sucesso"
        )
        print(f"✓ Progression criada: {progress}")
    except Exception as e:
        print(f"✗ Erro em Progresso: {e}")

    # Teste School
    try:
        user = User.objects.create_user(username="prof1", password="pass123")
        teacher = Teacher.objects.create(
            user=user,
            name="Prof. Maria",
            specialty="Matematica"
        )
        print(f"✓ Teacher criado: {teacher}")

        classroom = Classroom.objects.create(
            name="Classroom A",
            cycle=1,
            academic_year="2023-2024",
            lead_teacher=teacher
        )
        print(f"✓ Classroom criada: {classroom}")

        enrollment = Enrollment.objects.create(
            student=student,
            classroom=classroom
        )
        print(f"✓ Enrollment criada: {enrollment}")
    except Exception as e:
        print(f"✗ Erro em School: {e}")

    # Teste Relatorios
    try:
        relatorio = Report.objects.create(
            titulo="Report de Student Joao",
            tipo="student",
            period="2023-2024",
            conteudo={"notas": [8, 9, 7]},
            student=student
        )
        print(f"✓ Report criado: {relatorio}")
    except Exception as e:
        print(f"✗ Erro em Relatorios: {e}")

    # Teste Eventos
    try:
        evento = Event.objects.create(
            tipo="aluno_registrado",
            dados={"aluno_id": student.id},
            tenant_id="escola1"
        )
        print(f"✓ Event criado: {evento}")
    except Exception as e:
        print(f"✗ Erro em Eventos: {e}")

    print("Testes concluidos!")

if __name__ == "__main__":
    test_models()
