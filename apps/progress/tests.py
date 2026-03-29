from django.test import TestCase

from .evaluation import EvaluationError, evaluate_student_progress


class EvaluateStudentProgressTests(TestCase):
    def test_reprovado_por_media_dos_testes(self):
        resultado = evaluate_student_progress(teste1=5, teste2=12, teste3=12)
        self.assertEqual(resultado["estado"], "reprovado_media_testes")
        self.assertIn("não deve realizar exame", resultado["motivo"])

    def test_aguarda_exame_quando_testes_ok(self):
        resultado = evaluate_student_progress(teste1=10, teste2=11, teste3=12)
        self.assertEqual(resultado["estado"], "aguarda_exame")
        self.assertEqual(resultado["proxima_etapa"], "Realizar exame final")

    def test_aprova_no_exame_de_recorrencia(self):
        resultado = evaluate_student_progress(teste1=10, teste2=10, teste3=14, exame=8, exame_recorrencia=11)
        self.assertEqual(resultado["estado"], "aprovado")
        self.assertIn("recorrência", resultado["motivo"])

    def test_repete_ano_quando_exame_especial_falha(self):
        resultado = evaluate_student_progress(
            teste1=12,
            teste2=12,
            teste3=12,
            exame=8,
            exame_recorrencia=9,
            exame_especial=7,
        )
        self.assertEqual(resultado["estado"], "repetir_ano")
        self.assertIn("Exame especial", resultado["motivo"])

    def test_valida_intervalo_de_notas(self):
        with self.assertRaises(EvaluationError):
            evaluate_student_progress(teste1=21, teste2=10, teste3=10)
