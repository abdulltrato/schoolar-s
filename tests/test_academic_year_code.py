from datetime import date

import pytest
from rest_framework.test import APIRequestFactory

from apps.reports.serializers import ReportGenerationSerializer
from apps.school.models import AcademicYear, Grade


@pytest.mark.django_db
def test_academic_year_code_resolves_with_tenant_header():
    year_a = AcademicYear.objects.create(
        code="2026-2027",
        tenant_id="tenant-a",
        start_date=date(2026, 1, 1),
        end_date=date(2027, 1, 1),
        active=True,
    )
    AcademicYear.objects.create(
        code="2026-2027",
        tenant_id="tenant-b",
        start_date=date(2026, 2, 1),
        end_date=date(2027, 2, 1),
        active=True,
    )
    grade = Grade.objects.create(number=1, cycle=1, name="")

    factory = APIRequestFactory()
    request = factory.post("/api/v1/reports/generate", HTTP_X_TENANT_ID="tenant-a")

    serializer = ReportGenerationSerializer(
        data={
            "report_kind": "annual_grade_sheet",
            "academic_year": "2026-2027",
            "grade": grade.id,
        },
        context={"request": request},
    )

    assert serializer.is_valid(), serializer.errors
    assert serializer.validated_data["academic_year"].id == year_a.id


@pytest.mark.django_db
def test_academic_year_code_requires_tenant_when_ambiguous():
    AcademicYear.objects.create(
        code="2026-2027",
        tenant_id="tenant-a",
        start_date=date(2026, 1, 1),
        end_date=date(2027, 1, 1),
        active=True,
    )
    AcademicYear.objects.create(
        code="2026-2027",
        tenant_id="tenant-b",
        start_date=date(2026, 2, 1),
        end_date=date(2027, 2, 1),
        active=True,
    )
    grade = Grade.objects.create(number=2, cycle=1, name="")

    factory = APIRequestFactory()
    request = factory.post("/api/v1/reports/generate")

    serializer = ReportGenerationSerializer(
        data={
            "report_kind": "annual_grade_sheet",
            "academic_year": "2026-2027",
            "grade": grade.id,
        },
        context={"request": request},
    )

    assert not serializer.is_valid()
    assert "academic_year" in serializer.errors
