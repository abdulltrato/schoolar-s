from datetime import date

from django.core.exceptions import ValidationError
from django.test import TestCase

from .models import Student


class AlunoModelTests(TestCase):
    def test_rejeita_classe_fora_do_intervalo(self):
        with self.assertRaises(ValidationError):
            Student.objects.create(
                name="Student Inválido",
                birth_date=date(2015, 1, 1),
                grade=0,
                cycle=1,
            )

    def test_define_ciclo_automaticamente_a_partir_da_classe(self):
        student = Student.objects.create(
            name="Student Coerente",
            birth_date=date(2014, 1, 1),
            grade=5,
            cycle=1,
        )

        self.assertEqual(student.cycle, 2)

    def test_define_ensino_secundario_e_primeiro_ciclo_para_classe_7(self):
        student = Student.objects.create(
            name="Student Secundario",
            birth_date=date(2012, 1, 1),
            grade=7,
            cycle=1,
        )

        self.assertEqual(student.education_level, "secundario")
        self.assertEqual(student.cycle, 1)
