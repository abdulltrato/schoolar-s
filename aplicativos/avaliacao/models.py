from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import models


class PeriodoAvaliativo(models.Model):
    ano_letivo = models.ForeignKey("escola.AnoLetivo", on_delete=models.CASCADE, verbose_name="Ano Letivo")
    nome = models.CharField(max_length=50, verbose_name="Nome")
    ordem = models.PositiveSmallIntegerField(verbose_name="Ordem")
    data_inicio = models.DateField(verbose_name="Data de Início")
    data_fim = models.DateField(verbose_name="Data de Fim")
    ativo = models.BooleanField(default=True, verbose_name="Ativo")

    def clean(self):
        if self.data_fim <= self.data_inicio:
            raise ValidationError({"data_fim": "A data de fim deve ser posterior a data de início."})

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.nome} - {self.ano_letivo}"

    class Meta:
        verbose_name = "Período Avaliativo"
        verbose_name_plural = "Períodos Avaliativos"
        ordering = ["ano_letivo__codigo", "ordem"]
        unique_together = ("ano_letivo", "ordem")


class ComponenteAvaliativa(models.Model):
    TIPO_CHOICES = [
        ("acs", "ACS"),
        ("acp", "ACP"),
        ("trabalho_individual", "Trabalho Individual"),
        ("trabalho_grupo", "Trabalho em Grupo"),
        ("teste", "Teste"),
        ("exame", "Exame"),
        ("diagnostica", "Diagnóstica"),
        ("formativa", "Formativa"),
        ("sumativa", "Sumativa"),
        ("outra", "Outra"),
    ]

    periodo = models.ForeignKey(PeriodoAvaliativo, on_delete=models.CASCADE, verbose_name="Período")
    disciplina_classe = models.ForeignKey("escola.DisciplinaClasse", on_delete=models.CASCADE, verbose_name="Disciplina da Classe")
    tipo = models.CharField(max_length=30, choices=TIPO_CHOICES, verbose_name="Tipo")
    nome = models.CharField(max_length=80, verbose_name="Nome")
    peso = models.DecimalField(max_digits=5, decimal_places=2, verbose_name="Peso")
    nota_maxima = models.DecimalField(max_digits=5, decimal_places=2, default=20, verbose_name="Nota Máxima")
    obrigatoria = models.BooleanField(default=True, verbose_name="Obrigatória")

    def clean(self):
        if self.periodo.ano_letivo_id != self.disciplina_classe.ano_letivo_id:
            raise ValidationError({"disciplina_classe": "A disciplina deve pertencer ao mesmo ano letivo do período."})
        if self.peso <= 0 or self.peso > 100:
            raise ValidationError({"peso": "O peso deve estar entre 0 e 100."})
        if self.nota_maxima <= 0:
            raise ValidationError({"nota_maxima": "A nota máxima deve ser positiva."})

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.nome} - {self.disciplina_classe.disciplina}"

    class Meta:
        verbose_name = "Componente Avaliativa"
        verbose_name_plural = "Componentes Avaliativas"
        ordering = ["periodo__ano_letivo__codigo", "periodo__ordem", "disciplina_classe__disciplina__nome", "nome"]
        unique_together = ("periodo", "disciplina_classe", "nome")


class Avaliacao(models.Model):
    TIPO_CHOICES = ComponenteAvaliativa.TIPO_CHOICES

    aluno = models.ForeignKey("academico.Aluno", on_delete=models.CASCADE, verbose_name="Aluno")
    alocacao_docente = models.ForeignKey(
        "escola.AlocacaoDocente",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name="Alocação Docente",
    )
    periodo = models.ForeignKey(
        PeriodoAvaliativo,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Período",
    )
    componente = models.ForeignKey(
        ComponenteAvaliativa,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Componente Avaliativa",
    )
    competencia = models.ForeignKey(
        "curriculo.Competencia",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Competência",
    )
    tipo = models.CharField(max_length=30, choices=TIPO_CHOICES, verbose_name="Tipo")
    data = models.DateField(verbose_name="Data")
    nota = models.DecimalField(max_digits=4, decimal_places=1, null=True, blank=True, verbose_name="Nota")
    comentario = models.TextField(blank=True, verbose_name="Comentário")
    conhecimentos = models.BooleanField(default=False, verbose_name="Conhecimentos")
    habilidades = models.BooleanField(default=False, verbose_name="Habilidades")
    atitudes = models.BooleanField(default=False, verbose_name="Atitudes")

    def clean(self):
        if not self.alocacao_docente_id:
            raise ValidationError({"alocacao_docente": "A alocação docente é obrigatória."})

        turma = self.alocacao_docente.turma
        disciplina = self.alocacao_docente.disciplina_classe.disciplina

        if self.aluno_id:
            if self.aluno.ciclo != turma.ciclo:
                raise ValidationError({"aluno": "Aluno e turma devem pertencer ao mesmo ciclo."})
            if self.aluno.classe != turma.classe.numero:
                raise ValidationError({"aluno": "Aluno e turma devem pertencer a mesma classe."})
            matriculado = self.aluno.matricula_set.filter(turma=turma).exists()
            if not matriculado:
                raise ValidationError({"aluno": "O aluno deve estar matriculado na turma avaliada."})

        if self.competencia_id and self.competencia.disciplina_id != disciplina.id:
            raise ValidationError({"competencia": "A competência deve pertencer a disciplina avaliada."})

        if self.periodo_id and self.periodo.ano_letivo_id != turma.ano_letivo_id:
            raise ValidationError({"periodo": "O período deve pertencer ao mesmo ano letivo da turma."})

        if self.componente_id:
            if self.componente.disciplina_classe_id != self.alocacao_docente.disciplina_classe_id:
                raise ValidationError({"componente": "A componente deve pertencer à mesma disciplina da avaliação."})
            if self.periodo_id and self.componente.periodo_id != self.periodo_id:
                raise ValidationError({"componente": "A componente deve pertencer ao mesmo período."})
            self.tipo = self.componente.tipo
            if self.nota is not None and self.nota > self.componente.nota_maxima:
                raise ValidationError({"nota": "A nota não pode ultrapassar a nota máxima da componente."})

        if self.nota is not None and not 0 <= self.nota <= 20:
            raise ValidationError({"nota": "A nota deve estar entre 0 e 20 valores."})

    def _chave_resultado(self):
        if not self.aluno_id or not self.alocacao_docente_id or not self.periodo_id:
            return None
        return {
            "aluno": self.aluno,
            "alocacao_docente": self.alocacao_docente,
            "periodo": self.periodo,
        }

    def _sincronizar_resultados(self, chaves):
        for chave in chaves:
            if not chave:
                continue
            ResultadoPeriodoDisciplina.recalcular(**chave)

    def save(self, *args, **kwargs):
        chave_anterior = None
        if self.pk:
            anterior = type(self).objects.filter(pk=self.pk).select_related("aluno", "alocacao_docente", "periodo").first()
            if anterior:
                chave_anterior = anterior._chave_resultado()

        self.full_clean()
        resultado = super().save(*args, **kwargs)
        self._sincronizar_resultados([chave_anterior, self._chave_resultado()])
        return resultado

    def delete(self, *args, **kwargs):
        chave_atual = self._chave_resultado()
        resultado = super().delete(*args, **kwargs)
        self._sincronizar_resultados([chave_atual])
        return resultado

    def __str__(self):
        return f"Avaliação {self.tipo} de {self.aluno} em {self.alocacao_docente.disciplina_classe.disciplina}"

    class Meta:
        verbose_name = "Avaliação"
        verbose_name_plural = "Avaliações"
        ordering = ["-data"]


class ResultadoPeriodoDisciplina(models.Model):
    aluno = models.ForeignKey("academico.Aluno", on_delete=models.CASCADE, verbose_name="Aluno")
    alocacao_docente = models.ForeignKey("escola.AlocacaoDocente", on_delete=models.CASCADE, verbose_name="Alocação Docente")
    periodo = models.ForeignKey(PeriodoAvaliativo, on_delete=models.CASCADE, verbose_name="Período")
    media_final = models.DecimalField(max_digits=5, decimal_places=2, default=0, verbose_name="Média Final")
    avaliacoes_consideradas = models.PositiveSmallIntegerField(default=0, verbose_name="Avaliações Consideradas")

    @classmethod
    def recalcular(cls, *, aluno, alocacao_docente, periodo):
        avaliacoes = Avaliacao.objects.filter(
            aluno=aluno,
            alocacao_docente=alocacao_docente,
            periodo=periodo,
            componente__isnull=False,
            nota__isnull=False,
        ).select_related("componente")

        soma_pesos = Decimal("0")
        soma_notas = Decimal("0")

        for avaliacao in avaliacoes:
            peso = Decimal(avaliacao.componente.peso)
            nota_maxima = Decimal(avaliacao.componente.nota_maxima)
            nota = Decimal(avaliacao.nota)
            nota_normalizada = (nota / nota_maxima) * Decimal("20")
            soma_notas += nota_normalizada * peso
            soma_pesos += peso

        total_avaliacoes = avaliacoes.count()
        if soma_pesos <= 0 or total_avaliacoes == 0:
            cls.objects.filter(
                aluno=aluno,
                alocacao_docente=alocacao_docente,
                periodo=periodo,
            ).delete()
            return None

        media_final = soma_notas / soma_pesos

        resultado, _ = cls.objects.update_or_create(
            aluno=aluno,
            alocacao_docente=alocacao_docente,
            periodo=periodo,
            defaults={
                "media_final": media_final.quantize(Decimal("0.01")),
                "avaliacoes_consideradas": total_avaliacoes,
            },
        )
        return resultado

    def clean(self):
        if self.periodo.ano_letivo_id != self.alocacao_docente.turma.ano_letivo_id:
            raise ValidationError({"periodo": "O período deve pertencer ao mesmo ano letivo da alocação."})
        if self.aluno.ciclo != self.alocacao_docente.turma.ciclo or self.aluno.classe != self.alocacao_docente.turma.classe.numero:
            raise ValidationError({"aluno": "O aluno deve pertencer à turma da alocação."})

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        return f"Resultado {self.aluno} - {self.alocacao_docente.disciplina_classe.disciplina} - {self.periodo}"

    class Meta:
        verbose_name = "Resultado por Período e Disciplina"
        verbose_name_plural = "Resultados por Período e Disciplina"
        ordering = ["periodo__ano_letivo__codigo", "periodo__ordem", "aluno__nome"]
        unique_together = ("aluno", "alocacao_docente", "periodo")
