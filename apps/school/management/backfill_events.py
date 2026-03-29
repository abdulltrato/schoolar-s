from apps.events.models import Event
from apps.school.models import School
from apps.academic.models import Student
from apps.reports.models import Report
from apps.assessment.models import Assessment


def backfill_events(runner):
    if not runner._table_exists(Event):
        runner._record(label="Event", scanned=0, updated=0, missing=0, conflicts=0)
        runner._add_sample("Event", "-", f"table {Event._meta.db_table} missing")
        return

    queryset = Event.objects.all()
    blank_events = list(queryset.filter(tenant_id="").values_list("id", "payload"))

    school_ids = set()
    student_ids = set()
    report_ids = set()
    assessment_ids = set()

    for _, payload in blank_events:
        if not isinstance(payload, dict):
            continue
        school_ids.update({payload.get("school_id"), payload.get("escola_id")})
        student_ids.update({payload.get("student_id"), payload.get("aluno_id")})
        report_ids.update({payload.get("report_id"), payload.get("relatorio_id")})
        assessment_ids.update({payload.get("assessment_id"), payload.get("avaliacao_id")})

    school_ids.discard(None)
    student_ids.discard(None)
    report_ids.discard(None)
    assessment_ids.discard(None)

    schools = School.objects.in_bulk(list(school_ids)) if runner._table_exists(School) else {}
    students = Student.objects.in_bulk(list(student_ids)) if runner._table_exists(Student) else {}
    reports = Report.objects.in_bulk(list(report_ids)) if runner._table_exists(Report) else {}
    assessments = Assessment.objects.in_bulk(list(assessment_ids)) if runner._table_exists(Assessment) else {}

    tenant_by_school = {pk: (obj.tenant_id or "").strip() for pk, obj in schools.items()}
    tenant_by_student = {pk: (obj.tenant_id or "").strip() for pk, obj in students.items()}
    tenant_by_report = {pk: (obj.tenant_id or "").strip() for pk, obj in reports.items()}
    tenant_by_assessment = {pk: (obj.tenant_id or "").strip() for pk, obj in assessments.items()}

    payloads_by_id = {event_id: payload for event_id, payload in blank_events}

    def candidates(obj):
        payload = payloads_by_id.get(obj.pk, {})
        if not isinstance(payload, dict):
            return []
        direct = payload.get("tenant_id") or payload.get("tenant")
        if direct:
            return [direct]
        school_id = payload.get("school_id") or payload.get("escola_id")
        student_id = payload.get("student_id") or payload.get("aluno_id")
        report_id = payload.get("report_id") or payload.get("relatorio_id")
        assessment_id = payload.get("assessment_id") or payload.get("avaliacao_id")
        return [
            tenant_by_school.get(school_id, ""),
            tenant_by_student.get(student_id, ""),
            tenant_by_report.get(report_id, ""),
            tenant_by_assessment.get(assessment_id, ""),
        ]

    runner._backfill_queryset(
        label="Event",
        queryset=queryset,
        candidate_fn=candidates,
        model=Event,
    )
