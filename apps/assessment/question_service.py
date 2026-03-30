from django.db import transaction
# Importa controle de transação para operações atômicas.

from .question import AssessmentQuestion, Question
# Importa modelos de pergunta e vínculo de pergunta.

# Conjunto de tipos de avaliação que utilizam perguntas.
TESTABLE_TYPES = {"test", "exam", "acs", "acp"}


def assign_questions_to_assessment(assessment, *, question_ids=None, default_count=6):
    """
    Atribui perguntas a uma avaliação de forma segura,
    removendo vínculos anteriores e criando novos com base em IDs fornecidos
    ou sorteando perguntas aleatórias do mesmo tipo/disciplina.
    """
    # Se o tipo da avaliação não utiliza perguntas, sai cedo.
    if assessment.type not in TESTABLE_TYPES:
        return

    # Executa toda a atribuição dentro de uma transação.
    with transaction.atomic():
        # Remove vínculos anteriores da avaliação.
        AssessmentQuestion.objects.filter(assessment=assessment).delete()
        if question_ids:
            # Quando IDs são fornecidos, filtra exatamente essas perguntas.
            questions = Question.objects.filter(pk__in=[q.pk for q in question_ids])
            questions = list(questions)
        else:
            # Caso contrário, busca perguntas aleatórias da mesma disciplina e tipo.
            subject = assessment.teaching_assignment.grade_subject.subject
            pool = Question.objects.filter(subject=subject, question_type=assessment.type)
            questions = list(pool.order_by("?")[:default_count])
        # Cria vínculos preservando a ordem.
        for order, question in enumerate(questions):
            AssessmentQuestion.objects.create(
                assessment=assessment,
                question=question,
                order=order,
            )
