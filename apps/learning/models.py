from __future__ import annotations

# Public re-exports for Django model discovery and existing imports.
from .models_assignments import Assignment, Submission, SubmissionAttachment  # noqa: F401
from .models_courses import Course, CourseOffering  # noqa: F401
from .models_lessons import Lesson, LessonMaterial  # noqa: F401

__all__ = [
    "Assignment",
    "Course",
    "CourseOffering",
    "Lesson",
    "LessonMaterial",
    "Submission",
]
