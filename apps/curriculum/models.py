from django.core.exceptions import ValidationError
# Exceções específicas para validação de modelos.
from django.db import models
# Campos e utilidades de modelagem do Django.
from django.db.models.signals import m2m_changed
# Sinal para acompanhar mudanças em relacionamentos ManyToMany.
from django.dispatch import receiver
# Decorador para registrar handlers de sinais.

from core.models import BaseCodeModel, BaseNamedCodeModel
# Modelos base com código, nome e auditoria.

from apps.school.models import Grade
# Modelo de classe/ano escolar.


class CurriculumArea(BaseNamedCodeModel):
    """Área curricular que agrupa disciplinas dentro de um tenant."""

    # Prefixo usado na geração automática de código.
    CODE_PREFIX = "CAR"

    def __str__(self):
        """Retorna o nome para representação textual."""
        return self.name

    class Meta:
        # Rótulos administrativos.
        verbose_name = "Área curricular"
        verbose_name_plural = "Áreas curriculares"
        # Garante unicidade de nome por tenant enquanto ativo.
        constraints = [
            models.UniqueConstraint(
                fields=["tenant_id", "name"],
                condition=models.Q(deleted_at__isnull=True),
                name="unique_curriculumarea_name_per_tenant",
            ),
        ]


class Subject(BaseNamedCodeModel):
    """Disciplina pertencente a uma área curricular e ciclo de ensino."""

    # Prefixo de código automático.
    CODE_PREFIX = "SUB"
    # Área curricular associada.
    area = models.ForeignKey(CurriculumArea, on_delete=models.CASCADE, verbose_name="Área")
    # Ciclo (1º ou 2º).
    cycle = models.IntegerField(verbose_name="Ciclo")

    def clean(self):
        """Valida coerência de tenant e ciclo."""
        # Obtém tenant da área, se houver.
        area_tenant = (self.area.tenant_id or "").strip() if self.area_id else ""
        # Sincroniza tenant da disciplina com o da área.
        if area_tenant:
            if self.tenant_id and self.tenant_id != area_tenant:
                raise ValidationError({"tenant_id": "O tenant da disciplina deve coincidir com o tenant da área curricular."})
            if not self.tenant_id:
                self.tenant_id = area_tenant
        # Aceita apenas ciclos 1 ou 2.
        if self.cycle not in {1, 2}:
            raise ValidationError({"cycle": "O ciclo da disciplina deve ser 1 ou 2."})

    def save(self, *args, **kwargs):
        """Executa validação completa antes de persistir."""
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        """Representação textual da disciplina."""
        return self.name

    @property
    def competencia_set(self):
        """Alias legado para acessar competencies via ORM."""
        return self.competency_set

    class Meta:
        # Rótulo singular e plural.
        verbose_name = "Disciplina"
        verbose_name_plural = "Disciplinas"
        # Ordena alfabeticamente.
        ordering = ["name"]


class SubjectSpecialty(BaseNamedCodeModel):
    """Especialidade vinculada a uma disciplina específica."""

    # Prefixo de código automático.
    CODE_PREFIX = "SSP"
    # Disciplina dona da especialidade.
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name="specialties", verbose_name="Disciplina")

    def clean(self):
        """Força alinhamento de tenant com a disciplina."""
        # Tenant da disciplina de referência.
        subject_tenant = (self.subject.tenant_id or "").strip() if self.subject_id else ""
        # Replica tenant se existir e verifica conflitos.
        if subject_tenant:
            if self.tenant_id and self.tenant_id != subject_tenant:
                raise ValidationError({"tenant_id": "O tenant da especialidade deve coincidir com o tenant da disciplina."})
            if not self.tenant_id:
                self.tenant_id = subject_tenant

    def save(self, *args, **kwargs):
        """Valida antes de persistir."""
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        """Exibe disciplina e especialidade."""
        return f"{self.subject.name} - {self.name}"

    class Meta:
        # Rótulos administrativos.
        verbose_name = "Especialidade por disciplina"
        verbose_name_plural = "Especialidades por disciplina"
        # Ordena por disciplina e nome.
        ordering = ["subject__name", "name"]
        # Unicidade de nome por disciplina enquanto ativo.
        constraints = [
            models.UniqueConstraint(
                fields=["subject", "name"],
                condition=models.Q(deleted_at__isnull=True),
                name="unique_subject_specialty_active",
            ),
        ]


class Competency(BaseNamedCodeModel):
    """Competência ligada a disciplina, ciclo e classe, com área curricular."""

    # Prefixo de código automático.
    CODE_PREFIX = "COM"

    def __init__(self, *args, area=None, **kwargs):
        """Permite inicializar área via string, criando-a se necessário."""
        # Aceita nome de área como string e normaliza para objeto.
        if area is not None and not hasattr(area, "pk") and isinstance(area, str):
            normalized = area.strip()
            if normalized:
                area_obj, _ = CurriculumArea.objects.get_or_create(name=normalized)
                kwargs["area"] = area_obj
            else:
                kwargs["area"] = None
        else:
            # Mantém área quando já é objeto.
            if area is not None:
                kwargs["area"] = area
        # Chama construtor do modelo base.
        super().__init__(*args, **kwargs)

    # Descrição textual da competência.
    description = models.TextField(blank=True, verbose_name="Descrição")
    # Área curricular vinculada (pode ser nula).
    area = models.ForeignKey(
        CurriculumArea,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        verbose_name="Área",
    )
    # Ciclo de ensino.
    cycle = models.IntegerField(verbose_name="Ciclo")
    # Disciplina relacionada (opcional).
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, null=True, blank=True, verbose_name="Disciplina")
    # Classe/ano opcional.
    grade = models.ForeignKey(Grade, null=True, blank=True, on_delete=models.PROTECT, verbose_name="Classe")

    def clean(self):
        """Normaliza área, valida tenants e consistência de ciclo."""
        # Trata payload legado que envia área como string.
        if isinstance(self.area, str):
            area_name = self.area.strip()
            if area_name:
                self.area, _ = CurriculumArea.objects.get_or_create(name=area_name)
            else:
                self.area = None

        # Tenants derivados de disciplina e área.
        subject_tenant = (self.subject.tenant_id or "").strip() if self.subject_id else ""
        area_tenant = (self.area.tenant_id or "").strip() if self.area_id else ""

        # Herdar área da disciplina quando não informado.
        if self.subject_id and not self.area_id:
            self.area = self.subject.area
            area_tenant = (self.area.tenant_id or "").strip() if self.area_id else ""

        # Corrigir área em caso de divergência com disciplina.
        if self.subject_id and self.area_id and self.subject.area_id != self.area_id:
            # Favor disciplina para manter compatibilidade com payloads legados.
            self.area = self.subject.area
            area_tenant = (self.area.tenant_id or "").strip() if self.area_id else ""

        # Exige sempre uma área válida.
        if not self.area_id:
            raise ValidationError({"area": "Informe uma área para a competência."})

        # Valida coincidência de tenant entre disciplina e área.
        if subject_tenant and area_tenant and subject_tenant != area_tenant:
            raise ValidationError({"tenant_id": "A disciplina e a área devem pertencer ao mesmo tenant."})

        # Ajusta tenant a partir da disciplina.
        if subject_tenant:
            if self.tenant_id and self.tenant_id != subject_tenant:
                raise ValidationError({"tenant_id": "O tenant da competência deve coincidir com o tenant da disciplina."})
            if not self.tenant_id:
                self.tenant_id = subject_tenant
        # Ajusta tenant a partir da área.
        if area_tenant:
            if self.tenant_id and self.tenant_id != area_tenant:
                raise ValidationError({"tenant_id": "O tenant da competência deve coincidir com o tenant da área."})
            if not self.tenant_id:
                self.tenant_id = area_tenant

        # Ciclo permitido apenas 1 ou 2.
        if self.cycle not in {1, 2}:
            raise ValidationError({"cycle": "O ciclo da competência deve ser 1 ou 2."})
        # Disciplina deve pertencer ao mesmo ciclo.
        if self.subject and self.subject.cycle != self.cycle:
            raise ValidationError({"subject": "A disciplina deve pertencer ao mesmo ciclo da competência."})
        # Se classe informada, sincroniza ciclo a partir dela.
        if self.grade_id:
            self.cycle = self.grade.cycle

    def save(self, *args, **kwargs):
        """Garante validação completa antes de salvar."""
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        """Exibe nome da competência."""
        return self.name

    class Meta:
        # Rótulos administrativos.
        verbose_name = "Competência"
        verbose_name_plural = "Competências"
        # Ordenação padrão.
        ordering = ["name"]


class LearningOutcome(BaseCodeModel):
    """Resultado de aprendizagem associado a disciplina/classe com taxonomia."""

    # Prefixo de código automático.
    CODE_PREFIX = "OUT"
    # Ativa geração automática de código no modelo base.
    AUTO_CODE = True
    # Níveis cognitivos (Bloom).
    TAXONOMY_LEVEL_CHOICES = [
        ("remember", "Recordar"),
        ("understand", "Compreender"),
        ("apply", "Aplicar"),
        ("analyze", "Analisar"),
        ("evaluate", "Avaliar"),
        ("create", "Criar"),
    ]
    # Dimensões de conhecimento.
    KNOWLEDGE_DIMENSION_CHOICES = [
        ("factual", "Factual"),
        ("conceptual", "Conceitual"),
        ("procedural", "Procedimental"),
        ("metacognitive", "Metacognitivo"),
    ]

    # Código identificador (gerado automaticamente).
    code = models.CharField(max_length=60, verbose_name="Código")
    # Descrição do resultado esperado.
    description = models.TextField(verbose_name="Descrição")
    # Disciplina vinculada (opcional).
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, null=True, blank=True, verbose_name="Disciplina")
    # Classe vinculada (opcional).
    grade = models.ForeignKey(Grade, null=True, blank=True, on_delete=models.PROTECT, verbose_name="Classe")
    # Ciclo associado.
    cycle = models.IntegerField(verbose_name="Ciclo")
    # Nível cognitivo dentro da taxonomia.
    taxonomy_level = models.CharField(max_length=20, choices=TAXONOMY_LEVEL_CHOICES, verbose_name="Nível cognitivo")
    # Dimensão do conhecimento.
    knowledge_dimension = models.CharField(
        max_length=20,
        choices=KNOWLEDGE_DIMENSION_CHOICES,
        blank=True,
        verbose_name="Dimensão do conhecimento",
    )
    # Flag de ativação.
    active = models.BooleanField(default=True, verbose_name="Ativo")
    # Competências relacionadas via tabela intermediária.
    competencies = models.ManyToManyField(
        Competency,
        through="CompetencyOutcome",
        related_name="learning_outcomes",
        verbose_name="Competências",
    )

    def clean(self):
        """Valida tenant, vínculos e ciclo."""
        # Sanitiza tenant.
        self.tenant_id = (self.tenant_id or "").strip()
        # Tenant obrigatório sempre.
        if not self.tenant_id:
            raise ValidationError({"tenant_id": "tenant_id é obrigatório. Envie o header X-Tenant-ID ou configure tenant_id no seu perfil (UserProfile)."})
        # Exige disciplina ou classe.
        if not self.subject_id and not self.grade_id:
            raise ValidationError({"subject": "Informe uma disciplina ou classe para o resultado de aprendizagem."})

        # Sincroniza ciclo com a classe, se presente.
        if self.grade_id:
            self.cycle = self.grade.cycle

        # Se houver disciplina, alinhar ciclo.
        if self.subject_id:
            if self.cycle and self.subject.cycle != self.cycle:
                raise ValidationError({"subject": "A disciplina deve pertencer ao mesmo ciclo."})
            self.cycle = self.subject.cycle

        # Ciclo válido apenas 1 ou 2.
        if self.cycle not in {1, 2}:
            raise ValidationError({"cycle": "O ciclo deve ser 1 ou 2."})

    def save(self, *args, **kwargs):
        """Executa validação completa e salva."""
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        """Mostra código e primeira parte da descrição."""
        return f"{self.code} - {self.description[:40]}"

    class Meta:
        # Rótulos administrativos.
        verbose_name = "Resultado de aprendizagem"
        verbose_name_plural = "Resultados de aprendizagem"
        # Ordenação por código.
        ordering = ["code"]
        # Impede duplicidade ativa por tenant, código e escopo.
        constraints = [
            models.UniqueConstraint(
                fields=["tenant_id", "code", "subject", "grade"],
                condition=models.Q(deleted_at__isnull=True),
                name="unique_learning_outcome_active",
            ),
        ]


class CompetencyOutcome(BaseCodeModel):
    """Relaciona uma competência a um resultado de aprendizagem com peso."""

    # Prefixo para código automático.
    CODE_PREFIX = "COT"
    # Competência vinculada.
    competency = models.ForeignKey(Competency, on_delete=models.CASCADE, verbose_name="Competência")
    # Resultado de aprendizagem vinculado.
    outcome = models.ForeignKey(LearningOutcome, on_delete=models.CASCADE, verbose_name="Resultado de aprendizagem")
    # Peso do alinhamento.
    weight = models.DecimalField(max_digits=5, decimal_places=2, default=100, verbose_name="Peso")
    # Campo opcional para observações.
    notes = models.CharField(max_length=255, blank=True, verbose_name="Observações")

    def clean(self):
        """Valida tenant, pesos e consistência entre competência e resultado."""
        # Tenant derivado do resultado, quando presente.
        outcome_tenant = (self.outcome.tenant_id or "").strip() if self.outcome_id else ""
        # Replica ou confere tenant.
        if outcome_tenant:
            if self.tenant_id and self.tenant_id != outcome_tenant:
                raise ValidationError({"tenant_id": "O tenant do alinhamento deve coincidir com o resultado."})
            if not self.tenant_id:
                self.tenant_id = outcome_tenant
        # Tenant obrigatório.
        if not (self.tenant_id or "").strip():
            raise ValidationError({"tenant_id": "tenant_id é obrigatório. Envie o header X-Tenant-ID ou configure tenant_id no seu perfil (UserProfile)."})
        # Peso precisa estar no intervalo (0, 100].
        if self.weight <= 0 or self.weight > 100:
            raise ValidationError({"weight": "O peso deve estar entre 0 e 100."})

        # Checagens de consistência entre competência e resultado.
        if self.outcome_id:
            if self.outcome.subject_id and self.competency.subject_id and self.outcome.subject_id != self.competency.subject_id:
                raise ValidationError({"competency": "A competência deve pertencer à mesma disciplina do resultado."})
            if self.outcome.grade_id and self.competency.grade_id and self.outcome.grade_id != self.competency.grade_id:
                raise ValidationError({"competency": "A competência deve pertencer à mesma classe do resultado."})
            if self.outcome.cycle and self.competency.cycle and self.outcome.cycle != self.competency.cycle:
                raise ValidationError({"competency": "A competência deve pertencer ao mesmo ciclo do resultado."})

    def save(self, *args, **kwargs):
        """Valida e salva o mapeamento."""
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        """Representa alinhamento pelo código do resultado e nome da competência."""
        return f"{self.outcome.code} - {self.competency.name}"

    class Meta:
        # Rótulos administrativos.
        verbose_name = "Alinhamento competência-resultado"
        verbose_name_plural = "Alinhamentos competência-resultado"
        # Ordenação padrão.
        ordering = ["outcome__code", "competency__name"]
        # Impede duplicidade ativa de combinação.
        constraints = [
            models.UniqueConstraint(
                fields=["tenant_id", "competency", "outcome"],
                condition=models.Q(deleted_at__isnull=True),
                name="unique_competency_outcome_active",
            ),
        ]


class BaseCurriculum(BaseCodeModel):
    """Currículo base, comum a todos os tenants, com competências definidas."""

    # Prefixo de código automático.
    CODE_PREFIX = "BCU"
    # Ciclo ao qual o currículo pertence.
    cycle = models.IntegerField(verbose_name="Ciclo")
    # Competências que compõem o currículo.
    competencies = models.ManyToManyField(Competency, verbose_name="Competências")

    def clean(self):
        """Restringe ciclo aos valores 1 ou 2."""
        if self.cycle not in {1, 2}:
            raise ValidationError({"cycle": "The base curriculum cycle must be 1 or 2."})

    def save(self, *args, **kwargs):
        """Valida e salva currículo base."""
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        """Exibe ciclo do currículo base."""
        return f"Base curriculum cycle {self.cycle}"

    class Meta:
        # Rótulos administrativos.
        verbose_name = "Currículo base"
        verbose_name_plural = "Currículos base"
        # Ordena por ciclo.
        ordering = ["cycle"]


class LocalCurriculum(BaseCodeModel):
    """Currículo complementar de um tenant, adicionando competências ao base."""

    # Prefixo de código automático.
    CODE_PREFIX = "LCU"
    # Ciclo de ensino.
    cycle = models.IntegerField(verbose_name="Ciclo")
    # Competências extras do tenant.
    additional_competencies = models.ManyToManyField(Competency, blank=True, verbose_name="Competências adicionais")

    def clean(self):
        """Valida ciclo e presença do tenant."""
        if self.cycle not in {1, 2}:
            raise ValidationError({"cycle": "The local curriculum cycle must be 1 or 2."})
        if not self.tenant_id.strip():
            raise ValidationError({"tenant_id": "tenant_id é obrigatório. Envie o header X-Tenant-ID ou configure tenant_id no seu perfil (UserProfile)."})

    def save(self, *args, **kwargs):
        """Valida e persiste currículo local."""
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        """Mostra tenant e ciclo."""
        return f"Local curriculum {self.tenant_id} cycle {self.cycle}"

    class Meta:
        # Rótulos administrativos.
        verbose_name = "Currículo local"
        verbose_name_plural = "Currículos locais"
        # Ordena por tenant e ciclo.
        ordering = ["tenant_id", "cycle"]


class SubjectCurriculumPlan(BaseCodeModel):
    """Plano curricular detalhado por disciplina e classe."""

    # Prefixo de código automático.
    CODE_PREFIX = "SCP"
    # Relação 1-para-1 com a oferta da disciplina em uma classe.
    grade_subject = models.OneToOneField(
        "school.GradeSubject",
        on_delete=models.CASCADE,
        related_name="curriculum_plan",
        verbose_name="Disciplina da classe",
    )
    # Objetivos do plano.
    objectives = models.TextField(blank=True, verbose_name="Objetivos")
    # Competências previstas para a disciplina.
    planned_competencies = models.ManyToManyField(
        Competency,
        blank=True,
        related_name="curriculum_plans",
        verbose_name="Competências previstas",
    )
    # Estratégias de ensino.
    methodology = models.TextField(blank=True, verbose_name="Metodologia")
    # Critérios de avaliação.
    assessment_criteria = models.TextField(blank=True, verbose_name="Critérios de avaliação")
    # Flag de ativação.
    active = models.BooleanField(default=True, verbose_name="Ativo")

    def validate_competencies(self, competencies):
        """Confere se competências correspondem à mesma disciplina e ciclo."""
        # Sem grade_subject não há o que validar.
        if not self.grade_subject_id:
            return

        # Ciclo derivado da disciplina.
        subject_cycle = self.grade_subject.subject.cycle
        for competency in competencies:
            # Todas devem pertencer à mesma disciplina.
            if competency.subject_id != self.grade_subject.subject_id:
                raise ValidationError({"planned_competencies": "All competencies must belong to the same subject."})
            # Todas devem respeitar o ciclo.
            if competency.cycle != subject_cycle:
                raise ValidationError({"planned_competencies": "All competencies must belong to the same cycle as the subject."})

    def clean(self):
        """Valida tenant, ciclo e competências planejadas."""
        # Ajusta tenant com base na disciplina da classe.
        if self.grade_subject_id:
            grade_subject_tenant = (self.grade_subject.tenant_id or "").strip()
            if grade_subject_tenant:
                if self.tenant_id and self.tenant_id != grade_subject_tenant:
                    raise ValidationError({"tenant_id": "Curriculum plan tenant must match the grade subject tenant."})
                if not self.tenant_id:
                    self.tenant_id = grade_subject_tenant
        # Tenant obrigatório.
        if not (self.tenant_id or "").strip():
            raise ValidationError({"tenant_id": "tenant_id é obrigatório. Envie o header X-Tenant-ID ou configure tenant_id no seu perfil (UserProfile)."})
        # Quando já existe registro, valida competências associadas.
        if self.pk:
            self.validate_competencies(self.planned_competencies.all())

    def save(self, *args, **kwargs):
        """Executa validação e salva plano."""
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        """Exibe disciplina e classe do plano."""
        return f"Plan {self.grade_subject.subject} - {self.grade_subject.grade}"

    class Meta:
        # Rótulos administrativos.
        verbose_name = "Plano curricular por disciplina"
        verbose_name_plural = "Planos curriculares por disciplina"
        # Ordena por ano letivo e número da classe.
        ordering = ["grade_subject__academic_year__code", "grade_subject__grade__number"]


@receiver(m2m_changed, sender=SubjectCurriculumPlan.planned_competencies.through)
def validate_planned_competencies(sender, instance, action, pk_set, **kwargs):
    """Handler que valida competências antes de adicionar ao plano."""
    # Apenas intercepta inclusões antes da gravação.
    if action != "pre_add" or not pk_set:
        return

    # Recupera competências que serão adicionadas.
    competencies = Competency.objects.filter(pk__in=pk_set)
    # Usa validação do próprio modelo.
    instance.validate_competencies(competencies)
