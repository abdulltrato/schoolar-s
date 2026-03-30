from django.core.exceptions import ValidationError
# Exceção de validação.
from django.db import models
# Componentes do ORM.

from core.models import BaseNamedCodeModel
# Modelo base com nome, código e auditoria.

from .cycle_grade import Cycle, Grade
# Ciclo e classe/ano.
from .academic_year import AcademicYear
# Ano letivo vinculado.
from .school import School
# Escola (tenant) dona da turma.
from .teacher import Teacher
# Professor diretor de turma.


class Classroom(BaseNamedCodeModel):
    """Turma vinculada a classe, ano letivo e escola, com ciclo derivado."""

    CODE_PREFIX = "CLS"

    # Escola a que a turma pertence.
    school = models.ForeignKey(
        School,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="classrooms",
        verbose_name="Escola",
    )
    # Classe/ano associado.
    grade = models.ForeignKey(Grade, on_delete=models.PROTECT, null=True, blank=True, verbose_name="Classe")
    # Ciclo derivado da classe.
    cycle = models.IntegerField(verbose_name="Ciclo")
    # Modelo de ciclo (legado/compatibilidade).
    cycle_model = models.ForeignKey(
        Cycle,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="classrooms",
        verbose_name="Ciclo (model)",
    )
    # Ano letivo em que a turma ocorre.
    academic_year = models.ForeignKey(
        AcademicYear,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        verbose_name="Ano letivo",
    )
    # Professor responsável/diretor.
    lead_teacher = models.ForeignKey(
        Teacher,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Diretor de turma",
    )

    def clean(self):
        """Valida vínculos obrigatórios, sincroniza ciclo e garante tenant coerente."""
        if not self.grade_id:
            raise ValidationError({"grade": "A turma deve estar associada a uma classe."})
        if not self.academic_year_id:
            raise ValidationError({"academic_year": "A turma deve estar associada a um ano letivo."})

        school_tenant = (self.school.tenant_id or "").strip() if self.school_id else ""
        academic_tenant = (self.academic_year.tenant_id or "").strip() if self.academic_year_id else ""
        if school_tenant:
            if self.tenant_id and self.tenant_id != school_tenant:
                raise ValidationError({"tenant_id": "O tenant da turma deve coincidir com o tenant da escola."})
            if not self.tenant_id:
                self.tenant_id = school_tenant
        if academic_tenant:
            if self.tenant_id and self.tenant_id != academic_tenant:
                raise ValidationError({"tenant_id": "O tenant da turma deve coincidir com o tenant do ano letivo."})
            if school_tenant and academic_tenant != school_tenant:
                raise ValidationError({"academic_year": "O ano letivo deve pertencer ao mesmo tenant da escola."})
            if not self.tenant_id:
                self.tenant_id = academic_tenant

        if self.lead_teacher_id and self.school_id and self.lead_teacher.school_id:
            if self.lead_teacher.school_id != self.school_id:
                raise ValidationError({"lead_teacher": "O diretor de turma deve pertencer à mesma escola."})
            if self.lead_teacher.tenant_id:
                if self.tenant_id and self.tenant_id != self.lead_teacher.tenant_id:
                    raise ValidationError({"tenant_id": "O tenant da turma deve coincidir com o tenant do diretor de turma."})
                if not self.tenant_id:
                    self.tenant_id = self.lead_teacher.tenant_id

        if self.grade_id:
            self.cycle = self.grade.cycle
            if not self.cycle_model_id and self.grade.cycle_model_id:
                self.cycle_model = self.grade.cycle_model
        if not (self.tenant_id or "").strip():
            raise ValidationError({"tenant_id": "tenant_id é obrigatório."})

    def save(self, *args, **kwargs):
        """Valida antes de salvar."""
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        """Exibe nome e ano letivo para fácil identificação."""
        return f"{self.name} - {self.academic_year}"

    class Meta:
        # Rótulos, ordenação e unicidade por tenant/ano/classe/nome.
        verbose_name = "Turma"
        verbose_name_plural = "Turmas"
        ordering = ["academic_year__code", "grade__number", "name"]
        constraints = [
            models.UniqueConstraint(
                fields=["tenant_id", "name", "grade", "academic_year"],
                condition=models.Q(deleted_at__isnull=True),
                name="unique_classroom_active",
            ),
        ]
