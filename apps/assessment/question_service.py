from django.db import transaction

from .question import AssessmentQuestion, Question

TESTABLE_TYPES = {"test", "exam", "acs", "acp"}


def assign_questions_to_assessment(assessment, *, question_ids=None, default_count=6):
    if assessment.type not in TESTABLE_TYPES:
        return

    with transaction.atomic():
        AssessmentQuestion.objects.filter(assessment=assessment).delete()
        if question_ids:
            questions = Question.objects.filter(pk__in=[q.pk for q in question_ids])
            questions = list(questions)
        else:
            subject = assessment.teaching_assignment.grade_subject.subject
            pool = Question.objects.filter(subject=subject, question_type=assessment.type)
            questions = list(pool.order_by("?")[:default_count])
        for order, question in enumerate(questions):
            AssessmentQuestion.objects.create(
                assessment=assessment,
                question=question,
                order=order,
            )
