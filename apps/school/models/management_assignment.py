from django.core.exceptions import ValidationError
# Exceção de validação.
from django.db import models
# Campos do ORM.

from core.models import BaseCodeModel
# Modelo base com código e auditoria.

from .academic_year import AcademicYear
# Ano letivo da atribuição.
from .cycle_grade import Grade
# Classe alvo (quando aplicável).
from .classroom import Classroom
# Turma alvo (quando aplicável).
from .school import School
# Escola (tenant) onde o cargo se aplica.
from .teacher import Teacher
# Professor designado.


class ManagementAssignment(BaseCodeModel):
    """Atribuição de cargos de gestão (diretor, coordenador, etc.) para um professor."""

    CODE_PREFIX = "MAS"
    ROLE_CHOICES = [
        ("homeroom_director", "Diretor de turma"),
        ("grade_coordinator", "Coordenador de classe"),
        ("cycle_director", "Diretor de ciclo"),
        ("deputy_pedagogical_director", "Diretor adjunto pedagógico"),
        ("school_director", "Diretor da escola"),
    ]
    LEGACY_ROLE_MAP = {
        "director_turma": "homeroom_director",
        "diretor_turma": "homeroom_director",
        "coordenador_classe": "grade_coordinator",
        "diretor_ciclo": "cycle_director",
        "director_pedagogico_adjunto": "deputy_pedagogical_director",
        "diretor_pedagogico_adjunto": "deputy_pedagogical_director",
        "director_escola": "school_director",
        "diretor_escola": "school_director",
    }

    # Professor designado.
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, verbose_name="Professor")
    # Escola em que o cargo se aplica.
    school = models.ForeignKey(School, on_delete=models.CASCADE, verbose_name="Escola")
    # Ano letivo de validade.
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE, verbose_name="Ano letivo")
    # Cargo atribuído (com mapeamento legado).
    role = models.CharField(max_length=40, choices=ROLE_CHOICES, verbose_name="Cargo")
    # Escopo por classe (para coordenador de classe).
    grade = models.ForeignKey(Grade, null=True, blank=True, on_delete=models.CASCADE, verbose_name="Classe")
    # Escopo por turma (para diretor de turma).
    classroom = models.ForeignKey(Classroom, null=True, blank=True, on_delete=models.CASCADE, verbose_name="Turma")
    # Escopo por ciclo (para diretor de ciclo).
    cycle = models.PositiveSmallIntegerField(null=True, blank=True, verbose_name="Ciclo")
    # Ativo/inativo.
    active = models.BooleanField(default=True, verbose_name="Ativo")

    def __init__(self, *args, **kwargs):
        """Normaliza nomes legados de cargos na criação."""
        role = kwargs.get("role")
        if role is not None:
            kwargs["role"] = self.LEGACY_ROLE_MAP.get(role, role)
        super().__init__(*args, **kwargs)

    def clean(self):
        """Valida tenants e escopos coerentes conforme o cargo."""
        self.role = self.LEGACY_ROLE_MAP.get(self.role, self.role)
        teacher_tenant = (self.teacher.tenant_id or "").strip() if self.teacher_id else ""
        school_tenant = (self.school.tenant_id or "").strip() if self.school_id else ""
        academic_tenant = (self.academic_year.tenant_id or "").strip() if self.academic_year_id else ""
        if self.tenant_id and teacher_tenant and self.tenant_id != teacher_tenant:
            raise ValidationError({"tenant_id": "O tenant da atribuição deve coincidir com o tenant do professor."})
        if self.tenant_id and school_tenant and self.tenant_id != school_tenant:
            raise ValidationError({"tenant_id": "O tenant da atribuição deve coincidir com o tenant da escola."})
        if self.tenant_id and academic_tenant and self.tenant_id != academic_tenant:
            raise ValidationError({"tenant_id": "O tenant da atribuição deve coincidir com o tenant do ano letivo."})
        if teacher_tenant and school_tenant and teacher_tenant != school_tenant:
            raise ValidationError({"tenant_id": "Professor e escola devem pertencer ao mesmo tenant."})
        if academic_tenant and school_tenant and academic_tenant != school_tenant:
            raise ValidationError({"tenant_id": "Ano letivo e escola devem pertencer ao mesmo tenant."})
        self.tenant_id = self.tenant_id or teacher_tenant or school_tenant or academic_tenant
        if not (self.tenant_id or "").strip():
            raise ValidationError({"tenant_id": "tenant_id é obrigatório."})
        if self.teacher.school_id and self.teacher.school_id != self.school_id:
            raise ValidationError({"teacher": "O professor deve pertencer à mesma escola da atribuição."})

        if self.classroom_id:
            if self.classroom.school_id and self.classroom.school_id != self.school_id:
                raise ValidationError({"classroom": "A turma deve pertencer à mesma escola."})
            if self.classroom.academic_year_id != self.academic_year_id:
                raise ValidationError({"classroom": "A turma deve pertencer ao mesmo ano letivo."})

        if self.role == "homeroom_director":
            if not self.classroom_id:
                raise ValidationError({"classroom": "A homeroom director assignment requires a classroom."})
            if self.grade_id or self.cycle:
                raise ValidationError("Uma atribuição de diretor de turma não deve definir classe ou ciclo separadamente.")
        elif self.role == "grade_coordinator":
            if not self.grade_id:
                raise ValidationError({"grade": "Uma atribuição de coordenador de classe requer uma classe."})
            if self.classroom_id or self.cycle:
                raise ValidationError("Uma atribuição de coordenador de classe não deve definir turma ou ciclo.")
        elif self.role == "cycle_director":
            if self.cycle not in {1, 2}:
                raise ValidationError({"cycle": "Uma atribuição de diretor de ciclo requer ciclo 1 ou 2."})
            if self.classroom_id or self.grade_id:
                raise ValidationError("Uma atribuição de diretor de ciclo não deve definir turma ou classe.")
        elif self.role in {"deputy_pedagogical_director", "school_director"}:
            if self.classroom_id or self.grade_id or self.cycle:
                raise ValidationError("Uma função ao nível da escola não deve definir escopos adicionais.")

    def save(self, *args, **kwargs):
        """Normaliza cargo legado, valida e salva."""
        self.role = self.LEGACY_ROLE_MAP.get(self.role, self.role)
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        """Exibe cargo, professor e ano letivo."""
        return f"{self.get_role_display()} - {self.teacher} ({self.academic_year})"

    class Meta:
        verbose_name = "Atribuição de gestão"
        verbose_name_plural = "Atribuições de gestão"
        ordering = ["academic_year__code", "school__name", "role", "teacher__name"]
