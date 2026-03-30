from django.core.exceptions import ValidationError
# Exceção de validação.
from django.db import models
# Campos do ORM.

from core.models import BaseCodeModel
# Modelo base com código e auditoria.

from .academic_year import AcademicYear
# Ano letivo vinculado.
from .cycle_grade import Grade
# Classe/ano da disciplina ofertada.


class GradeSubject(BaseCodeModel):
    """Oferta de uma disciplina para uma classe em um ano letivo específico."""

    CODE_PREFIX = "GDS"

    # Ano letivo em que a disciplina é ofertada.
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE, verbose_name="Ano letivo")
    # Classe/ano alvo.
    grade = models.ForeignKey(Grade, on_delete=models.CASCADE, verbose_name="Classe")
    # Disciplina do currículo.
    subject = models.ForeignKey("curriculum.Subject", on_delete=models.CASCADE, verbose_name="Disciplina")
    # Carga horária semanal.
    weekly_workload = models.PositiveSmallIntegerField(default=0, verbose_name="Carga horária semanal")

    def clean(self):
        """Valida ciclo compatível e sincroniza tenant com ano letivo."""
        if self.subject_id and self.grade_id and self.subject.cycle != self.grade.cycle:
            raise ValidationError({"subject": "A disciplina deve pertencer ao mesmo ciclo da classe."})
        academic_tenant = (self.academic_year.tenant_id or "").strip() if self.academic_year_id else ""
        if academic_tenant:
            if self.tenant_id and self.tenant_id != academic_tenant:
                raise ValidationError({"tenant_id": "O tenant da disciplina da classe deve coincidir com o tenant do ano letivo."})
            if not self.tenant_id:
                self.tenant_id = academic_tenant
        if not (self.tenant_id or "").strip():
            raise ValidationError({"tenant_id": "tenant_id é obrigatório."})

    def save(self, *args, **kwargs):
        """Valida antes de persistir."""
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        """Exibe disciplina, classe e ano."""
        return f"{self.subject} - {self.grade} ({self.academic_year})"

    class Meta:
        # Rótulos, ordenação e unicidade ativa.
        verbose_name = "Disciplina da classe"
        verbose_name_plural = "Disciplinas da classe"
        ordering = ["academic_year__code", "grade__number", "subject__name"]
        constraints = [
            models.UniqueConstraint(
                fields=["tenant_id", "academic_year", "grade", "subject"],
                condition=models.Q(deleted_at__isnull=True),
                name="unique_grade_subject_active",
            ),
        ]
