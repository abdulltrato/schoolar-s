from django.db import models
from django.core.exceptions import ValidationError


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
    ciclo = models.IntegerField(verbose_name="Ciclo")  # 1 or 2

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
        ordering = ['nome']


class Competencia(models.Model):
    AREA_CHOICES = [
        ('linguagem_comunicacao', 'Linguagem e Comunicação'),
        ('saber_cientifico_tecnologico', 'Saber Científico e Tecnológico'),
        ('raciocinio_resolucao_problemas', 'Raciocínio e Resolução de Problemas'),
        ('desenvolvimento_pessoal_autonomia', 'Desenvolvimento Pessoal e Autonomia'),
        ('relacionamento_interpessoal', 'Relacionamento Interpessoal'),
        ('bem_estar_saude_ambiente', 'Bem-estar, Saúde e Ambiente'),
        ('sensibilidade_estetica_artistica', 'Sensibilidade Estética e Artística'),
    ]

    nome = models.CharField(max_length=200, verbose_name="Nome")
    descricao = models.TextField(blank=True, verbose_name="Descrição")
    area = models.CharField(max_length=50, choices=AREA_CHOICES, verbose_name="Área")
    ciclo = models.IntegerField(verbose_name="Ciclo")
    disciplina = models.ForeignKey(Disciplina, on_delete=models.CASCADE, null=True, blank=True, verbose_name="Disciplina")

    def clean(self):
        if self.ciclo not in {1, 2}:
            raise ValidationError({"ciclo": "O ciclo da competência deve ser 1 ou 2."})
        if self.disciplina and self.disciplina.ciclo != self.ciclo:
            raise ValidationError({"disciplina": "A disciplina deve pertencer ao mesmo ciclo da competência."})

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        return self.nome

    class Meta:
        verbose_name = "Competência"
        verbose_name_plural = "Competências"
        ordering = ['nome']


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
        ordering = ['ciclo']


class CurriculoLocal(models.Model):
    tenant_id = models.CharField(max_length=50, verbose_name="ID do Tenant")  # Reference to tenant
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
        ordering = ['tenant_id', 'ciclo']
