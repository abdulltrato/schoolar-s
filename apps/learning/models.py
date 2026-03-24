from django.apps import apps
from django.core.exceptions import ValidationError
from django.db import models

from core.models import TenantModel


class Course(TenantModel):
    MODALITY_CHOICES = [
        ("online", "Online"),
        ("blended", "Híbrido"),
        ("offline", "Presencial"),
    ]

    school = models.ForeignKey("school.School", on_delete=models.CASCADE, verbose_name="Escola")
    title = models.CharField(max_length=180, verbose_name="Título")
    description = models.TextField(blank=True, verbose_name="Descrição")
    modality = models.CharField(max_length=20, choices=MODALITY_CHOICES, default="online", verbose_name="Modalidade")
    active = models.BooleanField(default=True, verbose_name="Ativo")

    def clean(self):
        school_tenant = ""
        if self.school_id and hasattr(self.school, "tenant_id"):
            school_tenant = (self.school.tenant_id or "").strip()
        if self.tenant_id and school_tenant and self.tenant_id != school_tenant:
            raise ValidationError({"tenant_id": "Course tenant must match the school tenant."})
        if school_tenant and not self.tenant_id:
            self.tenant_id = school_tenant
        if not (self.tenant_id or "").strip():
            raise ValidationError({"tenant_id": "tenant_id is required."})

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Curso"
        verbose_name_plural = "Cursos"
        ordering = ["title"]


class CourseOffering(TenantModel):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="offerings", verbose_name="Curso")
    classroom = models.ForeignKey("school.Classroom", on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Turma")
    teacher = models.ForeignKey("school.Teacher", on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Professor")
    academic_year = models.ForeignKey("school.AcademicYear", on_delete=models.CASCADE, verbose_name="Ano letivo")
    start_date = models.DateField(verbose_name="Data de início")
    end_date = models.DateField(verbose_name="Data de fim")
    active = models.BooleanField(default=True, verbose_name="Ativa")

    def clean(self):
        course_tenant = (self.course.tenant_id or "").strip() if self.course_id else ""
        classroom_tenant = (self.classroom.tenant_id or "").strip() if self.classroom_id else ""
        teacher_tenant = (self.teacher.tenant_id or "").strip() if self.teacher_id else ""
        academic_year_tenant = (self.academic_year.tenant_id or "").strip() if self.academic_year_id else ""
        for related_tenant in [classroom_tenant, teacher_tenant]:
            if course_tenant and related_tenant and course_tenant != related_tenant:
                raise ValidationError({"tenant_id": "Course offering relations must belong to the same tenant."})
        if academic_year_tenant and course_tenant and academic_year_tenant != course_tenant:
            raise ValidationError({"academic_year": "Academic year must belong to the same tenant as the course."})
        if self.tenant_id and course_tenant and self.tenant_id != course_tenant:
            raise ValidationError({"tenant_id": "Course offering tenant must match the course tenant."})
        self.tenant_id = self.tenant_id or course_tenant or classroom_tenant or teacher_tenant or academic_year_tenant
        if self.end_date <= self.start_date:
            raise ValidationError({"end_date": "End date must be later than the start date."})
        if self.classroom_id and self.course_id:
            course_school_id = self.course.school_id
            classroom_school_id = self.classroom.school_id
            if course_school_id and classroom_school_id and course_school_id != classroom_school_id:
                raise ValidationError({"classroom": "The classroom must belong to the same school as the course."})
        if self.teacher_id and self.course_id:
            course_school_id = self.course.school_id
            teacher_school_id = self.teacher.school_id
            if course_school_id and teacher_school_id and course_school_id != teacher_school_id:
                raise ValidationError({"teacher": "The teacher must belong to the same school as the course."})
        if self.teacher_id and self.classroom_id:
            teacher_school_id = self.teacher.school_id
            classroom_school_id = self.classroom.school_id
            if teacher_school_id and classroom_school_id and teacher_school_id != classroom_school_id:
                raise ValidationError({"teacher": "The teacher must belong to the same school as the classroom."})

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.course} - {self.academic_year}"

    class Meta:
        verbose_name = "Oferta do curso"
        verbose_name_plural = "Ofertas do curso"
        ordering = ["-academic_year__code", "course__title"]


class Lesson(TenantModel):
    offering = models.ForeignKey(CourseOffering, on_delete=models.CASCADE, related_name="lessons", verbose_name="Oferta")
    title = models.CharField(max_length=180, verbose_name="Título")
    description = models.TextField(blank=True, verbose_name="Descrição")
    scheduled_at = models.DateTimeField(verbose_name="Agendada para")
    duration_minutes = models.PositiveIntegerField(default=45, verbose_name="Duração em minutos")
    meeting_url = models.URLField(blank=True, verbose_name="Link da aula")
    recording_url = models.URLField(blank=True, verbose_name="Link da gravação")
    published = models.BooleanField(default=False, verbose_name="Publicada")

    def clean(self):
        offering_tenant = (self.offering.tenant_id or "").strip() if self.offering_id else ""
        if self.tenant_id and offering_tenant and self.tenant_id != offering_tenant:
            raise ValidationError({"tenant_id": "Lesson tenant must match the offering tenant."})
        if offering_tenant and not self.tenant_id:
            self.tenant_id = offering_tenant
        if not (self.tenant_id or "").strip():
            raise ValidationError({"tenant_id": "tenant_id is required."})

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Aula"
        verbose_name_plural = "Aulas"
        ordering = ["scheduled_at"]


class LessonMaterial(models.Model):
    TYPE_CHOICES = [
        ("link", "Link"),
        ("document", "Documento"),
        ("video", "Vídeo"),
        ("audio", "Áudio"),
        ("other", "Outro"),
    ]

    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name="materials", verbose_name="Aula")
    title = models.CharField(max_length=180, verbose_name="Título")
    material_type = models.CharField(max_length=20, choices=TYPE_CHOICES, verbose_name="Tipo")
    url = models.URLField(verbose_name="Endereço do recurso")
    required = models.BooleanField(default=False, verbose_name="Obrigatório")

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Material da aula"
        verbose_name_plural = "Materiais da aula"
        ordering = ["lesson__scheduled_at", "title"]


class Assignment(TenantModel):
    offering = models.ForeignKey(CourseOffering, on_delete=models.CASCADE, related_name="assignments", verbose_name="Oferta")
    title = models.CharField(max_length=180, verbose_name="Título")
    instructions = models.TextField(blank=True, verbose_name="Instruções")
    opens_at = models.DateTimeField(verbose_name="Abre em")
    due_at = models.DateTimeField(verbose_name="Prazo")
    max_score = models.DecimalField(max_digits=5, decimal_places=2, default=20, verbose_name="Nota máxima")
    published = models.BooleanField(default=False, verbose_name="Publicada")

    def clean(self):
        offering_tenant = (self.offering.tenant_id or "").strip() if self.offering_id else ""
        if self.tenant_id and offering_tenant and self.tenant_id != offering_tenant:
            raise ValidationError({"tenant_id": "Assignment tenant must match the offering tenant."})
        if offering_tenant and not self.tenant_id:
            self.tenant_id = offering_tenant
        if not (self.tenant_id or "").strip():
            raise ValidationError({"tenant_id": "tenant_id is required."})
        if self.due_at <= self.opens_at:
            raise ValidationError({"due_at": "Due date must be later than the opening date."})

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Tarefa"
        verbose_name_plural = "Tarefas"
        ordering = ["-due_at"]


class Submission(TenantModel):
    STATUS_CHOICES = [
        ("draft", "Rascunho"),
        ("submitted", "Submetida"),
        ("graded", "Corrigida"),
    ]

    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE, related_name="submissions", verbose_name="Tarefa")
    student = models.ForeignKey("academic.Student", on_delete=models.CASCADE, verbose_name="Aluno")
    submitted_at = models.DateTimeField(null=True, blank=True, verbose_name="Submetida em")
    text_response = models.TextField(blank=True, verbose_name="Resposta")
    attachment_url = models.URLField(blank=True, verbose_name="Link do anexo")
    score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name="Nota")
    feedback = models.TextField(blank=True, verbose_name="Devolutiva")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="draft", verbose_name="Estado")

    def clean(self):
        assignment_tenant = (self.assignment.tenant_id or "").strip() if self.assignment_id else ""
        student_tenant = (self.student.tenant_id or "").strip() if self.student_id else ""
        if assignment_tenant and student_tenant and assignment_tenant != student_tenant:
            raise ValidationError({"tenant_id": "Submission assignment and student must belong to the same tenant."})
        if self.tenant_id and assignment_tenant and self.tenant_id != assignment_tenant:
            raise ValidationError({"tenant_id": "Submission tenant must match the assignment tenant."})
        if self.tenant_id and student_tenant and self.tenant_id != student_tenant:
            raise ValidationError({"tenant_id": "Submission tenant must match the student tenant."})
        self.tenant_id = self.tenant_id or assignment_tenant or student_tenant
        if not (self.tenant_id or "").strip():
            raise ValidationError({"tenant_id": "tenant_id is required."})
        if self.score is not None and self.score > self.assignment.max_score:
            raise ValidationError({"score": "The score cannot exceed the assignment maximum score."})
        if self.assignment_id and self.student_id:
            offering = self.assignment.offering
            if offering.classroom_id:
                Enrollment = apps.get_model("school", "Enrollment")
                enrolled = Enrollment.objects.filter(student=self.student, classroom=offering.classroom).exists()
                if not enrolled:
                    raise ValidationError({"student": "Student must be enrolled in the offering classroom."})

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.assignment} - {self.student}"

    class Meta:
        unique_together = ("assignment", "student")
        verbose_name = "Submissão"
        verbose_name_plural = "Submissões"
        ordering = ["-submitted_at"]
