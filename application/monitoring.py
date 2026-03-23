from django.utils import timezone

from services.infrastructure import check_cache, check_database


def build_health_payload():
    return {
        "status": "ok",
        "service": "schoolar-s",
        "timestamp": timezone.now().isoformat(),
    }


def build_readiness_payload():
    checks = {"database": "error", "cache": "error"}

    try:
        checks["database"] = check_database()
    except Exception:
        checks["database"] = "error"

    try:
        checks["cache"] = check_cache()
    except Exception:
        checks["cache"] = "error"

    ready = all(status == "ok" for status in checks.values())
    return {
        "status": "ok" if ready else "degraded",
        "service": "schoolar-s",
        "checks": checks,
        "timestamp": timezone.now().isoformat(),
    }, ready
