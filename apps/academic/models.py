from django.db import models
from django.core.exceptions import ValidationError


class Student(models.Model):
    CICLO_CHOICES = [
        (1, '1º Ciclo'),
        (2, '2º Ciclo'),
    ]

    ESTADO_CHOICES = [
        ('active', 'Ativo'),
        ('graduado', 'Graduado'),
        ('retido', 'Retido'),
        ('transferido', 'Transferido'),
    ]

    name = models.CharField(max_length=100, verbose_name="Nome")
    birth_date = models.DateField(verbose_name="Data de Nascimento")
    grade = models.IntegerField(verbose_name="Grade")
    cycle = models.IntegerField(choices=CICLO_CHOICES, verbose_name="Ciclo")
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='active', verbose_name="Estado")
    competencies = models.ManyToManyField('curriculum.Competency', through='StudentCompetency', verbose_name="Competências")

    @staticmethod
    def education_level_for_grade(grade: int) -> str:
        if grade is None:
            return ""
        return "primario" if grade <= 6 else "secundario"

    @staticmethod
    def cycle_for_grade(grade: int) -> int:
        if grade is None:
            return 0
        if grade <= 3 or 7 <= grade <= 9:
            return 1
        return 2

    @property
    def education_level(self) -> str:
        return self.education_level_for_grade(self.grade)

    def clean(self):
        if not 1 <= self.grade <= 12:
            raise ValidationError({"grade": "A grade deve estar entre 1 e 12."})
        self.cycle = self.cycle_for_grade(self.grade)

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Aluno"
        verbose_name_plural = "Alunos"
        ordering = ['name']


class StudentCompetency(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, verbose_name="Aluno")
    competency = models.ForeignKey('curriculum.Competency', on_delete=models.CASCADE, verbose_name="Competência")
    nivel = models.DecimalField(max_digits=3, decimal_places=1, default=0.0, verbose_name="Nível")  # e.g., 0.0 to 5.0
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Data de Atualização")

    def clean(self):
        if not 0 <= self.nivel <= 5:
            raise ValidationError({"nivel": "O nível deve estar entre 0.0 e 5.0."})

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    class Meta:
        unique_together = ('student', 'competency')
        verbose_name = "Competência do aluno"
        verbose_name_plural = "Competências dos Alunos"
