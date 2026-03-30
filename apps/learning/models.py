from __future__ import annotations

# Public re-exports for Django model discovery and existing imports.
from .models_assignments import Assignment, Submission, SubmissionAttachment  # noqa: F401
# Tarefas, submissões e anexos.
from .models_courses import Course, CourseOffering, CourseModule  # noqa: F401
# Cursos, ofertas e módulos.
from .models_lessons import Lesson, LessonMaterial  # noqa: F401
# Aulas e materiais.

__all__ = [
    "Assignment",
    "Course",
    "CourseOffering",
    "CourseModule",
    "Lesson",
    "LessonMaterial",
    "Submission",
]
