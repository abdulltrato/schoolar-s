import re

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models


def validar_codigo_ano_letivo(codigo: str):
    if not re.fullmatch(r"\d{4}-\d{4}", codigo):
        raise ValidationError("Use o formato AAAA-AAAA.")

    ano_inicio, ano_fim = [int(valor) for valor in codigo.split("-")]
    if ano_fim != ano_inicio + 1:
        raise ValidationError("O ano letivo deve terminar no ano seguinte ao inicio.")


class AnoLetivo(models.Model):
    codigo = models.CharField(max_length=9, unique=True, verbose_name="Ano Letivo")
    data_inicio = models.DateField(verbose_name="Data de Início")
    data_fim = models.DateField(verbose_name="Data de Fim")
    ativo = models.BooleanField(default=False, verbose_name="Ativo")

    def clean(self):
        validar_codigo_ano_letivo(self.codigo)
        if self.data_fim <= self.data_inicio:
            raise ValidationError({"data_fim": "A data de fim deve ser posterior a data de inicio."})

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        return self.codigo

    class Meta:
        verbose_name = "Ano Letivo"
        verbose_name_plural = "Anos Letivos"
        ordering = ["-codigo"]


class Classe(models.Model):
    numero = models.PositiveSmallIntegerField(unique=True, verbose_name="Classe")
    ciclo = models.PositiveSmallIntegerField(verbose_name="Ciclo")
    nome = models.CharField(max_length=50, blank=True, verbose_name="Nome")

    @staticmethod
    def nivel_ensino_para_classe(numero: int) -> str:
        return "primario" if numero <= 6 else "secundario"

    @staticmethod
    def ciclo_para_classe(numero: int) -> int:
        if numero <= 3 or 7 <= numero <= 9:
            return 1
        return 2

    @property
    def nivel_ensino(self) -> str:
        return self.nivel_ensino_para_classe(self.numero)

    def clean(self):
        if not 1 <= self.numero <= 12:
            raise ValidationError({"numero": "A classe deve estar entre 1 e 12."})

        self.ciclo = self.ciclo_para_classe(self.numero)

        if not self.nome:
            self.nome = f"{self.numero}a Classe"

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        return self.nome or f"{self.numero}a Classe"

    class Meta:
        verbose_name = "Classe"
        verbose_name_plural = "Classes"
        ordering = ["numero"]


class Escola(models.Model):
    codigo = models.CharField(max_length=30, unique=True, verbose_name="Código")
    nome = models.CharField(max_length=150, verbose_name="Nome")
    distrito = models.CharField(max_length=100, blank=True, verbose_name="Distrito")
    provincia = models.CharField(max_length=100, blank=True, verbose_name="Província")
    ativa = models.BooleanField(default=True, verbose_name="Ativa")

    def __str__(self):
        return self.nome

    class Meta:
        verbose_name = "Escola"
        verbose_name_plural = "Escolas"
        ordering = ["nome"]


class Professor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name="Usuário")
    escola = models.ForeignKey(
        Escola,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="professores",
        verbose_name="Escola",
    )
    nome = models.CharField(max_length=100, verbose_name="Nome")
    especialidade = models.CharField(max_length=100, blank=True, verbose_name="Especialidade")

    def __str__(self):
        return self.nome

    class Meta:
        verbose_name = "Professor"
        verbose_name_plural = "Professores"
        ordering = ["nome"]


class Turma(models.Model):
    nome = models.CharField(max_length=50, verbose_name="Nome")
    escola = models.ForeignKey(
        Escola,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="turmas",
        verbose_name="Escola",
    )
    classe = models.ForeignKey(Classe, on_delete=models.PROTECT, null=True, blank=True, verbose_name="Classe")
    ciclo = models.IntegerField(verbose_name="Ciclo")
    ano_letivo = models.ForeignKey(
        AnoLetivo,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        verbose_name="Ano Letivo",
    )
    professor_responsavel = models.ForeignKey(
        Professor,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Director de Turma",
    )

    def clean(self):
        if not self.classe_id:
            raise ValidationError({"classe": "A turma deve estar associada a uma classe."})

        if not self.ano_letivo_id:
            raise ValidationError({"ano_letivo": "A turma deve estar associada a um ano letivo."})

        if self.professor_responsavel_id and self.escola_id and self.professor_responsavel.escola_id:
            if self.professor_responsavel.escola_id != self.escola_id:
                raise ValidationError({"professor_responsavel": "O director de turma deve pertencer a mesma escola."})

        if self.classe_id:
            self.ciclo = self.classe.ciclo

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.nome} - {self.ano_letivo}"

    class Meta:
        verbose_name = "Turma"
        verbose_name_plural = "Turmas"
        ordering = ["ano_letivo__codigo", "classe__numero", "nome"]
        unique_together = ("nome", "classe", "ano_letivo")


class DisciplinaClasse(models.Model):
    ano_letivo = models.ForeignKey(AnoLetivo, on_delete=models.CASCADE, verbose_name="Ano Letivo")
    classe = models.ForeignKey(Classe, on_delete=models.CASCADE, verbose_name="Classe")
    disciplina = models.ForeignKey("curriculo.Disciplina", on_delete=models.CASCADE, verbose_name="Disciplina")
    carga_horaria_semanal = models.PositiveSmallIntegerField(default=0, verbose_name="Carga Horária Semanal")

    def clean(self):
        if self.disciplina_id and self.classe_id and self.disciplina.ciclo != self.classe.ciclo:
            raise ValidationError({"disciplina": "A disciplina deve pertencer ao mesmo ciclo da classe."})

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.disciplina} - {self.classe} ({self.ano_letivo})"

    class Meta:
        verbose_name = "Disciplina da Classe"
        verbose_name_plural = "Disciplinas das Classes"
        ordering = ["ano_letivo__codigo", "classe__numero", "disciplina__nome"]
        unique_together = ("ano_letivo", "classe", "disciplina")


class AlocacaoDocente(models.Model):
    professor = models.ForeignKey(Professor, on_delete=models.CASCADE, verbose_name="Professor")
    turma = models.ForeignKey(Turma, on_delete=models.CASCADE, verbose_name="Turma")
    disciplina_classe = models.ForeignKey(
        DisciplinaClasse,
        on_delete=models.CASCADE,
        verbose_name="Disciplina da Classe",
    )

    def clean(self):
        if self.turma_id and self.disciplina_classe_id:
            if self.turma.classe_id != self.disciplina_classe.classe_id:
                raise ValidationError({"disciplina_classe": "A disciplina deve pertencer a classe da turma."})

            if self.turma.ano_letivo_id != self.disciplina_classe.ano_letivo_id:
                raise ValidationError({"disciplina_classe": "A disciplina deve pertencer ao mesmo ano letivo da turma."})

            if self.professor.escola_id and self.turma.escola_id and self.professor.escola_id != self.turma.escola_id:
                raise ValidationError({"professor": "O professor deve pertencer a mesma escola da turma."})

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.professor} - {self.disciplina_classe.disciplina} - {self.turma}"

    class Meta:
        verbose_name = "Alocação Docente"
        verbose_name_plural = "Alocações Docentes"
        ordering = ["turma__ano_letivo__codigo", "turma__nome", "disciplina_classe__disciplina__nome"]
        unique_together = ("turma", "disciplina_classe")


class Matricula(models.Model):
    aluno = models.ForeignKey("academico.Aluno", on_delete=models.CASCADE, verbose_name="Aluno")
    turma = models.ForeignKey(Turma, on_delete=models.CASCADE, verbose_name="Turma")
    data_matricula = models.DateField(auto_now_add=True, verbose_name="Data da Matrícula")

    def clean(self):
        if self.aluno_id and self.turma_id:
            if self.aluno.ciclo != self.turma.ciclo:
                raise ValidationError("O ciclo da turma deve corresponder ao ciclo do aluno.")
            if self.aluno.classe != self.turma.classe.numero:
                raise ValidationError("A classe da turma deve corresponder a classe do aluno.")

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        return f"Matrícula de {self.aluno} na {self.turma}"

    class Meta:
        unique_together = ("aluno", "turma")
        verbose_name = "Matrícula"
        verbose_name_plural = "Matrículas"
        ordering = ["-data_matricula"]


class AtribuicaoGestao(models.Model):
    CARGO_CHOICES = [
        ("director_turma", "Director de Turma"),
        ("coordenador_classe", "Coordenador de Classe"),
        ("director_ciclo", "Director de Ciclo"),
        ("director_adjunto_pedagogico", "Director Adjunto Pedagógico"),
        ("director_escola", "Director da Escola"),
    ]

    professor = models.ForeignKey(Professor, on_delete=models.CASCADE, verbose_name="Professor")
    escola = models.ForeignKey(Escola, on_delete=models.CASCADE, verbose_name="Escola")
    ano_letivo = models.ForeignKey(AnoLetivo, on_delete=models.CASCADE, verbose_name="Ano Letivo")
    cargo = models.CharField(max_length=40, choices=CARGO_CHOICES, verbose_name="Cargo")
    classe = models.ForeignKey(Classe, null=True, blank=True, on_delete=models.CASCADE, verbose_name="Classe")
    turma = models.ForeignKey(Turma, null=True, blank=True, on_delete=models.CASCADE, verbose_name="Turma")
    ciclo = models.PositiveSmallIntegerField(null=True, blank=True, verbose_name="Ciclo")
    ativo = models.BooleanField(default=True, verbose_name="Ativo")

    def clean(self):
        if self.professor.escola_id and self.professor.escola_id != self.escola_id:
            raise ValidationError({"professor": "O professor deve pertencer a mesma escola da atribuição."})

        if self.turma_id:
            if self.turma.escola_id and self.turma.escola_id != self.escola_id:
                raise ValidationError({"turma": "A turma deve pertencer a mesma escola."})
            if self.turma.ano_letivo_id != self.ano_letivo_id:
                raise ValidationError({"turma": "A turma deve pertencer ao mesmo ano letivo."})

        if self.cargo == "director_turma":
            if not self.turma_id:
                raise ValidationError({"turma": "Director de turma exige uma turma."})
            if self.classe_id or self.ciclo:
                raise ValidationError("Director de turma não deve definir classe ou ciclo separadamente.")
        elif self.cargo == "coordenador_classe":
            if not self.classe_id:
                raise ValidationError({"classe": "Coordenador de classe exige uma classe."})
            if self.turma_id or self.ciclo:
                raise ValidationError("Coordenador de classe não deve definir turma ou ciclo.")
        elif self.cargo == "director_ciclo":
            if self.ciclo not in {1, 2}:
                raise ValidationError({"ciclo": "Director de ciclo exige ciclo 1 ou 2."})
            if self.turma_id or self.classe_id:
                raise ValidationError("Director de ciclo não deve definir turma ou classe.")
        elif self.cargo in {"director_adjunto_pedagogico", "director_escola"}:
            if self.turma_id or self.classe_id or self.ciclo:
                raise ValidationError("Este cargo atua ao nível da escola e não deve definir escopo adicional.")

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.get_cargo_display()} - {self.professor} ({self.ano_letivo})"

    class Meta:
        verbose_name = "Atribuição de Gestão"
        verbose_name_plural = "Atribuições de Gestão"
        ordering = ["ano_letivo__codigo", "escola__nome", "cargo", "professor__nome"]
