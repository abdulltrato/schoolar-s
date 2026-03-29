from decimal import Decimal, InvalidOperation
from typing import Dict, Optional


class EvaluationError(ValueError):
    """Erro de validação para avaliação de progressão."""


def _to_score(value: Optional[float], field: str) -> Optional[Decimal]:
    if value is None:
        return None
    try:
        score = Decimal(str(value))
    except (InvalidOperation, TypeError):
        raise EvaluationError(f"O campo {field} deve ser numérico.")
    if score < 0 or score > 20:
        raise EvaluationError(f"O campo {field} deve estar entre 0 e 20.")
    return score


def evaluate_student_progress(
    teste1: float,
    teste2: float,
    teste3: float,
    exame: Optional[float] = None,
    exame_recorrencia: Optional[float] = None,
    exame_especial: Optional[float] = None,
) -> Dict[str, object]:
    """
    Avalia o percurso de aprovação de um estudante com base nas regras fornecidas.

    Regras:
    - Cada teste precisa de pelo menos 10 valores.
    - A média dos três testes precisa ser >= 10; caso contrário, não realiza exame.
    - Se exame < 10, segue para exame de recorrência; se também < 10, vai para exame especial;
      se também < 10, repete o ano.
    - Atingindo 10 ou mais em qualquer exame (exame, recorrência ou especial) o aluno é aprovado,
      desde que os testes cumpram os critérios.
    """

    t1 = _to_score(teste1, "teste1")
    t2 = _to_score(teste2, "teste2")
    t3 = _to_score(teste3, "teste3")
    exam = _to_score(exame, "exame") if exame is not None else None
    exam_rec = _to_score(exame_recorrencia, "exame_recorrencia") if exame_recorrencia is not None else None
    exam_spec = _to_score(exame_especial, "exame_especial") if exame_especial is not None else None

    for name, score in (("teste1", t1), ("teste2", t2), ("teste3", t3)):
        if score is None:
            raise EvaluationError(f"O campo {name} é obrigatório.")
        if score < 10:
            return {
                "estado": "reprovado_testes",
                "proxima_etapa": "Repetir o ano",
                "motivo": f"{name} abaixo de 10 valores.",
                "media_testes": float((t1 + t2 + t3) / 3),
            }

    media = (t1 + t2 + t3) / 3
    if media < 10:
        return {
            "estado": "reprovado_media_testes",
            "proxima_etapa": "Repetir o ano",
            "motivo": "Média dos testes inferior a 10 valores; não deve realizar exame.",
            "media_testes": float(media),
        }

    if exam is None:
        return {
            "estado": "aguarda_exame",
            "proxima_etapa": "Realizar exame final",
            "motivo": "Requisitos dos testes cumpridos; falta o exame final.",
            "media_testes": float(media),
        }

    if exam >= 10:
        return {
            "estado": "aprovado",
            "proxima_etapa": "Nenhuma; aluno aprovado.",
            "motivo": "Exame final com nota suficiente.",
            "media_testes": float(media),
        }

    if exam_rec is None:
        return {
            "estado": "exame_recorrencia",
            "proxima_etapa": "Agendar exame de recorrência",
            "motivo": "Exame final abaixo de 10 valores.",
            "media_testes": float(media),
        }

    if exam_rec >= 10:
        return {
            "estado": "aprovado",
            "proxima_etapa": "Nenhuma; aluno aprovado.",
            "motivo": "Aprovado no exame de recorrência.",
            "media_testes": float(media),
        }

    if exam_spec is None:
        return {
            "estado": "exame_especial",
            "proxima_etapa": "Agendar exame especial",
            "motivo": "Exame de recorrência abaixo de 10 valores.",
            "media_testes": float(media),
        }

    if exam_spec >= 10:
        return {
            "estado": "aprovado",
            "proxima_etapa": "Nenhuma; aluno aprovado.",
            "motivo": "Aprovado no exame especial.",
            "media_testes": float(media),
        }

    return {
        "estado": "repetir_ano",
        "proxima_etapa": "Repetir o ano",
        "motivo": "Exame especial abaixo de 10 valores.",
        "media_testes": float(media),
    }
