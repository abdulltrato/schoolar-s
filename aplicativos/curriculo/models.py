from django.core.exceptions import ValidationError
from django.db import models
from django.db.models.signals import m2m_changed
from django.dispatch import receiver

from aplicativos.escola.models import Classe


class AreaCurricular(models.Model):
    nome = models.CharField(max_length=100, unique=True, verbose_name="Nome")

    def __str__(self):
        return self.nome

    class Meta:
        verbose_name = "Área Curricular"
        verbose_name_plural = "Áreas Curriculares"


class Disciplina(models.Model):
    nome = models.CharField(max_length=100, verbose_name="Nome")
    area = models.ForeignKey(AreaCurricular, on_delete=models.CASCADE, verbose_name="Área")
    ciclo = models.IntegerField(verbose_name="Ciclo")

    def clean(self):
        if self.ciclo not in {1, 2}:
            raise ValidationError({"ciclo": "O ciclo da disciplina deve ser 1 ou 2."})

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        return self.nome

    class Meta:
        verbose_name = "Disciplina"
        verbose_name_plural = "Disciplinas"
        ordering = ["nome"]


class Competencia(models.Model):
    AREA_CHOICES = [
        ("linguagem_comunicacao", "Linguagem e Comunicação"),
        ("saber_cientifico_tecnologico", "Saber Científico e Tecnológico"),
        ("raciocinio_resolucao_problemas", "Raciocínio e Resolução de Problemas"),
        ("desenvolvimento_pessoal_autonomia", "Desenvolvimento Pessoal e Autonomia"),
        ("relacionamento_interpessoal", "Relacionamento Interpessoal"),
        ("bem_estar_saude_ambiente", "Bem-estar, Saúde e Ambiente"),
        ("sensibilidade_estetica_artistica", "Sensibilidade Estética e Artística"),
    ]

    nome = models.CharField(max_length=200, verbose_name="Nome")
    descricao = models.TextField(blank=True, verbose_name="Descrição")
    area = models.CharField(max_length=50, choices=AREA_CHOICES, verbose_name="Área")
    ciclo = models.IntegerField(verbose_name="Ciclo")
    disciplina = models.ForeignKey(Disciplina, on_delete=models.CASCADE, null=True, blank=True, verbose_name="Disciplina")
    classe = models.ForeignKey(Classe, null=True, blank=True, on_delete=models.PROTECT, verbose_name="Classe")

    def clean(self):
        if self.ciclo not in {1, 2}:
            raise ValidationError({"ciclo": "O ciclo da competência deve ser 1 ou 2."})
        if self.disciplina and self.disciplina.ciclo != self.ciclo:
            raise ValidationError({"disciplina": "A disciplina deve pertencer ao mesmo ciclo da competência."})
        if self.classe_id:
            self.ciclo = self.classe.ciclo

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        return self.nome

    class Meta:
        verbose_name = "Competência"
        verbose_name_plural = "Competências"
        ordering = ["nome"]


class CurriculoBase(models.Model):
    ciclo = models.IntegerField(verbose_name="Ciclo")
    competencias = models.ManyToManyField(Competencia, verbose_name="Competências")

    def clean(self):
        if self.ciclo not in {1, 2}:
            raise ValidationError({"ciclo": "O ciclo do currículo base deve ser 1 ou 2."})

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        return f"Currículo Base Ciclo {self.ciclo}"

    class Meta:
        verbose_name = "Currículo Base"
        verbose_name_plural = "Currículos Base"
        ordering = ["ciclo"]


class CurriculoLocal(models.Model):
    tenant_id = models.CharField(max_length=50, verbose_name="ID do Tenant")
    ciclo = models.IntegerField(verbose_name="Ciclo")
    competencias_adicionais = models.ManyToManyField(Competencia, blank=True, verbose_name="Competências Adicionais")

    def clean(self):
        if self.ciclo not in {1, 2}:
            raise ValidationError({"ciclo": "O ciclo do currículo local deve ser 1 ou 2."})
        if not self.tenant_id.strip():
            raise ValidationError({"tenant_id": "O tenant_id é obrigatório."})

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        return f"Currículo Local {self.tenant_id} Ciclo {self.ciclo}"

    class Meta:
        verbose_name = "Currículo Local"
        verbose_name_plural = "Currículos Locais"
        ordering = ["tenant_id", "ciclo"]


class PlanoCurricularDisciplina(models.Model):
    disciplina_classe = models.OneToOneField(
        "escola.DisciplinaClasse",
        on_delete=models.CASCADE,
        related_name="plano_curricular",
        verbose_name="Disciplina da Classe",
    )
    objetivos = models.TextField(blank=True, verbose_name="Objetivos")
    competencias_previstas = models.ManyToManyField(
        Competencia,
        blank=True,
        related_name="planos_curriculares",
        verbose_name="Competências Previstas",
    )
    metodologia = models.TextField(blank=True, verbose_name="Metodologia")
    criterios_avaliacao = models.TextField(blank=True, verbose_name="Critérios de Avaliação")
    ativo = models.BooleanField(default=True, verbose_name="Ativo")

    def validar_competencias(self, competencias):
        if not self.disciplina_classe_id:
            return

        ciclo_disciplina = self.disciplina_classe.disciplina.ciclo
        for competencia in competencias:
            if competencia.disciplina_id != self.disciplina_classe.disciplina_id:
                raise ValidationError({"competencias_previstas": "Todas as competências devem pertencer à mesma disciplina."})
            if competencia.ciclo != ciclo_disciplina:
                raise ValidationError({"competencias_previstas": "As competências devem pertencer ao mesmo ciclo da disciplina."})

    def clean(self):
        if self.disciplina_classe_id:
            self.validar_competencias(self.competencias_previstas.all())

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.full_clean()
        return self

    def __str__(self):
        return f"Plano {self.disciplina_classe.disciplina} - {self.disciplina_classe.classe}"

    class Meta:
        verbose_name = "Plano Curricular por Disciplina"
        verbose_name_plural = "Planos Curriculares por Disciplina"
        ordering = ["disciplina_classe__ano_letivo__codigo", "disciplina_classe__classe__numero"]


@receiver(m2m_changed, sender=PlanoCurricularDisciplina.competencias_previstas.through)
def validar_competencias_previstas(sender, instance, action, pk_set, **kwargs):
    if action != "pre_add" or not pk_set:
        return

    competencias = Competencia.objects.filter(pk__in=pk_set)
    instance.validar_competencias(competencias)
