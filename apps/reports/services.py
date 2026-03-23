from decimal import Decimal

from django.db.models import Avg, Count, Q
from django.utils import timezone

from apps.academic.models import Student
from apps.assessment.models import Assessment, AssessmentPeriod, SubjectPeriodResult
from apps.school.models import (
    AcademicYear,
    AttendanceRecord,
    Classroom,
    Enrollment,
    Grade,
    Invoice,
    ManagementAssignment,
    Payment,
    Teacher,
)


DIRECTOR_ROLES = {
    "homeroom_director": "Diretor de turma",
    "grade_coordinator": "Coordenador de classe",
    "cycle_director": "Diretor de ciclo",
    "deputy_pedagogical_director": "Diretor adjunto pedagógico",
    "school_director": "Diretor da escola",
}


class ReportGenerationService:
    CATALOG = {
        "student_declaration": {
            "label": "Declaração do estudante",
            "scope": "student",
            "requires": ["student"],
        },
        "student_certificate": {
            "label": "Certificado do estudante",
            "scope": "student",
            "requires": ["student"],
        },
        "student_diploma": {
            "label": "Diploma do estudante",
            "scope": "student",
            "requires": ["student"],
        },
        "student_progress_report": {
            "label": "Relatório de aproveitamento do estudante",
            "scope": "student",
            "requires": ["student"],
        },
        "school_statistics": {
            "label": "Relatório estatístico da escola",
            "scope": "school",
            "requires": [],
        },
        "quarterly_grade_sheet": {
            "label": "Pauta trimestral",
            "scope": "school",
            "requires": ["academic_year"],
        },
        "semester_grade_sheet": {
            "label": "Pauta semestral",
            "scope": "school",
            "requires": ["academic_year"],
        },
        "annual_grade_sheet": {
            "label": "Pauta anual",
            "scope": "school",
            "requires": ["academic_year"],
        },
        "students_list": {
            "label": "Lista de estudantes",
            "scope": "school",
            "requires": [],
        },
        "teachers_list": {
            "label": "Lista de professores",
            "scope": "school",
            "requires": [],
        },
        "directors_list": {
            "label": "Lista de diretores e coordenadores",
            "scope": "school",
            "requires": [],
        },
        "students_by_grade_year": {
            "label": "Lista de estudantes por classe e ano",
            "scope": "school",
            "requires": ["academic_year", "grade"],
        },
        "students_by_grade_year_classroom": {
            "label": "Lista de estudantes por classe, ano e turma",
            "scope": "school",
            "requires": ["academic_year", "classroom"],
        },
    }

    STUDENT_KINDS = {
        "student_declaration",
        "student_certificate",
        "student_diploma",
        "student_progress_report",
    }

    @classmethod
    def get_catalog(cls):
        return [{"key": key, **value} for key, value in cls.CATALOG.items()]

    def __init__(self, *, user=None):
        self.user = user
        self.profile = getattr(user, "school_profile", None) if user and getattr(user, "is_authenticated", False) else None

    def generate(self, *, report_kind, student=None, academic_year=None, grade=None, classroom=None, period_scope=None, period_order=None):
        generator = getattr(self, f"_generate_{report_kind}")
        payload = generator(
            student=student,
            academic_year=academic_year,
            grade=grade,
            classroom=classroom,
            period_scope=period_scope,
            period_order=period_order,
        )
        payload["report_kind"] = report_kind
        payload["generated_at"] = timezone.now().isoformat()
        payload["generated_by"] = getattr(self.user, "username", None)
        payload["scope"] = self.CATALOG[report_kind]["scope"]
        return payload

    def report_type_for(self, report_kind):
        return "student" if report_kind in self.STUDENT_KINDS else "school"

    def default_title_for(self, report_kind, payload):
        label = self.CATALOG[report_kind]["label"]
        target = payload.get("student_snapshot", {}).get("name") or payload.get("metadata", {}).get("classroom")
        return f"{label} - {target}" if target else label

    def default_period_for(self, payload):
        metadata = payload.get("metadata", {})
        parts = [metadata.get("academic_year"), metadata.get("period_label")]
        return " | ".join(part for part in parts if part)

    def _base_metadata(self, *, academic_year=None, grade=None, classroom=None, period_label=None):
        return {
            "academic_year": getattr(academic_year, "code", None),
            "grade": getattr(grade, "number", None),
            "classroom": getattr(classroom, "name", None),
            "period_label": period_label,
            "school": getattr(getattr(classroom, "school", None), "name", None) or getattr(getattr(self.profile, "school", None), "name", None),
        }

    def _student_snapshot(self, student, enrollment=None):
        snapshot = {
            "id": student.id,
            "name": student.name,
            "birth_date": student.birth_date.isoformat(),
            "grade": student.grade,
            "cycle": student.cycle,
            "status": student.estado,
            "education_level": student.education_level,
        }
        if enrollment:
            snapshot.update(
                {
                    "classroom": enrollment.classroom.name,
                    "academic_year": enrollment.classroom.academic_year.code,
                    "school": getattr(enrollment.classroom.school, "name", None),
                }
            )
        return snapshot

    def _student_enrollments(self, student, academic_year=None):
        queryset = Enrollment.objects.select_related(
            "classroom",
            "classroom__academic_year",
            "classroom__grade",
            "classroom__school",
        ).filter(student=student)
        if academic_year:
            queryset = queryset.filter(classroom__academic_year=academic_year)
        return queryset.order_by("-classroom__academic_year__code", "classroom__name")

    def _attendance_summary(self, student, academic_year=None):
        records = AttendanceRecord.objects.filter(enrollment__student=student)
        if academic_year:
            records = records.filter(enrollment__classroom__academic_year=academic_year)
        counts = {item["status"]: item["total"] for item in records.values("status").annotate(total=Count("id"))}
        return {
            "total_records": sum(counts.values()),
            "present": counts.get("present", 0),
            "late": counts.get("late", 0),
            "absent": counts.get("absent", 0),
            "justified_absence": counts.get("justified_absence", 0),
        }

    def _performance_summary(self, student, academic_year=None):
        results = SubjectPeriodResult.objects.select_related(
            "period",
            "teaching_assignment__grade_subject__subject",
            "teaching_assignment__classroom__academic_year",
        ).filter(student=student)
        if academic_year:
            results = results.filter(period__academic_year=academic_year)
        rows = []
        for result in results.order_by(
            "period__academic_year__code",
            "period__order",
            "teaching_assignment__grade_subject__subject__name",
        ):
            rows.append(
                {
                    "subject": result.teaching_assignment.grade_subject.subject.name,
                    "period": result.period.name,
                    "period_order": result.period.order,
                    "average": float(result.final_average),
                    "assessments_counted": result.assessments_counted,
                }
            )
        average = results.aggregate(value=Avg("final_average"))["value"]
        return {
            "overall_average": float(average) if average is not None else None,
            "subjects": rows,
        }

    def _school_filter(self, prefix=""):
        if self.profile and self.profile.school_id:
            return {f"{prefix}school_id": self.profile.school_id}
        return {}

    def _tenant_filter(self, prefix=""):
        tenant_id = (getattr(self.profile, "tenant_id", "") or "").strip() if self.profile else ""
        if tenant_id:
            return {f"{prefix}tenant_id": tenant_id}
        return {}

    def _resolve_periods(self, academic_year, period_scope=None, period_order=None):
        periods = list(AssessmentPeriod.objects.filter(academic_year=academic_year).order_by("order"))
        if not periods:
            return [], "Sem períodos configurados"

        period_scope = period_scope or "quarterly"
        if period_scope == "quarterly":
            target_order = period_order or 1
            selected = [period for period in periods if period.order == target_order]
            return selected, f"Trimestre {target_order}"
        if period_scope == "semester":
            half_size = max(1, len(periods) // 2)
            target_order = 1 if (period_order or 1) <= 1 else 2
            selected = periods[:half_size] if target_order == 1 else periods[half_size:]
            return selected, f"Semestre {target_order}"
        return periods, "Ano letivo"

    def _scoped_enrollments(self, *, academic_year=None, grade=None, classroom=None):
        queryset = Enrollment.objects.select_related(
            "student",
            "classroom",
            "classroom__grade",
            "classroom__academic_year",
            "classroom__school",
        )
        school_filter = self._school_filter("classroom__")
        tenant_filter = self._tenant_filter()
        if school_filter:
            queryset = queryset.filter(**school_filter)
        if tenant_filter:
            queryset = queryset.filter(**tenant_filter)
        if academic_year:
            queryset = queryset.filter(classroom__academic_year=academic_year)
        if grade:
            queryset = queryset.filter(classroom__grade=grade)
        if classroom:
            queryset = queryset.filter(classroom=classroom)
        return queryset.order_by("classroom__academic_year__code", "classroom__grade__number", "classroom__name", "student__name")

    def _generate_student_declaration(self, **kwargs):
        return self._generate_student_document(document_name="Declaração", body_template="Declara-se que o estudante encontra-se matriculado e em situação académica regular.", **kwargs)

    def _generate_student_certificate(self, **kwargs):
        return self._generate_student_document(document_name="Certificado", body_template="Certifica-se o percurso académico e a frequência do estudante no período indicado.", **kwargs)

    def _generate_student_diploma(self, **kwargs):
        return self._generate_student_document(document_name="Diploma", body_template="Reconhece-se a conclusão do ciclo ou classe correspondente pelo estudante.", **kwargs)

    def _generate_student_progress_report(self, *, student=None, academic_year=None, **kwargs):
        enrollments = self._student_enrollments(student, academic_year=academic_year)
        enrollment = enrollments.first()
        effective_year = academic_year or getattr(getattr(enrollment, "classroom", None), "academic_year", None)
        return {
            "title": f"Relatório de aproveitamento - {student.name}",
            "metadata": self._base_metadata(
                academic_year=effective_year,
                classroom=getattr(enrollment, "classroom", None),
                period_label="Ano letivo",
            ),
            "student_snapshot": self._student_snapshot(student, enrollment=enrollment),
            "summary": {
                "attendance": self._attendance_summary(student, academic_year=effective_year),
                "performance": self._performance_summary(student, academic_year=effective_year),
            },
        }

    def _generate_student_document(self, *, student=None, academic_year=None, document_name=None, body_template=None, **kwargs):
        enrollments = self._student_enrollments(student, academic_year=academic_year)
        enrollment = enrollments.first()
        effective_year = academic_year or getattr(getattr(enrollment, "classroom", None), "academic_year", None)
        return {
            "title": f"{document_name} - {student.name}",
            "metadata": self._base_metadata(
                academic_year=effective_year,
                classroom=getattr(enrollment, "classroom", None),
                period_label="Ano letivo",
            ),
            "student_snapshot": self._student_snapshot(student, enrollment=enrollment),
            "summary": {
                "statement": body_template,
                "attendance": self._attendance_summary(student, academic_year=effective_year),
                "performance": self._performance_summary(student, academic_year=effective_year),
            },
        }

    def _generate_school_statistics(self, *, academic_year=None, **kwargs):
        school_filter = self._school_filter()
        tenant_filter = self._tenant_filter()
        enrollment_filter = self._school_filter("classroom__")
        enrollment_tenant_filter = self._tenant_filter()
        assessment_filter = self._school_filter("teaching_assignment__classroom__")
        assessment_tenant_filter = self._tenant_filter()

        if academic_year:
            enrollment_filter["classroom__academic_year"] = academic_year
            assessment_filter["period__academic_year"] = academic_year

        directors_filter = self._school_filter()
        if academic_year:
            directors_filter["academic_year"] = academic_year

        return {
            "title": "Relatório estatístico da escola",
            "metadata": self._base_metadata(academic_year=academic_year, period_label="Ano letivo"),
            "summary": {
                "students": Student.objects.filter(**tenant_filter).count(),
                "teachers": Teacher.objects.filter(**school_filter, **tenant_filter).count(),
                "classrooms": Classroom.objects.filter(**school_filter, academic_year=academic_year).count() if academic_year else Classroom.objects.filter(**school_filter).count(),
                "enrollments": Enrollment.objects.filter(**enrollment_filter, **enrollment_tenant_filter).count(),
                "directors": ManagementAssignment.objects.filter(active=True, **directors_filter).count(),
                "assessments": Assessment.objects.filter(**assessment_filter, **assessment_tenant_filter).count(),
                "invoices": Invoice.objects.filter(**tenant_filter).count(),
                "payments": Payment.objects.filter(**tenant_filter).count(),
            },
        }

    def _generate_quarterly_grade_sheet(self, *, academic_year=None, grade=None, classroom=None, period_order=None, **kwargs):
        return self._generate_grade_sheet(
            academic_year=academic_year,
            grade=grade,
            classroom=classroom,
            period_scope="quarterly",
            period_order=period_order,
        )

    def _generate_semester_grade_sheet(self, *, academic_year=None, grade=None, classroom=None, period_order=None, **kwargs):
        return self._generate_grade_sheet(
            academic_year=academic_year,
            grade=grade,
            classroom=classroom,
            period_scope="semester",
            period_order=period_order,
        )

    def _generate_annual_grade_sheet(self, *, academic_year=None, grade=None, classroom=None, **kwargs):
        return self._generate_grade_sheet(
            academic_year=academic_year,
            grade=grade,
            classroom=classroom,
            period_scope="annual",
        )

    def _generate_grade_sheet(self, *, academic_year=None, grade=None, classroom=None, period_scope=None, period_order=None):
        periods, period_label = self._resolve_periods(academic_year, period_scope=period_scope, period_order=period_order)
        scoped_enrollments = list(self._scoped_enrollments(academic_year=academic_year, grade=grade, classroom=classroom))
        student_ids = [enrollment.student_id for enrollment in scoped_enrollments]
        classroom_ids = list({enrollment.classroom_id for enrollment in scoped_enrollments})

        results = SubjectPeriodResult.objects.select_related(
            "student",
            "period",
            "teaching_assignment__classroom",
            "teaching_assignment__grade_subject__subject",
        ).filter(student_id__in=student_ids, teaching_assignment__classroom_id__in=classroom_ids)
        if periods:
            results = results.filter(period__in=periods)
        else:
            results = results.none()

        indexed_results = {}
        for result in results:
            key = result.student_id
            indexed_results.setdefault(key, []).append(result)

        rows = []
        for enrollment in scoped_enrollments:
            student_results = indexed_results.get(enrollment.student_id, [])
            subjects = []
            total = Decimal("0")
            counted = 0
            for result in sorted(student_results, key=lambda item: item.teaching_assignment.grade_subject.subject.name):
                average = Decimal(result.final_average)
                total += average
                counted += 1
                subjects.append(
                    {
                        "subject": result.teaching_assignment.grade_subject.subject.name,
                        "average": float(average),
                        "period": result.period.name,
                    }
                )
            rows.append(
                {
                    "student_id": enrollment.student_id,
                    "student_name": enrollment.student.name,
                    "classroom": enrollment.classroom.name,
                    "grade": enrollment.classroom.grade.number,
                    "overall_average": float((total / counted).quantize(Decimal("0.01"))) if counted else None,
                    "subjects": subjects,
                }
            )

        return {
            "title": f"Pauta de notas - {period_label}",
            "metadata": self._base_metadata(
                academic_year=academic_year,
                grade=grade,
                classroom=classroom,
                period_label=period_label,
            ),
            "summary": {
                "students_count": len(rows),
                "periods": [{"id": period.id, "name": period.name, "order": period.order} for period in periods],
            },
            "rows": rows,
        }

    def _generate_students_list(self, *, academic_year=None, grade=None, classroom=None, **kwargs):
        enrollments = self._scoped_enrollments(academic_year=academic_year, grade=grade, classroom=classroom)
        rows = [
            {
                "student_id": enrollment.student_id,
                "student_name": enrollment.student.name,
                "grade": enrollment.classroom.grade.number,
                "classroom": enrollment.classroom.name,
                "academic_year": enrollment.classroom.academic_year.code,
                "status": enrollment.student.estado,
            }
            for enrollment in enrollments
        ]
        return {
            "title": "Lista de estudantes",
            "metadata": self._base_metadata(academic_year=academic_year, grade=grade, classroom=classroom),
            "summary": {"total": len(rows)},
            "rows": rows,
        }

    def _generate_teachers_list(self, *, academic_year=None, **kwargs):
        queryset = Teacher.objects.select_related("school", "user").filter(**self._school_filter(), **self._tenant_filter())
        rows = [
            {
                "teacher_id": teacher.id,
                "name": teacher.name,
                "specialty": teacher.specialty,
                "school": getattr(teacher.school, "name", None),
                "username": getattr(teacher.user, "username", None),
            }
            for teacher in queryset.order_by("name")
        ]
        return {
            "title": "Lista de professores",
            "metadata": self._base_metadata(academic_year=academic_year),
            "summary": {"total": len(rows)},
            "rows": rows,
        }

    def _generate_directors_list(self, *, academic_year=None, **kwargs):
        queryset = ManagementAssignment.objects.select_related(
            "teacher",
            "school",
            "academic_year",
            "grade",
            "classroom",
        ).filter(active=True, **self._school_filter())
        if academic_year:
            queryset = queryset.filter(academic_year=academic_year)
        rows = [
            {
                "teacher_id": assignment.teacher_id,
                "teacher_name": assignment.teacher.name,
                "role": assignment.role,
                "role_label": DIRECTOR_ROLES.get(assignment.role, assignment.role),
                "academic_year": assignment.academic_year.code,
                "grade": getattr(assignment.grade, "number", None),
                "classroom": getattr(assignment.classroom, "name", None),
            }
            for assignment in queryset.order_by("role", "teacher__name")
        ]
        return {
            "title": "Lista de diretores e coordenadores",
            "metadata": self._base_metadata(academic_year=academic_year),
            "summary": {"total": len(rows)},
            "rows": rows,
        }

    def _generate_students_by_grade_year(self, *, academic_year=None, grade=None, **kwargs):
        return self._generate_students_list(academic_year=academic_year, grade=grade)

    def _generate_students_by_grade_year_classroom(self, *, academic_year=None, classroom=None, **kwargs):
        return self._generate_students_list(academic_year=academic_year, classroom=classroom)


def resolve_report_dependencies(validated_data):
    dependencies = {}
    if validated_data.get("student"):
        dependencies["student"] = Student.objects.get(pk=validated_data["student"].pk)
    if validated_data.get("academic_year"):
        dependencies["academic_year"] = AcademicYear.objects.get(pk=validated_data["academic_year"].pk)
    if validated_data.get("grade"):
        dependencies["grade"] = Grade.objects.get(pk=validated_data["grade"].pk)
    if validated_data.get("classroom"):
        dependencies["classroom"] = Classroom.objects.select_related("academic_year", "grade", "school").get(pk=validated_data["classroom"].pk)
    return dependencies
