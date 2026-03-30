from django.core.exceptions import ValidationError
# Importa exceção de validação do Django para validar regras de negócio.
from django.db import models
# Importa a base de modelos e campos do Django.

from core.models import BaseCodeModel
# Modelo base com código/tenant e campos auditáveis.
from .component import AssessmentComponent
# Importa o modelo de componente avaliativo para relacionamentos e constantes.
from .period import AssessmentPeriod
# Importa o período avaliativo usado nas FK.


class Assessment(BaseCodeModel):
    """Avaliação de um estudante em uma disciplina/turma, com vínculo a período e componente."""

    # Prefixo usado na geração automática de códigos.
    CODE_PREFIX = "ASM"
    # Tipos de avaliação permitidos, herdados dos componentes.
    TYPE_CHOICES = AssessmentComponent.TYPE_CHOICES

    def __init__(self, *args, **kwargs):
        # Extrai campos legados que podem ter vindo em requests antigas.
        legacy_type = kwargs.pop("tipo", None)
        legacy_date = kwargs.pop("data", None)
        # Converte `tipo` legado para o campo `type` caso ainda não tenha sido informado.
        if legacy_type is not None and "type" not in kwargs:
            kwargs["type"] = legacy_type
        # Converte `data` legado para o campo `date` caso ainda não tenha sido informado.
        if legacy_date is not None and "date" not in kwargs:
            kwargs["date"] = legacy_date
        # Normaliza o tipo recebido mapeando valores legados para o novo padrão.
        normalized_type = kwargs.get("type")
        if normalized_type is not None:
            kwargs["type"] = AssessmentComponent.LEGACY_TYPE_MAP.get(normalized_type, normalized_type)
        # Inicializa a superclasse com os argumentos já higienizados.
        super().__init__(*args, **kwargs)

    # Estudante avaliado.
    student = models.ForeignKey("academic.Student", on_delete=models.CASCADE, verbose_name="Aluno")
    # Alocação docente (turma/disciplina) que originou a avaliação.
    teaching_assignment = models.ForeignKey(
        "school.TeachingAssignment",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name="Alocação docente",
    )
    # Período avaliativo associado.
    period = models.ForeignKey(
        AssessmentPeriod,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Período",
    )
    # Componente avaliativo (exame, teste, etc.).
    component = models.ForeignKey(
        AssessmentComponent,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Componente",
    )
    # Competência curricular avaliada (opcional).
    competency = models.ForeignKey(
        "curriculum.Competency",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Competência",
    )
    # Tipo textual da avaliação.
    type = models.CharField(max_length=30, choices=TYPE_CHOICES, verbose_name="Tipo")
    # Data de realização.
    date = models.DateField(verbose_name="Data")
    # Nota obtida (0-20), opcional até correção.
    score = models.DecimalField(max_digits=4, decimal_places=1, null=True, blank=True, verbose_name="Nota")
    # Observação livre do professor.
    comment = models.TextField(blank=True, verbose_name="Comentário")
    # Flags de domínio para registrar eixos avaliados.
    knowledge = models.BooleanField(default=False, verbose_name="Conhecimentos")
    skills = models.BooleanField(default=False, verbose_name="Habilidades")
    attitudes = models.BooleanField(default=False, verbose_name="Atitudes")

    def clean(self):
        # Normaliza tipo para valores atuais.
        self.type = AssessmentComponent.LEGACY_TYPE_MAP.get(self.type, self.type)
        # Exige sempre uma alocação docente.
        if not self.teaching_assignment_id:
            raise ValidationError({"teaching_assignment": "A teaching assignment is required."})

        # Facilita acesso a turma e disciplina.
        classroom = self.teaching_assignment.classroom
        subject = self.teaching_assignment.grade_subject.subject
        # Obtém tenants dos relacionados para validar consistência.
        student_tenant = (self.student.tenant_id or "").strip() if self.student_id else ""
        classroom_tenant = (classroom.tenant_id or "").strip()

        # Garante que o tenant da avaliação combine com aluno e turma.
        if self.tenant_id and student_tenant and self.tenant_id != student_tenant:
            raise ValidationError({"tenant_id": "Assessment tenant must match the student tenant."})
        if self.tenant_id and classroom_tenant and self.tenant_id != classroom_tenant:
            raise ValidationError({"tenant_id": "Assessment tenant must match the classroom tenant."})
        if student_tenant and classroom_tenant and student_tenant != classroom_tenant:
            raise ValidationError({"tenant_id": "Assessment student and classroom must belong to the same tenant."})
        # Preenche automaticamente tenant se estiver vazio.
        self.tenant_id = self.tenant_id or student_tenant or classroom_tenant

        # Evita duplicar avaliações na mesma data para a mesma turma/disciplina.
        if self.date and self.teaching_assignment_id:
            conflicts = (
                Assessment.objects.filter(
                    tenant_id=self.tenant_id,
                    teaching_assignment_id=self.teaching_assignment_id,
                    date=self.date,
                    deleted_at__isnull=True,
                )
                .exclude(pk=self.pk)
                .exists()
            )
            if conflicts:
                raise ValidationError({"date": "Já existe uma avaliação marcada para esta turma/disciplina nesta data."})

        # Valida vínculo do aluno com a turma e consistência de ciclo/classe.
        if self.student_id:
            if self.student.cycle != classroom.cycle:
                raise ValidationError({"student": "Student and classroom must belong to the same cycle."})
            if self.student.grade != classroom.grade.number:
                raise ValidationError({"student": "Student and classroom must belong to the same grade."})
            enrolled = self.student.enrollment_set.filter(classroom=classroom).exists()
            if not enrolled:
                raise ValidationError({"student": "The student must be enrolled in the assessed classroom."})

        # Garante que a competência selecionada pertence à disciplina avaliada.
        if self.competency_id and self.competency.subject_id != subject.id:
            raise ValidationError({"competency": "The competency must belong to the assessed subject."})

        # Garante que o período seja do mesmo ano letivo da turma.
        if self.period_id and self.period.academic_year_id != classroom.academic_year_id:
            raise ValidationError({"period": "The period must belong to the same academic year as the classroom."})

        # Se houver componente, valida compatibilidades e limites.
        if self.component_id:
            if self.component.grade_subject_id != self.teaching_assignment.grade_subject_id:
                raise ValidationError({"component": "The component must belong to the same grade subject as the assessment."})
            if self.period_id and self.component.period_id != self.period_id:
                raise ValidationError({"component": "The component must belong to the same period."})
            # Sincroniza o tipo com o componente selecionado.
            self.type = self.component.type
            # Impede nota acima do máximo permitido pelo componente.
            if self.score is not None and self.score > self.component.max_score:
                raise ValidationError({"score": "The score cannot exceed the component maximum score."})

        # Checa faixa de nota permitida.
        if self.score is not None and not 0 <= self.score <= 20:
            raise ValidationError({"score": "The score must be between 0 and 20."})

    def _result_key(self):
        # Sem chaves completas não há resultado para recalcular.
        if not self.student_id or not self.teaching_assignment_id or not self.period_id:
            return None
        # Retorna dicionário usado para recalcular média por período.
        return {
            "student": self.student,
            "teaching_assignment": self.teaching_assignment,
            "period": self.period,
        }

    def _sync_results(self, keys):
        # Importa tardiamente para evitar dependência circular.
        from .subject_period_result import SubjectPeriodResult

        # Recalcula resultados agregados para cada chave válida.
        for key in keys:
            if key:
                SubjectPeriodResult.recalculate(**key)

    def _sync_outcomes(self, component_ids):
        # Sem estudante não há competência para atualizar.
        if not self.student_id:
            return
        # Filtra IDs nulos.
        component_ids = [component_id for component_id in component_ids if component_id]
        if not component_ids:
            return
        # Importa serviço de resultados de aprendizagem.
        from apps.academic.models import StudentOutcome

        # Recalcula outcomes relacionados aos componentes passados.
        StudentOutcome.recalculate_for_components(student=self.student, component_ids=component_ids)

    def save(self, *args, **kwargs):
        # Normaliza tipo antes de salvar.
        self.type = AssessmentComponent.LEGACY_TYPE_MAP.get(self.type, self.type)
        previous_key = None
        previous_component_id = None
        # Se já existe registro, captura estado anterior para ressincronizar médias.
        if self.pk:
            previous = type(self).objects.filter(pk=self.pk).select_related(
                "student",
                "teaching_assignment",
                "period",
                "component",
            ).first()
            if previous:
                previous_key = previous._result_key()
                previous_component_id = previous.component_id

        # Valida antes de persistir.
        self.full_clean()
        # Salva usando lógica de BaseCodeModel.
        result = super().save(*args, **kwargs)
        # Recalcula resultados agregados para chaves anterior e nova.
        self._sync_results([previous_key, self._result_key()])
        # Recalcula outcomes associados ao componente anterior e atual.
        self._sync_outcomes([previous_component_id, self.component_id])
        return result

    def delete(self, *args, **kwargs):
        # Guarda chave atual para recalcular médias após a exclusão.
        current_key = self._result_key()
        # Guarda componente atual para recalcular outcomes.
        component_id = self.component_id
        # Executa delete padrão (soft-delete na base).
        result = super().delete(*args, **kwargs)
        # Recalcula resultados agregados removendo esta avaliação.
        self._sync_results([current_key])
        # Recalcula outcomes que dependiam deste componente.
        self._sync_outcomes([component_id])
        return result

    def __str__(self):
        # Representação textual amigável para admin/listagens.
        return f"{self.type} assessment for {self.student} in {self.teaching_assignment.grade_subject.subject}"

    class Meta:
        # Texto exibido no admin.
        verbose_name = "Avaliação"
        verbose_name_plural = "Avaliações"
        # Ordenação padrão por data decrescente.
        ordering = ["-date"]
