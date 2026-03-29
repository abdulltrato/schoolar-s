from django.db import transaction

from .tenant_utils import add_sample, normalize, pick_tenant, record, summarize, table_exists


class BackfillRunner:
    def __init__(self, stdout, *, dry_run, strict, chunk_size, fallback_tenant, max_samples):
        self.stdout = stdout
        self.dry_run = dry_run
        self.strict = strict
        self.chunk_size = chunk_size
        self.fallback_tenant = normalize(fallback_tenant)
        self.max_samples = max_samples
        self.stats = []
        self.samples = []

    def _record(self, **kwargs):
        record(self.stats, **kwargs)

    def _add_sample(self, label, pk, detail):
        add_sample(self.samples, label, pk, detail, max_samples=self.max_samples)

    def _table_exists(self, model) -> bool:
        return table_exists(model)

    def _backfill_queryset(self, *, label, queryset, candidate_fn, model):
        scanned = updated = missing = conflicts = 0
        update_batch = []

        for obj in queryset.iterator(chunk_size=self.chunk_size):
            scanned += 1
            candidates = candidate_fn(obj)
            tenant, issue = pick_tenant(candidates)
            if tenant:
                if obj.tenant_id != tenant:
                    obj.tenant_id = tenant
                    update_batch.append(obj)
            elif self.fallback_tenant:
                obj.tenant_id = self.fallback_tenant
                update_batch.append(obj)
                missing += 1
            elif issue == "missing":
                missing += 1
                self._add_sample(label, obj.pk, "missing tenant candidates")
            elif issue == "conflict":
                conflicts += 1
                self._add_sample(label, obj.pk, f"conflicting tenants: {candidates}")

            if len(update_batch) >= self.chunk_size:
                model.objects.bulk_update(update_batch, ["tenant_id"])
                updated += len(update_batch)
                update_batch.clear()

        if update_batch:
            model.objects.bulk_update(update_batch, ["tenant_id"])
            updated += len(update_batch)

        self._record(label=label, scanned=scanned, updated=updated, missing=missing, conflicts=conflicts)

    def run(self, fn):
        with transaction.atomic():
            fn()
            if self.dry_run:
                transaction.set_rollback(True)
        summarize(self.stdout, self.stats, self.samples, self.dry_run)
        if self.strict and any(entry["missing"] or entry["conflicts"] for entry in self.stats):
            raise SystemExit(1)
