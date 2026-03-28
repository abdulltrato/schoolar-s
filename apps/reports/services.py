import html
from io import BytesIO

from decimal import Decimal

from django.db.models import Avg, Count, Q
from django.utils import timezone

from apps.academic.models import Student, StudentOutcome
from apps.assessment.models import Assessment, AssessmentPeriod, SubjectPeriodResult
from apps.curriculum.models import LearningOutcome
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
        "bloom_distribution": {
            "label": "Distribuição por Taxonomia de Bloom",
            "scope": "school",
            "requires": ["academic_year"],
        },
        "learning_risk_alerts": {
            "label": "Alertas de risco de aprendizagem",
            "scope": "school",
            "requires": ["academic_year"],
        },
        "learning_intervention_plan": {
            "label": "Plano de intervenção pedagógica",
            "scope": "school",
            "requires": ["academic_year"],
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

    def generate(
        self,
        *,
        report_kind,
        student=None,
        academic_year=None,
        grade=None,
        classroom=None,
        period_scope=None,
        period_order=None,
        emit_alerts=False,
    ):
        generator = getattr(self, f"_generate_{report_kind}")
        payload = generator(
            student=student,
            academic_year=academic_year,
            grade=grade,
            classroom=classroom,
            period_scope=period_scope,
            period_order=period_order,
            emit_alerts=emit_alerts,
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
                "specialty": getattr(teacher.specialty, "name", None),
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

    def _generate_bloom_distribution(self, *, academic_year=None, grade=None, classroom=None, **kwargs):
        enrollments = list(self._scoped_enrollments(academic_year=academic_year, grade=grade, classroom=classroom))
        student_ids = {enrollment.student_id for enrollment in enrollments}
        enrollment_by_student = {}
        for enrollment in enrollments:
            enrollment_by_student.setdefault(enrollment.student_id, enrollment.classroom)

        taxonomy_labels = dict(LearningOutcome.TAXONOMY_LEVEL_CHOICES)
        knowledge_labels = dict(LearningOutcome.KNOWLEDGE_DIMENSION_CHOICES)

        def empty_bucket():
            return {
                "not_started": 0,
                "developing": 0,
                "proficient": 0,
                "advanced": 0,
            }

        overall = empty_bucket()
        taxonomy = {level: empty_bucket() for level in taxonomy_labels}
        knowledge = {level: empty_bucket() for level in knowledge_labels}
        knowledge["unspecified"] = empty_bucket()

        classroom_buckets = {}
        student_buckets = {}

        if not student_ids:
            return {
                "title": "Distribuição por Taxonomia de Bloom",
                "metadata": self._base_metadata(academic_year=academic_year, grade=grade, classroom=classroom, period_label="Ano letivo"),
                "summary": {
                    "students_count": 0,
                    "total_outcomes": 0,
                    "mastery_distribution": overall,
                    "taxonomy_levels": [],
                    "knowledge_dimensions": [],
                },
                "rows": [],
            }

        outcomes = StudentOutcome.objects.select_related("student", "outcome").filter(student_id__in=student_ids)
        tenant_filter = self._tenant_filter()
        if tenant_filter:
            outcomes = outcomes.filter(**tenant_filter)
        if grade:
            outcomes = outcomes.filter(outcome__grade=grade)
        if classroom and classroom.grade_id:
            outcomes = outcomes.filter(outcome__grade=classroom.grade)

        for record in outcomes:
            status = record.status
            overall[status] += 1
            level = record.outcome.taxonomy_level
            taxonomy.setdefault(level, empty_bucket())
            taxonomy[level][status] += 1

            dimension = record.outcome.knowledge_dimension or "unspecified"
            knowledge.setdefault(dimension, empty_bucket())
            knowledge[dimension][status] += 1

            classroom_obj = enrollment_by_student.get(record.student_id)
            if classroom_obj:
                bucket = classroom_buckets.setdefault(
                    classroom_obj.id,
                    {
                        "classroom_id": classroom_obj.id,
                        "classroom": classroom_obj.name,
                        "grade": classroom_obj.grade.number,
                        "mastery_distribution": empty_bucket(),
                        "total_outcomes": 0,
                    },
                )
                bucket["mastery_distribution"][status] += 1
                bucket["total_outcomes"] += 1

            if classroom:
                student_bucket = student_buckets.setdefault(
                    record.student_id,
                    {
                        "student_id": record.student_id,
                        "student_name": record.student.name,
                        "mastery_distribution": empty_bucket(),
                        "total_outcomes": 0,
                    },
                )
                student_bucket["mastery_distribution"][status] += 1
                student_bucket["total_outcomes"] += 1

        def build_level_summary(level_key, bucket):
            total = sum(bucket.values())
            attainment = bucket["proficient"] + bucket["advanced"]
            return {
                "level": level_key,
                "label": taxonomy_labels.get(level_key, level_key),
                "total": total,
                "mastery_distribution": bucket,
                "attainment_rate": float(attainment / total) if total else 0.0,
            }

        def build_dimension_summary(dim_key, bucket):
            total = sum(bucket.values())
            attainment = bucket["proficient"] + bucket["advanced"]
            return {
                "dimension": dim_key,
                "label": knowledge_labels.get(dim_key, "Sem dimensão"),
                "total": total,
                "mastery_distribution": bucket,
                "attainment_rate": float(attainment / total) if total else 0.0,
            }

        taxonomy_rows = [build_level_summary(level, bucket) for level, bucket in taxonomy.items()]
        knowledge_rows = [build_dimension_summary(level, bucket) for level, bucket in knowledge.items()]

        total_outcomes = sum(overall.values())
        attainment_total = overall["proficient"] + overall["advanced"]

        rows = list(classroom_buckets.values())
        if classroom:
            rows = list(student_buckets.values())

        return {
            "title": "Distribuição por Taxonomia de Bloom",
            "metadata": self._base_metadata(academic_year=academic_year, grade=grade, classroom=classroom, period_label="Ano letivo"),
            "summary": {
                "students_count": len(student_ids),
                "total_outcomes": total_outcomes,
                "mastery_distribution": overall,
                "attainment_rate": float(attainment_total / total_outcomes) if total_outcomes else 0.0,
                "taxonomy_levels": taxonomy_rows,
                "knowledge_dimensions": knowledge_rows,
                "methodology": "snapshot",
            },
            "rows": rows,
        }

    def _generate_learning_risk_alerts(self, *, academic_year=None, grade=None, classroom=None, **kwargs):
        enrollments = list(self._scoped_enrollments(academic_year=academic_year, grade=grade, classroom=classroom))
        student_ids = {enrollment.student_id for enrollment in enrollments}
        enrollment_by_student = {enrollment.student_id: enrollment for enrollment in enrollments}

        if not student_ids:
            return {
                "title": "Alertas de risco de aprendizagem",
                "metadata": self._base_metadata(academic_year=academic_year, grade=grade, classroom=classroom, period_label="Ano letivo"),
                "summary": {
                    "students_count": 0,
                    "risk_levels": {"high": 0, "medium": 0, "low": 0, "no_data": 0},
                    "taxonomy_gaps": [],
                },
                "rows": [],
            }

        outcomes = StudentOutcome.objects.select_related("student", "outcome").filter(student_id__in=student_ids)
        tenant_filter = self._tenant_filter()
        if tenant_filter:
            outcomes = outcomes.filter(**tenant_filter)
        if grade:
            outcomes = outcomes.filter(outcome__grade=grade)
        if classroom and classroom.grade_id:
            outcomes = outcomes.filter(outcome__grade=classroom.grade)

        taxonomy_labels = dict(LearningOutcome.TAXONOMY_LEVEL_CHOICES)
        taxonomy_gap_counts = {level: 0 for level in taxonomy_labels}

        def classify_risk(attainment_rate, total_outcomes):
            if total_outcomes == 0:
                return "no_data"
            if attainment_rate < 0.4:
                return "high"
            if attainment_rate < 0.7:
                return "medium"
            return "low"

        student_buckets = {}
        for record in outcomes:
            bucket = student_buckets.setdefault(
                record.student_id,
                {
                    "student_id": record.student_id,
                    "student_name": record.student.name,
                    "classroom": None,
                    "grade": None,
                    "total_outcomes": 0,
                    "mastery_distribution": {
                        "not_started": 0,
                        "developing": 0,
                        "proficient": 0,
                        "advanced": 0,
                    },
                    "gaps": [],
                },
            )
            bucket["total_outcomes"] += 1
            bucket["mastery_distribution"][record.status] += 1

            if record.status in {"not_started", "developing"}:
                taxonomy_gap_counts[record.outcome.taxonomy_level] = taxonomy_gap_counts.get(record.outcome.taxonomy_level, 0) + 1
                if len(bucket["gaps"]) < 5:
                    bucket["gaps"].append(
                        {
                            "outcome_code": record.outcome.code,
                            "outcome_description": record.outcome.description,
                            "taxonomy_level": record.outcome.taxonomy_level,
                            "knowledge_dimension": record.outcome.knowledge_dimension,
                            "status": record.status,
                            "mastery_level": float(record.mastery_level),
                        }
                    )

        rows = []
        risk_levels = {"high": 0, "medium": 0, "low": 0, "no_data": 0}
        for student_id in student_ids:
            enrollment = enrollment_by_student.get(student_id)
            bucket = student_buckets.get(student_id)
            if not bucket:
                bucket = {
                    "student_id": student_id,
                    "student_name": enrollment.student.name if enrollment else "",
                    "classroom": enrollment.classroom.name if enrollment else None,
                    "grade": enrollment.classroom.grade.number if enrollment else None,
                    "total_outcomes": 0,
                    "mastery_distribution": {
                        "not_started": 0,
                        "developing": 0,
                        "proficient": 0,
                        "advanced": 0,
                    },
                    "gaps": [],
                }

            bucket["classroom"] = enrollment.classroom.name if enrollment else bucket["classroom"]
            bucket["grade"] = enrollment.classroom.grade.number if enrollment else bucket["grade"]
            total = bucket["total_outcomes"]
            attainment = bucket["mastery_distribution"]["proficient"] + bucket["mastery_distribution"]["advanced"]
            attainment_rate = float(attainment / total) if total else 0.0
            bucket["attainment_rate"] = attainment_rate
            bucket["risk_level"] = classify_risk(attainment_rate, total)
            risk_levels[bucket["risk_level"]] += 1
            rows.append(bucket)

        taxonomy_gaps = [
            {
                "level": level,
                "label": taxonomy_labels.get(level, level),
                "count": count,
            }
            for level, count in taxonomy_gap_counts.items()
        ]

        return {
            "title": "Alertas de risco de aprendizagem",
            "metadata": self._base_metadata(academic_year=academic_year, grade=grade, classroom=classroom, period_label="Ano letivo"),
            "summary": {
                "students_count": len(student_ids),
                "risk_levels": risk_levels,
                "taxonomy_gaps": taxonomy_gaps,
            },
            "rows": rows,
        }

    def _generate_learning_intervention_plan(self, *, academic_year=None, grade=None, classroom=None, emit_alerts=False, **kwargs):
        enrollments = list(self._scoped_enrollments(academic_year=academic_year, grade=grade, classroom=classroom))
        student_ids = {enrollment.student_id for enrollment in enrollments}
        enrollment_by_student = {enrollment.student_id: enrollment for enrollment in enrollments}

        if not student_ids:
            return {
                "title": "Plano de intervenção pedagógica",
                "metadata": self._base_metadata(academic_year=academic_year, grade=grade, classroom=classroom, period_label="Ano letivo"),
                "summary": {
                    "students_count": 0,
                    "tiers": {"tier1": 0, "tier2": 0, "tier3": 0, "diagnostic": 0},
                    "top_taxonomy_gaps": [],
                },
                "rows": [],
            }

        outcomes = StudentOutcome.objects.select_related("student", "outcome").filter(student_id__in=student_ids)
        tenant_filter = self._tenant_filter()
        if tenant_filter:
            outcomes = outcomes.filter(**tenant_filter)
        if grade:
            outcomes = outcomes.filter(outcome__grade=grade)
        if classroom and classroom.grade_id:
            outcomes = outcomes.filter(outcome__grade=classroom.grade)

        taxonomy_labels = dict(LearningOutcome.TAXONOMY_LEVEL_CHOICES)
        knowledge_labels = dict(LearningOutcome.KNOWLEDGE_DIMENSION_CHOICES)

        taxonomy_gap_counts = {level: 0 for level in taxonomy_labels}
        knowledge_gap_counts = {level: 0 for level in knowledge_labels}
        knowledge_gap_counts["unspecified"] = 0

        def classify_risk(attainment_rate, total_outcomes):
            if total_outcomes == 0:
                return "diagnostic"
            if attainment_rate < 0.4:
                return "tier3"
            if attainment_rate < 0.7:
                return "tier2"
            return "tier1"

        tier_strategies = {
            "tier1": [
                "Reforço em sala com prática guiada e feedback imediato.",
                "Rotina semanal de verificação formativa.",
            ],
            "tier2": [
                "Pequenos grupos focados em lacunas específicas.",
                "Ciclos curtos de intervenção (2-4 semanas) com metas claras.",
            ],
            "tier3": [
                "Plano individual intensivo com monitoria contínua.",
                "Ajuste de ritmo e apoio extra em habilidades pré-requisitos.",
            ],
            "diagnostic": [
                "Aplicar diagnóstico rápido para mapear lacunas prioritárias.",
                "Atualizar o plano após coleta de evidências iniciais.",
            ],
        }
        taxonomy_strategies = {
            "remember": "Prática de recuperação: cartões, quizzes rápidos, repetição espaçada.",
            "understand": "Mapas conceituais, paráfrase guiada e exemplos concretos.",
            "apply": "Exercícios contextualizados e resolução de problemas.",
            "analyze": "Comparar, classificar e justificar relações entre conceitos.",
            "evaluate": "Debates com critérios e rubricas de julgamento.",
            "create": "Projetos curtos com produção autoral orientada.",
        }
        knowledge_strategies = {
            "factual": "Foco em vocabulário-chave e fatos essenciais.",
            "conceptual": "Conexão entre conceitos e princípios estruturantes.",
            "procedural": "Demonstrações passo a passo e prática monitorada.",
            "metacognitive": "Autoavaliação e diário de aprendizagem.",
        }

        student_buckets = {}
        for record in outcomes:
            bucket = student_buckets.setdefault(
                record.student_id,
                {
                    "student_id": record.student_id,
                    "student_name": record.student.name,
                    "classroom": None,
                    "grade": None,
                    "total_outcomes": 0,
                    "mastery_distribution": {
                        "not_started": 0,
                        "developing": 0,
                        "proficient": 0,
                        "advanced": 0,
                    },
                    "taxonomy_gaps": {},
                    "knowledge_gaps": {},
                },
            )
            bucket["total_outcomes"] += 1
            bucket["mastery_distribution"][record.status] += 1

            if record.status in {"not_started", "developing"}:
                level = record.outcome.taxonomy_level
                dimension = record.outcome.knowledge_dimension or "unspecified"
                bucket["taxonomy_gaps"][level] = bucket["taxonomy_gaps"].get(level, 0) + 1
                bucket["knowledge_gaps"][dimension] = bucket["knowledge_gaps"].get(dimension, 0) + 1
                taxonomy_gap_counts[level] = taxonomy_gap_counts.get(level, 0) + 1
                knowledge_gap_counts[dimension] = knowledge_gap_counts.get(dimension, 0) + 1

        tiers_count = {"tier1": 0, "tier2": 0, "tier3": 0, "diagnostic": 0}
        rows = []
        for student_id in student_ids:
            enrollment = enrollment_by_student.get(student_id)
            bucket = student_buckets.get(student_id, {
                "student_id": student_id,
                "student_name": enrollment.student.name if enrollment else "",
                "classroom": None,
                "grade": None,
                "total_outcomes": 0,
                "mastery_distribution": {
                    "not_started": 0,
                    "developing": 0,
                    "proficient": 0,
                    "advanced": 0,
                },
                "taxonomy_gaps": {},
                "knowledge_gaps": {},
            })
            bucket["classroom"] = enrollment.classroom.name if enrollment else bucket["classroom"]
            bucket["grade"] = enrollment.classroom.grade.number if enrollment else bucket["grade"]

            total = bucket["total_outcomes"]
            attainment = bucket["mastery_distribution"]["proficient"] + bucket["mastery_distribution"]["advanced"]
            attainment_rate = float(attainment / total) if total else 0.0
            tier = classify_risk(attainment_rate, total)
            tiers_count[tier] += 1

            top_taxonomy = sorted(bucket["taxonomy_gaps"].items(), key=lambda item: item[1], reverse=True)[:3]
            top_knowledge = sorted(bucket["knowledge_gaps"].items(), key=lambda item: item[1], reverse=True)[:2]

            recommendations = []
            recommendations.extend(tier_strategies.get(tier, []))
            for level, _ in top_taxonomy:
                strategy = taxonomy_strategies.get(level)
                if strategy:
                    recommendations.append(strategy)
            for dimension, _ in top_knowledge:
                strategy = knowledge_strategies.get(dimension)
                if strategy:
                    recommendations.append(strategy)

            bucket["attainment_rate"] = attainment_rate
            bucket["tier"] = tier
            bucket["tenant_id"] = (enrollment.student.tenant_id or "").strip() if enrollment else ""
            bucket["top_taxonomy_gaps"] = [
                {"level": level, "label": taxonomy_labels.get(level, level), "count": count} for level, count in top_taxonomy
            ]
            bucket["top_knowledge_gaps"] = [
                {"dimension": dim, "label": knowledge_labels.get(dim, "Sem dimensão"), "count": count} for dim, count in top_knowledge
            ]
            bucket["recommendations"] = recommendations[:6]
            rows.append(bucket)

        top_taxonomy_gaps = [
            {"level": level, "label": taxonomy_labels.get(level, level), "count": count}
            for level, count in sorted(taxonomy_gap_counts.items(), key=lambda item: item[1], reverse=True)
        ]

        payload = {
            "title": "Plano de intervenção pedagógica",
            "metadata": self._base_metadata(academic_year=academic_year, grade=grade, classroom=classroom, period_label="Ano letivo"),
            "summary": {
                "students_count": len(student_ids),
                "tiers": tiers_count,
                "top_taxonomy_gaps": top_taxonomy_gaps[:5],
                "top_knowledge_gaps": [
                    {"dimension": dim, "label": knowledge_labels.get(dim, "Sem dimensão"), "count": count}
                    for dim, count in sorted(knowledge_gap_counts.items(), key=lambda item: item[1], reverse=True)
                ],
            },
            "rows": rows,
        }

        if emit_alerts:
            self._emit_learning_risk_alerts(rows, academic_year=academic_year)

        return payload

    def _emit_learning_risk_alerts(self, rows, *, academic_year=None):
        from apps.school.models import AuditAlert

        window_start = timezone.now() - timezone.timedelta(hours=24)
        username = getattr(self.user, "username", "") if self.user else ""
        for row in rows:
            if row.get("tier") != "tier3":
                continue
            tenant_id = (row.get("tenant_id") or (self.profile.tenant_id if self.profile else "") or "").strip()
            if not tenant_id:
                continue
            student_id = row.get("student_id")
            student_name = row.get("student_name") or "Aluno"
            summary = f"Risco alto: {student_name} ({student_id})"
            exists = AuditAlert.objects.filter(
                alert_type="learning_risk_tier3",
                tenant_id=tenant_id,
                summary=summary,
                acknowledged=False,
                created_at__gte=window_start,
            ).exists()
            if exists:
                continue
            AuditAlert.objects.create(
                alert_type="learning_risk_tier3",
                severity="elevated",
                tenant_id=tenant_id,
                resource="student",
                username=username,
                summary=summary,
                details={
                    "student_id": student_id,
                    "classroom": row.get("classroom"),
                    "grade": row.get("grade"),
                    "attainment_rate": row.get("attainment_rate"),
                    "academic_year": getattr(academic_year, "code", None),
                    "top_taxonomy_gaps": row.get("top_taxonomy_gaps", []),
                    "top_knowledge_gaps": row.get("top_knowledge_gaps", []),
                },
            )


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


def build_report_export_context(report):
    content = report.content if isinstance(report.content, dict) else {}
    metadata = content.get("metadata") if isinstance(content.get("metadata"), dict) else {}
    student_snapshot = content.get("student_snapshot") if isinstance(content.get("student_snapshot"), dict) else {}
    summary = content.get("summary") if isinstance(content.get("summary"), dict) else {}
    rows = content.get("rows") if isinstance(content.get("rows"), list) else []
    return {
        "title": report.title,
        "serial_number": report.serial_number,
        "verification_code": report.verification_code,
        "verification_hash": report.verification_hash,
        "generated_at": timezone.localtime(report.generated_at).strftime("%d/%m/%Y %H:%M") if report.generated_at else "",
        "report_kind": content.get("report_kind", ""),
        "metadata": metadata,
        "student_snapshot": student_snapshot,
        "summary": summary,
        "rows": rows,
    }


def render_report_html(report):
    context = build_report_export_context(report)
    metadata = context["metadata"]
    student_snapshot = context["student_snapshot"]
    summary = context["summary"]
    rows = context["rows"]

    def block(title, value):
        return f"<div class='meta'><span>{html.escape(title)}</span><strong>{html.escape(str(value or 'Sem valor'))}</strong></div>"

    summary_items = []
    for key, value in summary.items():
        if isinstance(value, (dict, list)):
            continue
        summary_items.append(block(key.replace('_', ' ').title(), value))

    row_cards = []
    for index, row in enumerate(rows[:60], start=1):
        cells = "".join(block(key.replace("_", " ").title(), value) for key, value in row.items())
        row_cards.append(f"<section class='row-card'><h4>Linha {index}</h4><div class='grid'>{cells}</div></section>")

    return f"""<!DOCTYPE html>
<html lang="pt">
<head>
  <meta charset="utf-8" />
  <title>{html.escape(context['title'])}</title>
  <style>
    body {{ font-family: 'Segoe UI', sans-serif; color:#14213d; margin:0; background:#f7f3e9; }}
    .sheet {{ max-width: 920px; margin: 24px auto; background: white; padding: 32px; border:1px solid rgba(20,33,61,.12); }}
    .brand {{ text-align:center; text-transform:uppercase; letter-spacing:.25em; font-size:11px; color:rgba(20,33,61,.6); }}
    h1 {{ text-align:center; margin:10px 0 6px; }}
    .sub {{ text-align:center; color:rgba(20,33,61,.75); margin-bottom:18px; }}
    .banner {{ border:1px solid rgba(60,122,87,.2); background:rgba(60,122,87,.08); color:#24543c; padding:12px 14px; border-radius:14px; text-align:center; }}
    .grid {{ display:grid; grid-template-columns:repeat(2,minmax(0,1fr)); gap:10px; }}
    .meta {{ border:1px solid rgba(20,33,61,.12); background:#fbf8f2; border-radius:12px; padding:10px 12px; }}
    .meta span {{ display:block; font-size:11px; text-transform:uppercase; letter-spacing:.12em; color:rgba(20,33,61,.55); }}
    .meta strong {{ display:block; margin-top:6px; font-size:14px; }}
    h3 {{ margin:26px 0 10px; }}
    .row-card {{ border:1px solid rgba(20,33,61,.12); border-radius:14px; padding:14px; margin-top:10px; }}
    .footer {{ margin-top:28px; border-top:1px solid rgba(20,33,61,.12); padding-top:12px; font-size:12px; color:rgba(20,33,61,.7); word-break:break-all; }}
    @media print {{ body {{ background:white; }} .sheet {{ margin:0; border:0; }} }}
  </style>
</head>
<body>
  <main class="sheet">
    <p class="brand">Substrato Educação</p>
    <h1>{html.escape(context["title"])}</h1>
    <p class="sub">{html.escape(str(metadata.get("school") or "Sem escola"))} | {html.escape(str(metadata.get("academic_year") or report.period or "Sem período"))}</p>
    <div class="banner">Documento oficial emitido pelo sistema | Série {html.escape(context["serial_number"])} | Código {html.escape(context["verification_code"])}</div>
    <h3>Identificação</h3>
    <div class="grid">
      {block("Tipo", report.type)}
      {block("Chave", context["report_kind"])}
      {block("Gerado em", context["generated_at"])}
      {block("Período", metadata.get("period_label") or report.period)}
    </div>
    {"<h3>Estudante</h3><div class='grid'>" + "".join(block(key.replace('_', ' ').title(), value) for key, value in student_snapshot.items()) + "</div>" if student_snapshot else ""}
    {"<h3>Síntese</h3><div class='grid'>" + "".join(summary_items) + "</div>" if summary_items else ""}
    {"<h3>Linhas</h3>" + "".join(row_cards) if row_cards else ""}
    <div class="footer">
      Série documental: {html.escape(context["serial_number"])}<br />
      Código de verificação: {html.escape(context["verification_code"])}<br />
      Assinatura criptográfica: {html.escape(context["verification_hash"])}
    </div>
  </main>
</body>
</html>"""


def _escape_pdf_text(value):
    return str(value).replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")


def render_report_pdf(report):
    context = build_report_export_context(report)
    metadata = context["metadata"]
    student_snapshot = context["student_snapshot"]
    summary = context["summary"]
    rows = context["rows"]

    lines = [
        "Substrato Educacao",
        context["title"],
        f"Serie: {context['serial_number']}",
        f"Codigo: {context['verification_code']}",
        f"Gerado em: {context['generated_at']}",
        f"Periodo: {metadata.get('academic_year') or report.period or 'Sem periodo'}",
    ]
    if student_snapshot:
        lines.append("")
        lines.append("Estudante")
        for key, value in student_snapshot.items():
            lines.append(f"{key}: {value}")
    if summary:
        lines.append("")
        lines.append("Resumo")
        for key, value in summary.items():
            if isinstance(value, (dict, list)):
                continue
            lines.append(f"{key}: {value}")
    if rows:
        lines.append("")
        lines.append("Linhas")
        for index, row in enumerate(rows[:25], start=1):
            lines.append(f"Linha {index}")
            for key, value in row.items():
                if isinstance(value, (dict, list)):
                    continue
                lines.append(f"  {key}: {value}")
    lines.append("")
    lines.append(f"Assinatura: {context['verification_hash']}")

    page_width = 595
    page_height = 842
    current_y = 800
    commands = ["BT", "/F1 11 Tf", "40 800 Td"]
    first_line = True
    for line in lines:
        if current_y < 50:
            break
        safe_line = _escape_pdf_text(line)
        if first_line:
            commands.append(f"({_escape_pdf_text(line)}) Tj")
            first_line = False
        else:
            commands.append("0 -16 Td")
            commands.append(f"({safe_line}) Tj")
        current_y -= 16
    commands.append("ET")
    stream = "\n".join(commands).encode("latin-1", errors="replace")

    objects = []

    def add_object(data):
        objects.append(data)
        return len(objects)

    font_id = add_object(b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>")
    content_id = add_object(f"<< /Length {len(stream)} >>\nstream\n".encode("latin-1") + stream + b"\nendstream")
    page_id = add_object(
        f"<< /Type /Page /Parent 4 0 R /MediaBox [0 0 {page_width} {page_height}] /Resources << /Font << /F1 {font_id} 0 R >> >> /Contents {content_id} 0 R >>".encode(
            "latin-1"
        )
    )
    pages_id = add_object(f"<< /Type /Pages /Kids [{page_id} 0 R] /Count 1 >>".encode("latin-1"))
    catalog_id = add_object(f"<< /Type /Catalog /Pages {pages_id} 0 R >>".encode("latin-1"))

    output = BytesIO()
    output.write(b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n")
    offsets = [0]
    for index, obj in enumerate(objects, start=1):
        offsets.append(output.tell())
        output.write(f"{index} 0 obj\n".encode("latin-1"))
        output.write(obj)
        output.write(b"\nendobj\n")
    xref_start = output.tell()
    output.write(f"xref\n0 {len(objects) + 1}\n".encode("latin-1"))
    output.write(b"0000000000 65535 f \n")
    for offset in offsets[1:]:
        output.write(f"{offset:010d} 00000 n \n".encode("latin-1"))
    output.write(
        f"trailer\n<< /Size {len(objects) + 1} /Root {catalog_id} 0 R >>\nstartxref\n{xref_start}\n%%EOF".encode("latin-1")
    )
    return output.getvalue()
