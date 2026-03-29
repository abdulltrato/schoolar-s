from apps.school.models import Invoice, Payment


def backfill_finance_entities(runner):
    runner._backfill_queryset(
        label="Invoice",
        queryset=Invoice.objects.select_related("student", "school"),
        candidate_fn=lambda obj: [
            getattr(obj.student, "tenant_id", ""),
            getattr(obj.school, "tenant_id", ""),
        ],
        model=Invoice,
    )

    runner._backfill_queryset(
        label="Payment",
        queryset=Payment.objects.select_related("invoice"),
        candidate_fn=lambda obj: [
            getattr(obj.invoice, "tenant_id", ""),
        ],
        model=Payment,
    )
