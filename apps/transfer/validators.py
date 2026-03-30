from django.core.exceptions import ValidationError
# Exceção de validação.


def _assert(condition, field, message):
    """Ajuda a lançar ValidationError de forma concisa."""
    if not condition:
        raise ValidationError({field: message})


def validate_student_transfer(instance):
    """Regras básicas para transferências de aluno."""
    _assert(instance.student_id, "student", "Informe o aluno.")
    _assert(not instance.teacher_id, "teacher", "Não pode informar professor numa transferência de aluno.")
    _assert(instance.to_classroom_id, "to_classroom", "Informe a turma de destino.")

    if instance.from_classroom_id and instance.from_classroom_id == instance.to_classroom_id:
        raise ValidationError({"to_classroom": "A turma de destino deve ser diferente da turma de origem."})

    instance.to_school = getattr(instance.to_classroom, "school", None)
    if instance.from_classroom_id:
        instance.from_school = getattr(instance.from_classroom, "school", None)


def validate_teacher_transfer(instance):
    """Regras básicas para transferências de professor."""
    _assert(instance.teacher_id, "teacher", "Informe o professor.")
    _assert(not instance.student_id, "student", "Não pode informar aluno numa transferência de professor.")
    _assert(instance.to_classroom_id or instance.to_school_id, "to_school", "Informe a escola ou a turma de destino.")

    if instance.to_classroom_id:
        instance.to_school = getattr(instance.to_classroom, "school", None)
    if instance.from_classroom_id:
        instance.from_school = getattr(instance.from_classroom, "school", None)

    if instance.move_teaching_assignments and not (instance.from_classroom_id and instance.to_classroom_id):
        raise ValidationError({"move_teaching_assignments": "Informe turma de origem e destino para mover alocações."})
