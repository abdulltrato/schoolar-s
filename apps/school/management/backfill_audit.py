from apps.school.models import AuditAlert, AuditEvent


def backfill_audit(runner):
    if not runner._table_exists(AuditEvent):
        runner._record(label="AuditEvent", scanned=0, updated=0, missing=0, conflicts=0)
    else:
        runner._backfill_queryset(
            label="AuditEvent",
            queryset=AuditEvent.objects.select_related("author"),
            candidate_fn=lambda obj: [getattr(obj.author, "tenant_id", ""), obj.tenant_id],
            model=AuditEvent,
        )

    if not runner._table_exists(AuditAlert):
        runner._record(label="AuditAlert", scanned=0, updated=0, missing=0, conflicts=0)
        runner._add_sample("AuditAlert", "-", f"table {AuditAlert._meta.db_table} missing")
        return

    event_rows = []
    if runner._table_exists(AuditEvent):
        event_rows = (
            AuditEvent.objects.exclude(tenant_id="")
            .order_by("-created_at")
            .values_list("resource", "username", "tenant_id")
        )
    by_resource_user = {}
    by_resource = {}
    for resource, username, tenant in event_rows:
        tenant = (tenant or "").strip()
        if not tenant:
            continue
        if resource and username and (resource, username) not in by_resource_user:
            by_resource_user[(resource, username)] = tenant
        if resource and resource not in by_resource:
            by_resource[resource] = tenant

    queryset = AuditAlert.objects.all()

    def candidates(obj):
        return [
            by_resource_user.get((obj.resource, obj.username), ""),
            by_resource.get(obj.resource, ""),
        ]

    runner._backfill_queryset(
        label="AuditAlert",
        queryset=queryset,
        candidate_fn=candidates,
        model=AuditAlert,
    )
