from collections import defaultdict

from django.db import connection


def normalize(value: str) -> str:
    return (value or "").strip()


def pick_tenant(candidates):
    normalized = {normalize(item) for item in candidates if normalize(item)}
    if not normalized:
        return None, "missing"
    if len(normalized) > 1:
        return None, "conflict"
    return next(iter(normalized)), None


def table_exists(model) -> bool:
    return model._meta.db_table in connection.introspection.table_names()


def record(stats, *, label, scanned, updated, missing, conflicts):
    stats.append(
        {
            "label": label,
            "scanned": scanned,
            "updated": updated,
            "missing": missing,
            "conflicts": conflicts,
        }
    )


def add_sample(samples, label, pk, detail, *, max_samples):
    if len(samples) < max_samples:
        samples.append(f"{label}#{pk}: {detail}")


def summarize(stdout, stats, samples, dry_run: bool):
    stdout.write("Backfill summary:")
    for entry in stats:
        stdout.write(
            f"  {entry['label']}: scanned={entry['scanned']} updated={entry['updated']} "
            f"missing={entry['missing']} conflicts={entry['conflicts']}"
        )
    if samples:
        stdout.write("Samples:")
        for sample in samples:
            stdout.write(f"  {sample}")
    if dry_run:
        stdout.write("Dry-run mode enabled: no changes were written.")
