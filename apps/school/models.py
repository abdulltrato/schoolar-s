import re

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models


def validate_academic_year_code(code: str):
    if not re.fullmatch(r"\d{4}-\d{4}", code):
        raise ValidationError("Use the YYYY-YYYY format.")

    start_year, end_year = [int(value) for value in code.split("-")]
    if end_year != start_year + 1:
        raise ValidationError("The academic year must end in the following calendar year.")


class AcademicYear(models.Model):
    code = models.CharField(max_length=9, unique=True, verbose_name="Ano letivo")
    start_date = models.DateField(verbose_name="Data de início")
    end_date = models.DateField(verbose_name="Data de fim")
    active = models.BooleanField(default=False, verbose_name="Ativo")

    def clean(self):
        validate_academic_year_code(self.code)
        if self.end_date <= self.start_date:
            raise ValidationError({"end_date": "End date must be later than the start date."})

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        return self.code

    class Meta:
        verbose_name = "Ano letivo"
        verbose_name_plural = "Anos letivos"
        ordering = ["-code"]


class Grade(models.Model):
    number = models.PositiveSmallIntegerField(unique=True, verbose_name="Classe")
    cycle = models.PositiveSmallIntegerField(verbose_name="Ciclo")
    name = models.CharField(max_length=50, blank=True, verbose_name="Nome")

    @staticmethod
    def education_level_for_grade(number: int) -> str:
        return "primary" if number <= 6 else "secondary"

    @staticmethod
    def cycle_for_grade(number: int) -> int:
        if number <= 3 or 7 <= number <= 9:
            return 1
        return 2

    @property
    def education_level(self) -> str:
        return self.education_level_for_grade(self.number)

    def clean(self):
        if not 1 <= self.number <= 12:
            raise ValidationError({"number": "Grade must be between 1 and 12."})

        self.cycle = self.cycle_for_grade(self.number)

        if not self.name:
            self.name = f"Grade {self.number}"

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        return self.name or f"Grade {self.number}"

    class Meta:
        verbose_name = "Classe"
        verbose_name_plural = "Classes"
        ordering = ["number"]


class School(models.Model):
    code = models.CharField(max_length=30, unique=True, verbose_name="Código")
    name = models.CharField(max_length=150, verbose_name="Nome")
    district = models.CharField(max_length=100, blank=True, verbose_name="Distrito")
    province = models.CharField(max_length=100, blank=True, verbose_name="Província")
    active = models.BooleanField(default=True, verbose_name="Ativa")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Escola"
        verbose_name_plural = "Escolas"
        ordering = ["name"]


class Teacher(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name="Usuário")
    school = models.ForeignKey(
        School,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="teachers",
        verbose_name="Escola",
    )
    name = models.CharField(max_length=100, verbose_name="Nome")
    specialty = models.CharField(max_length=100, blank=True, verbose_name="Especialidade")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Professor"
        verbose_name_plural = "Professores"
        ordering = ["name"]


class Classroom(models.Model):
    name = models.CharField(max_length=50, verbose_name="Nome")
    school = models.ForeignKey(
        School,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="classrooms",
        verbose_name="Escola",
    )
    grade = models.ForeignKey(Grade, on_delete=models.PROTECT, null=True, blank=True, verbose_name="Classe")
    cycle = models.IntegerField(verbose_name="Ciclo")
    academic_year = models.ForeignKey(
        AcademicYear,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        verbose_name="Ano letivo",
    )
    lead_teacher = models.ForeignKey(
        Teacher,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Diretor de turma",
    )

    def clean(self):
        if not self.grade_id:
            raise ValidationError({"grade": "A classroom must be linked to a grade."})

        if not self.academic_year_id:
            raise ValidationError({"academic_year": "A classroom must be linked to an academic year."})

        if self.lead_teacher_id and self.school_id and self.lead_teacher.school_id:
            if self.lead_teacher.school_id != self.school_id:
                raise ValidationError({"lead_teacher": "The lead teacher must belong to the same school."})

        if self.grade_id:
            self.cycle = self.grade.cycle

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} - {self.academic_year}"

    class Meta:
        verbose_name = "Turma"
        verbose_name_plural = "Turmas"
        ordering = ["academic_year__code", "grade__number", "name"]
        unique_together = ("name", "grade", "academic_year")


class GradeSubject(models.Model):
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE, verbose_name="Ano letivo")
    grade = models.ForeignKey(Grade, on_delete=models.CASCADE, verbose_name="Classe")
    subject = models.ForeignKey("curriculum.Subject", on_delete=models.CASCADE, verbose_name="Disciplina")
    weekly_workload = models.PositiveSmallIntegerField(default=0, verbose_name="Carga horária semanal")

    def clean(self):
        if self.subject_id and self.grade_id and self.subject.cycle != self.grade.cycle:
            raise ValidationError({"subject": "The subject must belong to the same cycle as the grade."})

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.subject} - {self.grade} ({self.academic_year})"

    class Meta:
        verbose_name = "Disciplina da classe"
        verbose_name_plural = "Disciplinas da classe"
        ordering = ["academic_year__code", "grade__number", "subject__name"]
        unique_together = ("academic_year", "grade", "subject")


class TeachingAssignment(models.Model):
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, verbose_name="Professor")
    classroom = models.ForeignKey(Classroom, on_delete=models.CASCADE, verbose_name="Turma")
    grade_subject = models.ForeignKey(
        GradeSubject,
        on_delete=models.CASCADE,
        verbose_name="Disciplina da classe",
    )

    def clean(self):
        if self.classroom_id and self.grade_subject_id:
            if self.classroom.grade_id != self.grade_subject.grade_id:
                raise ValidationError({"grade_subject": "The subject must belong to the classroom grade."})

            if self.classroom.academic_year_id != self.grade_subject.academic_year_id:
                raise ValidationError({"grade_subject": "The subject must belong to the same academic year as the classroom."})

            if self.teacher.school_id and self.classroom.school_id and self.teacher.school_id != self.classroom.school_id:
                raise ValidationError({"teacher": "The teacher must belong to the same school as the classroom."})

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.teacher} - {self.grade_subject.subject} - {self.classroom}"

    class Meta:
        verbose_name = "Alocação docente"
        verbose_name_plural = "Alocações docentes"
        ordering = ["classroom__academic_year__code", "classroom__name", "grade_subject__subject__name"]
        unique_together = ("classroom", "grade_subject")


class Enrollment(models.Model):
    student = models.ForeignKey("academic.Student", on_delete=models.CASCADE, verbose_name="Aluno")
    classroom = models.ForeignKey(Classroom, on_delete=models.CASCADE, verbose_name="Turma")
    enrollment_date = models.DateField(auto_now_add=True, verbose_name="Data de matrícula")

    def clean(self):
        if self.student_id and self.classroom_id:
            if self.student.cycle != self.classroom.cycle:
                raise ValidationError("The classroom cycle must match the student cycle.")
            if self.student.grade != self.classroom.grade.number:
                raise ValidationError("The classroom grade must match the student grade.")

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        return f"Enrollment for {self.student} in {self.classroom}"

    class Meta:
        unique_together = ("student", "classroom")
        verbose_name = "Matrícula"
        verbose_name_plural = "Matrículas"
        ordering = ["-enrollment_date"]


class ManagementAssignment(models.Model):
    ROLE_CHOICES = [
        ("homeroom_director", "Diretor de turma"),
        ("grade_coordinator", "Coordenador de classe"),
        ("cycle_director", "Diretor de ciclo"),
        ("deputy_pedagogical_director", "Diretor adjunto pedagógico"),
        ("school_director", "Diretor da escola"),
    ]

    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, verbose_name="Professor")
    school = models.ForeignKey(School, on_delete=models.CASCADE, verbose_name="Escola")
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE, verbose_name="Ano letivo")
    role = models.CharField(max_length=40, choices=ROLE_CHOICES, verbose_name="Cargo")
    grade = models.ForeignKey(Grade, null=True, blank=True, on_delete=models.CASCADE, verbose_name="Classe")
    classroom = models.ForeignKey(Classroom, null=True, blank=True, on_delete=models.CASCADE, verbose_name="Turma")
    cycle = models.PositiveSmallIntegerField(null=True, blank=True, verbose_name="Ciclo")
    active = models.BooleanField(default=True, verbose_name="Ativo")

    def clean(self):
        if self.teacher.school_id and self.teacher.school_id != self.school_id:
            raise ValidationError({"teacher": "The teacher must belong to the same school as the assignment."})

        if self.classroom_id:
            if self.classroom.school_id and self.classroom.school_id != self.school_id:
                raise ValidationError({"classroom": "The classroom must belong to the same school."})
            if self.classroom.academic_year_id != self.academic_year_id:
                raise ValidationError({"classroom": "The classroom must belong to the same academic year."})

        if self.role == "homeroom_director":
            if not self.classroom_id:
                raise ValidationError({"classroom": "A homeroom director assignment requires a classroom."})
            if self.grade_id or self.cycle:
                raise ValidationError("A homeroom director assignment must not define grade or cycle separately.")
        elif self.role == "grade_coordinator":
            if not self.grade_id:
                raise ValidationError({"grade": "A grade coordinator assignment requires a grade."})
            if self.classroom_id or self.cycle:
                raise ValidationError("A grade coordinator assignment must not define classroom or cycle.")
        elif self.role == "cycle_director":
            if self.cycle not in {1, 2}:
                raise ValidationError({"cycle": "A cycle director assignment requires cycle 1 or 2."})
            if self.classroom_id or self.grade_id:
                raise ValidationError("A cycle director assignment must not define classroom or grade.")
        elif self.role in {"deputy_pedagogical_director", "school_director"}:
            if self.classroom_id or self.grade_id or self.cycle:
                raise ValidationError("A school-level role must not define extra scope.")

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.get_role_display()} - {self.teacher} ({self.academic_year})"

    class Meta:
        verbose_name = "Atribuição de gestão"
        verbose_name_plural = "Atribuições de gestão"
        ordering = ["academic_year__code", "school__name", "role", "teacher__name"]
