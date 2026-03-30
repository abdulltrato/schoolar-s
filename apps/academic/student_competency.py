from django.core.exceptions import ValidationError
from django.db import models

from core.models import BaseCodeModel
from .student import Student


# Modelo que relaciona um aluno com uma competência e seu nível.
class StudentCompetency(BaseCodeModel):
    # Prefixo usado na geração de códigos.
    CODE_PREFIX = "STC"

    # FK para o aluno associado.
    student = models.ForeignKey(Student, on_delete=models.CASCADE, verbose_name="Aluno")
    # FK para a competência curricular.
    competency = models.ForeignKey("curriculum.Competency", on_delete=models.CASCADE, verbose_name="Competência")
    # Nível numérico de domínio na competência.
    nivel = models.DecimalField(max_digits=3, decimal_places=1, default=0.0, verbose_name="Nível")  # e.g., 0.0 to 5.0

    def clean(self):
        # Obtém tenant do aluno se estiver definido.
        student_tenant = (self.student.tenant_id or "").strip() if self.student_id else ""
        # Se existe tenant no aluno, valida coerência e preenche faltantes.
        if student_tenant:
            # Impede divergência de tenant.
            if self.tenant_id and self.tenant_id != student_tenant:
                raise ValidationError({"tenant_id": "O tenant da competência do aluno deve coincidir com o tenant do aluno."})
            # Herda tenant do aluno quando ausente.
            if not self.tenant_id:
                self.tenant_id = student_tenant
        # Exige tenant definido ao final.
        if not (self.tenant_id or "").strip():
            raise ValidationError({"tenant_id": "tenant_id é obrigatório. Envie o header X-Tenant-ID ou configure tenant_id no seu perfil (UserProfile)."})
        # Valida faixa permitida do nível.
        if not 0 <= self.nivel <= 5:
            raise ValidationError({"nivel": "O nível deve estar entre 0.0 e 5.0."})

    def save(self, *args, **kwargs):
        # Executa validação completa antes de salvar.
        self.full_clean()
        # Persiste usando lógica padrão.
        return super().save(*args, **kwargs)

    class Meta:
        # Garante unicidade de competência por aluno enquanto ativo.
        constraints = [
            models.UniqueConstraint(
                fields=["student", "competency"],
                condition=models.Q(deleted_at__isnull=True),
                name="unique_student_competency_active",
            ),
        ]
        # Nomes exibidos no admin.
        verbose_name = "Competência do aluno"
        verbose_name_plural = "Competências dos Alunos"
