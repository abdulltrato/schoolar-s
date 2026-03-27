import re

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models

from core.models import BaseCodeModel, BaseNamedCodeModel, tenant_id_from_user


def validate_academic_year_code(code: str):
    if not re.fullmatch(r"\d{4}-\d{4}", code):
        raise ValidationError("Use the YYYY-YYYY format.")

    start_year, end_year = [int(value) for value in code.split("-")]
    if end_year != start_year + 1:
        raise ValidationError("The academic year must end in the following calendar year.")


class AcademicYear(BaseCodeModel):
    CODE_PREFIX = "ACY"
    AUTO_CODE = False
    code = models.CharField(max_length=9, verbose_name="Ano letivo")
    start_date = models.DateField(verbose_name="Data de início")
    end_date = models.DateField(verbose_name="Data de fim")
    active = models.BooleanField(default=False, verbose_name="Ativo")

    def clean(self):
        validate_academic_year_code(self.code)
        self.tenant_id = (self.tenant_id or "").strip()
        if not self.tenant_id:
            raise ValidationError({"tenant_id": "tenant_id is required."})
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
        constraints = [
            models.UniqueConstraint(
                fields=["tenant_id", "code"],
                condition=models.Q(deleted_at__isnull=True),
                name="unique_academic_year_code_active",
            ),
        ]


class Grade(BaseNamedCodeModel):
    CODE_PREFIX = "GRA"
    number = models.PositiveSmallIntegerField(unique=True, verbose_name="Classe")
    cycle = models.PositiveSmallIntegerField(verbose_name="Ciclo")
    name = models.CharField(max_length=50, blank=True, verbose_name="Nome")

    @staticmethod
    def education_level_for_grade(number: int) -> str:
        return "primario" if number <= 6 else "secundario"

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
            self.name = f"Classe {self.number}"

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        return self.name or f"Grade {self.number}"

    class Meta:
        verbose_name = "Classe"
        verbose_name_plural = "Classes"
        ordering = ["number"]


class School(BaseNamedCodeModel):
    CODE_PREFIX = "ESC"
    code = models.CharField(max_length=30, unique=True, verbose_name="Código")
    tenant_id = models.CharField(max_length=50, unique=True, blank=True, verbose_name="Identificador do tenant")
    district = models.CharField(max_length=100, blank=True, verbose_name="Distrito")
    province = models.CharField(max_length=100, blank=True, verbose_name="Província")
    active = models.BooleanField(default=True, verbose_name="Ativa")

    def clean(self):
        self.tenant_id = (self.tenant_id or self.code or "").strip()
        if not self.tenant_id:
            raise ValidationError({"tenant_id": "tenant_id is required."})

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Escola"
        verbose_name_plural = "Escolas"
        ordering = ["name"]


class Teacher(BaseNamedCodeModel):
    CODE_PREFIX = "TCH"
    TENANT_INHERIT_USER_FIELDS = ("user",)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="Usuário")
    school = models.ForeignKey(
        School,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="teachers",
        verbose_name="Escola",
    )
    specialty = models.CharField(max_length=100, blank=True, verbose_name="Especialidade")

    def clean(self):
        profile_tenant_id = tenant_id_from_user(self.user)
        if profile_tenant_id:
            if self.tenant_id and self.tenant_id != profile_tenant_id:
                raise ValidationError({"tenant_id": "Teacher tenant must match the linked user profile tenant."})
            if not self.tenant_id:
                self.tenant_id = profile_tenant_id
        school_tenant = (self.school.tenant_id or "").strip() if self.school_id else ""
        if school_tenant:
            if self.tenant_id and self.tenant_id != school_tenant:
                raise ValidationError({"tenant_id": "Teacher tenant must match the school tenant."})
            if not self.tenant_id:
                self.tenant_id = school_tenant
        if not (self.tenant_id or "").strip():
            raise ValidationError({"tenant_id": "tenant_id is required."})

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Professor"
        verbose_name_plural = "Professores"
        ordering = ["name"]


class Classroom(BaseNamedCodeModel):
    CODE_PREFIX = "CLS"
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

        school_tenant = (self.school.tenant_id or "").strip() if self.school_id else ""
        academic_tenant = (self.academic_year.tenant_id or "").strip() if self.academic_year_id else ""
        if school_tenant:
            if self.tenant_id and self.tenant_id != school_tenant:
                raise ValidationError({"tenant_id": "Classroom tenant must match the school tenant."})
            if not self.tenant_id:
                self.tenant_id = school_tenant
        if academic_tenant:
            if self.tenant_id and self.tenant_id != academic_tenant:
                raise ValidationError({"tenant_id": "Classroom tenant must match the academic year tenant."})
            if school_tenant and academic_tenant != school_tenant:
                raise ValidationError({"academic_year": "Academic year must belong to the same tenant as the school."})
            if not self.tenant_id:
                self.tenant_id = academic_tenant

        if self.lead_teacher_id and self.school_id and self.lead_teacher.school_id:
            if self.lead_teacher.school_id != self.school_id:
                raise ValidationError({"lead_teacher": "The lead teacher must belong to the same school."})
            if self.lead_teacher.tenant_id:
                if self.tenant_id and self.tenant_id != self.lead_teacher.tenant_id:
                    raise ValidationError({"tenant_id": "Classroom tenant must match the lead teacher tenant."})
                if not self.tenant_id:
                    self.tenant_id = self.lead_teacher.tenant_id

        if self.grade_id:
            self.cycle = self.grade.cycle
        if not (self.tenant_id or "").strip():
            raise ValidationError({"tenant_id": "tenant_id is required."})

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} - {self.academic_year}"

    class Meta:
        verbose_name = "Turma"
        verbose_name_plural = "Turmas"
        ordering = ["academic_year__code", "grade__number", "name"]
        constraints = [
            models.UniqueConstraint(
                fields=["tenant_id", "name", "grade", "academic_year"],
                condition=models.Q(deleted_at__isnull=True),
                name="unique_classroom_active",
            ),
        ]


class GradeSubject(BaseCodeModel):
    CODE_PREFIX = "GDS"
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE, verbose_name="Ano letivo")
    grade = models.ForeignKey(Grade, on_delete=models.CASCADE, verbose_name="Classe")
    subject = models.ForeignKey("curriculum.Subject", on_delete=models.CASCADE, verbose_name="Disciplina")
    weekly_workload = models.PositiveSmallIntegerField(default=0, verbose_name="Carga horária semanal")

    def clean(self):
        if self.subject_id and self.grade_id and self.subject.cycle != self.grade.cycle:
            raise ValidationError({"subject": "The subject must belong to the same cycle as the grade."})
        academic_tenant = (self.academic_year.tenant_id or "").strip() if self.academic_year_id else ""
        if academic_tenant:
            if self.tenant_id and self.tenant_id != academic_tenant:
                raise ValidationError({"tenant_id": "Grade subject tenant must match the academic year tenant."})
            if not self.tenant_id:
                self.tenant_id = academic_tenant
        if not (self.tenant_id or "").strip():
            raise ValidationError({"tenant_id": "tenant_id is required."})

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.subject} - {self.grade} ({self.academic_year})"

    class Meta:
        verbose_name = "Disciplina da classe"
        verbose_name_plural = "Disciplinas da classe"
        ordering = ["academic_year__code", "grade__number", "subject__name"]
        constraints = [
            models.UniqueConstraint(
                fields=["tenant_id", "academic_year", "grade", "subject"],
                condition=models.Q(deleted_at__isnull=True),
                name="unique_grade_subject_active",
            ),
        ]


class TeachingAssignment(BaseCodeModel):
    CODE_PREFIX = "TAS"
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, verbose_name="Professor")
    classroom = models.ForeignKey(Classroom, on_delete=models.CASCADE, verbose_name="Turma")
    grade_subject = models.ForeignKey(
        GradeSubject,
        on_delete=models.CASCADE,
        verbose_name="Disciplina da classe",
    )

    def clean(self):
        if self.classroom_id and self.grade_subject_id:
            teacher_tenant = (self.teacher.tenant_id or "").strip()
            classroom_tenant = (self.classroom.tenant_id or "").strip()
            grade_subject_tenant = (self.grade_subject.tenant_id or "").strip()
            if teacher_tenant and classroom_tenant and teacher_tenant != classroom_tenant:
                raise ValidationError({"tenant_id": "Teacher and classroom must belong to the same tenant."})
            if grade_subject_tenant and classroom_tenant and grade_subject_tenant != classroom_tenant:
                raise ValidationError({"tenant_id": "Grade subject and classroom must belong to the same tenant."})
            if grade_subject_tenant and teacher_tenant and grade_subject_tenant != teacher_tenant:
                raise ValidationError({"tenant_id": "Grade subject and teacher must belong to the same tenant."})
            if self.tenant_id and teacher_tenant and self.tenant_id != teacher_tenant:
                raise ValidationError({"tenant_id": "Teaching assignment tenant must match the teacher tenant."})
            if self.tenant_id and classroom_tenant and self.tenant_id != classroom_tenant:
                raise ValidationError({"tenant_id": "Teaching assignment tenant must match the classroom tenant."})
            if self.tenant_id and grade_subject_tenant and self.tenant_id != grade_subject_tenant:
                raise ValidationError({"tenant_id": "Teaching assignment tenant must match the grade subject tenant."})
            self.tenant_id = self.tenant_id or teacher_tenant or classroom_tenant or grade_subject_tenant
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
        constraints = [
            models.UniqueConstraint(
                fields=["classroom", "grade_subject"],
                condition=models.Q(deleted_at__isnull=True),
                name="unique_teaching_assignment_active",
            ),
        ]


class Enrollment(BaseCodeModel):
    CODE_PREFIX = "MAT"
    student = models.ForeignKey("academic.Student", on_delete=models.CASCADE, verbose_name="Aluno")
    classroom = models.ForeignKey(Classroom, on_delete=models.CASCADE, verbose_name="Turma")
    enrollment_date = models.DateField(auto_now_add=True, verbose_name="Data de matrícula")

    def clean(self):
        if self.student_id and self.classroom_id:
            student_tenant = (self.student.tenant_id or "").strip()
            classroom_tenant = (self.classroom.tenant_id or "").strip()
            if student_tenant and classroom_tenant and student_tenant != classroom_tenant:
                raise ValidationError({"tenant_id": "Enrollment student and classroom must belong to the same tenant."})
            if self.tenant_id and student_tenant and self.tenant_id != student_tenant:
                raise ValidationError({"tenant_id": "Enrollment tenant must match the student tenant."})
            if self.tenant_id and classroom_tenant and self.tenant_id != classroom_tenant:
                raise ValidationError({"tenant_id": "Enrollment tenant must match the classroom tenant."})
            self.tenant_id = self.tenant_id or student_tenant or classroom_tenant
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
        constraints = [
            models.UniqueConstraint(
                fields=["student", "classroom"],
                condition=models.Q(deleted_at__isnull=True),
                name="unique_enrollment_active",
            ),
        ]
        verbose_name = "Matrícula"
        verbose_name_plural = "Matrículas"
        ordering = ["-enrollment_date"]


class ManagementAssignment(BaseCodeModel):
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

    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, verbose_name="Professor")
    school = models.ForeignKey(School, on_delete=models.CASCADE, verbose_name="Escola")
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE, verbose_name="Ano letivo")
    role = models.CharField(max_length=40, choices=ROLE_CHOICES, verbose_name="Cargo")
    grade = models.ForeignKey(Grade, null=True, blank=True, on_delete=models.CASCADE, verbose_name="Classe")
    classroom = models.ForeignKey(Classroom, null=True, blank=True, on_delete=models.CASCADE, verbose_name="Turma")
    cycle = models.PositiveSmallIntegerField(null=True, blank=True, verbose_name="Ciclo")
    active = models.BooleanField(default=True, verbose_name="Ativo")

    def __init__(self, *args, **kwargs):
        role = kwargs.get("role")
        if role is not None:
            kwargs["role"] = self.LEGACY_ROLE_MAP.get(role, role)
        super().__init__(*args, **kwargs)

    def clean(self):
        self.role = self.LEGACY_ROLE_MAP.get(self.role, self.role)
        teacher_tenant = (self.teacher.tenant_id or "").strip() if self.teacher_id else ""
        school_tenant = (self.school.tenant_id or "").strip() if self.school_id else ""
        academic_tenant = (self.academic_year.tenant_id or "").strip() if self.academic_year_id else ""
        if self.tenant_id and teacher_tenant and self.tenant_id != teacher_tenant:
            raise ValidationError({"tenant_id": "Management assignment tenant must match the teacher tenant."})
        if self.tenant_id and school_tenant and self.tenant_id != school_tenant:
            raise ValidationError({"tenant_id": "Management assignment tenant must match the school tenant."})
        if self.tenant_id and academic_tenant and self.tenant_id != academic_tenant:
            raise ValidationError({"tenant_id": "Management assignment tenant must match the academic year tenant."})
        if teacher_tenant and school_tenant and teacher_tenant != school_tenant:
            raise ValidationError({"tenant_id": "Teacher and school must belong to the same tenant."})
        if academic_tenant and school_tenant and academic_tenant != school_tenant:
            raise ValidationError({"tenant_id": "Academic year and school must belong to the same tenant."})
        self.tenant_id = self.tenant_id or teacher_tenant or school_tenant or academic_tenant
        if not (self.tenant_id or "").strip():
            raise ValidationError({"tenant_id": "tenant_id is required."})
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
        self.role = self.LEGACY_ROLE_MAP.get(self.role, self.role)
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.get_role_display()} - {self.teacher} ({self.academic_year})"

    class Meta:
        verbose_name = "Atribuição de gestão"
        verbose_name_plural = "Atribuições de gestão"
        ordering = ["academic_year__code", "school__name", "role", "teacher__name"]


class UserProfile(BaseCodeModel):
    CODE_PREFIX = "UPR"
    ROLE_CHOICES = [
        ("national_admin", "Administrador nacional"),
        ("provincial_admin", "Administrador provincial"),
        ("district_admin", "Administrador distrital"),
        ("school_director", "Diretor da escola"),
        ("teacher", "Professor"),
        ("student", "Aluno"),
        ("guardian", "Encarregado"),
        ("finance_officer", "Responsável financeiro"),
        ("support", "Suporte"),
    ]

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="school_profile",
        verbose_name="Usuário",
    )
    role = models.CharField(max_length=40, choices=ROLE_CHOICES, verbose_name="Papel")
    school = models.ForeignKey(School, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Escola")
    province = models.CharField(max_length=100, blank=True, verbose_name="Província")
    district = models.CharField(max_length=100, blank=True, verbose_name="Distrito")
    active = models.BooleanField(default=True, verbose_name="Ativo")

    def clean(self):
        school_tenant = (self.school.tenant_id or "").strip() if self.school_id else ""
        if school_tenant:
            if self.tenant_id and self.tenant_id != school_tenant:
                raise ValidationError({"tenant_id": "Profile tenant must match the school tenant."})
            if not self.tenant_id:
                self.tenant_id = school_tenant

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username} - {self.role}"

    class Meta:
        verbose_name = "Perfil de utilizador"
        verbose_name_plural = "Perfis de utilizador"
        ordering = ["user__username"]


class AttendanceRecord(BaseCodeModel):
    CODE_PREFIX = "ATT"
    STATUS_CHOICES = [
        ("present", "Presente"),
        ("late", "Atrasado"),
        ("absent", "Falta"),
        ("justified_absence", "Falta justificada"),
    ]

    enrollment = models.ForeignKey(Enrollment, on_delete=models.CASCADE, verbose_name="Matrícula")
    lesson_date = models.DateField(verbose_name="Data da aula")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, verbose_name="Estado")
    notes = models.CharField(max_length=255, blank=True, verbose_name="Observações")

    def clean(self):
        enrollment_tenant = (self.enrollment.tenant_id or "").strip() if self.enrollment_id else ""
        if self.tenant_id and enrollment_tenant and self.tenant_id != enrollment_tenant:
            raise ValidationError({"tenant_id": "Attendance tenant must match the enrollment tenant."})
        if enrollment_tenant and not self.tenant_id:
            self.tenant_id = enrollment_tenant
        if not (self.tenant_id or "").strip():
            raise ValidationError({"tenant_id": "tenant_id is required."})

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.enrollment.student} - {self.lesson_date} - {self.status}"

    class Meta:
        unique_together = ("enrollment", "lesson_date")
        verbose_name = "Presença"
        verbose_name_plural = "Presenças"
        ordering = ["-lesson_date"]


class Announcement(BaseCodeModel):
    CODE_PREFIX = "ANN"
    TENANT_INHERIT_USER_FIELDS = ("author",)
    REQUEST_USER_CREATE_FIELDS = ("author",)
    AUDIENCE_CHOICES = [
        ("school", "Escola"),
        ("classroom", "Turma"),
        ("teachers", "Professores"),
        ("guardians", "Encarregados"),
        ("students", "Alunos"),
    ]

    school = models.ForeignKey(School, on_delete=models.CASCADE, verbose_name="Escola")
    classroom = models.ForeignKey(Classroom, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Turma")
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Autor",
    )
    title = models.CharField(max_length=180, verbose_name="Título")
    message = models.TextField(verbose_name="Mensagem")
    audience = models.CharField(max_length=20, choices=AUDIENCE_CHOICES, verbose_name="Audiência")
    published_at = models.DateTimeField(auto_now_add=True, verbose_name="Publicado em")
    active = models.BooleanField(default=True, verbose_name="Ativo")

    def clean(self):
        classroom_tenant = (self.classroom.tenant_id or "").strip() if self.classroom_id else ""
        school_tenant = (self.school.tenant_id or "").strip() if self.school_id else ""
        author_tenant = tenant_id_from_user(self.author)
        if self.tenant_id and classroom_tenant and self.tenant_id != classroom_tenant:
            raise ValidationError({"tenant_id": "Announcement tenant must match the classroom tenant."})
        if self.tenant_id and school_tenant and self.tenant_id != school_tenant:
            raise ValidationError({"tenant_id": "Announcement tenant must match the school tenant."})
        if self.tenant_id and author_tenant and self.tenant_id != author_tenant:
            raise ValidationError({"tenant_id": "Announcement tenant must match the author tenant."})
        if classroom_tenant and author_tenant and classroom_tenant != author_tenant:
            raise ValidationError({"tenant_id": "Announcement classroom and author must belong to the same tenant."})
        if school_tenant and classroom_tenant and school_tenant != classroom_tenant:
            raise ValidationError({"tenant_id": "Announcement school and classroom must belong to the same tenant."})
        if school_tenant and author_tenant and school_tenant != author_tenant:
            raise ValidationError({"tenant_id": "Announcement school and author must belong to the same tenant."})
        self.tenant_id = self.tenant_id or classroom_tenant or author_tenant or school_tenant
        if not (self.tenant_id or "").strip():
            raise ValidationError({"tenant_id": "tenant_id is required."})

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Comunicado"
        verbose_name_plural = "Comunicados"
        ordering = ["-published_at"]


class Invoice(BaseCodeModel):
    CODE_PREFIX = "INV"
    STATUS_CHOICES = [
        ("draft", "Rascunho"),
        ("issued", "Emitida"),
        ("paid", "Paga"),
        ("overdue", "Em atraso"),
        ("cancelled", "Cancelada"),
    ]

    student = models.ForeignKey("academic.Student", on_delete=models.CASCADE, verbose_name="Aluno")
    school = models.ForeignKey(School, on_delete=models.CASCADE, verbose_name="Escola")
    reference = models.CharField(max_length=40, unique=True, verbose_name="Referência")
    description = models.CharField(max_length=180, verbose_name="Descrição")
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Valor")
    due_date = models.DateField(verbose_name="Vencimento")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="draft", verbose_name="Estado")
    issued_at = models.DateTimeField(auto_now_add=True, verbose_name="Emitida em")

    def clean(self):
        student_tenant = (self.student.tenant_id or "").strip() if self.student_id else ""
        school_tenant = (self.school.tenant_id or "").strip() if self.school_id else ""
        if self.tenant_id and student_tenant and self.tenant_id != student_tenant:
            raise ValidationError({"tenant_id": "Invoice tenant must match the student tenant."})
        if self.tenant_id and school_tenant and self.tenant_id != school_tenant:
            raise ValidationError({"tenant_id": "Invoice tenant must match the school tenant."})
        if student_tenant and school_tenant and student_tenant != school_tenant:
            raise ValidationError({"tenant_id": "Invoice student and school must belong to the same tenant."})
        self.tenant_id = self.tenant_id or student_tenant or school_tenant
        if not (self.tenant_id or "").strip():
            raise ValidationError({"tenant_id": "tenant_id is required."})

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        return self.reference

    class Meta:
        verbose_name = "Fatura"
        verbose_name_plural = "Faturas"
        ordering = ["-issued_at"]


class Payment(BaseCodeModel):
    CODE_PREFIX = "PGT"
    METHOD_CHOICES = [
        ("cash", "Numerário"),
        ("bank_transfer", "Transferência"),
        ("mobile_money", "Carteira móvel"),
        ("card", "Cartão"),
    ]

    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name="payments", verbose_name="Fatura")
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Valor pago")
    payment_date = models.DateField(verbose_name="Data do pagamento")
    method = models.CharField(max_length=20, choices=METHOD_CHOICES, verbose_name="Método")
    reference = models.CharField(max_length=60, blank=True, verbose_name="Referência")
    notes = models.CharField(max_length=255, blank=True, verbose_name="Observações")

    def clean(self):
        invoice_tenant = (self.invoice.tenant_id or "").strip() if self.invoice_id else ""
        if self.tenant_id and invoice_tenant and self.tenant_id != invoice_tenant:
            raise ValidationError({"tenant_id": "Payment tenant must match the invoice tenant."})
        if invoice_tenant and not self.tenant_id:
            self.tenant_id = invoice_tenant

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.invoice.reference} - {self.amount}"

    class Meta:
        verbose_name = "Pagamento"
        verbose_name_plural = "Pagamentos"
        ordering = ["-payment_date"]


class AuditEvent(BaseCodeModel):
    CODE_PREFIX = "AUD"
    ACTION_CHOICES = [
        ("create", "Criação"),
        ("update", "Atualização"),
    ]

    resource = models.CharField(max_length=80, verbose_name="Recurso")
    action = models.CharField(max_length=20, choices=ACTION_CHOICES, verbose_name="Ação")
    object_id = models.PositiveIntegerField(verbose_name="Identificador do objeto")
    object_repr = models.CharField(max_length=255, blank=True, verbose_name="Representação do objeto")
    request_id = models.CharField(max_length=64, blank=True, verbose_name="Identificador da requisição")
    path = models.CharField(max_length=255, blank=True, verbose_name="Rota")
    method = models.CharField(max_length=10, blank=True, verbose_name="Método")
    role = models.CharField(max_length=40, blank=True, verbose_name="Papel")
    username = models.CharField(max_length=150, blank=True, verbose_name="Nome de utilizador")
    changed_fields = models.JSONField(default=list, blank=True, verbose_name="Campos alterados")
    def clean(self):
        self.tenant_id = (self.tenant_id or "").strip()
        if not self.tenant_id:
            raise ValidationError({"tenant_id": "tenant_id is required."})

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.resource}#{self.object_id} {self.action}"

    class Meta:
        verbose_name = "Evento de auditoria"
        verbose_name_plural = "Eventos de auditoria"
        ordering = ["-created_at"]


class AuditAlert(BaseCodeModel):
    CODE_PREFIX = "AAL"
    SEVERITY_CHOICES = [
        ("watch", "Observação"),
        ("elevated", "Elevado"),
    ]

    alert_type = models.CharField(max_length=80, verbose_name="Tipo de alerta")
    severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES, verbose_name="Severidade")
    resource = models.CharField(max_length=80, blank=True, verbose_name="Recurso")
    username = models.CharField(max_length=150, blank=True, verbose_name="Nome de utilizador")
    summary = models.CharField(max_length=255, verbose_name="Resumo")
    details = models.JSONField(default=dict, blank=True, verbose_name="Detalhes")
    acknowledged = models.BooleanField(default=False, verbose_name="Reconhecido")
    def clean(self):
        self.tenant_id = (self.tenant_id or "").strip()
        if not self.tenant_id:
            raise ValidationError({"tenant_id": "tenant_id is required."})

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.alert_type} ({self.severity})"

    class Meta:
        verbose_name = "Alerta de auditoria"
        verbose_name_plural = "Alertas de auditoria"
        ordering = ["-created_at"]
