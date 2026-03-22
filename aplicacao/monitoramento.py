from django.utils import timezone

from servicos.infraestrutura import verificar_banco, verificar_cache


def montar_health_payload():
    return {
        "status": "ok",
        "service": "schoolar-s",
        "timestamp": timezone.now().isoformat(),
    }


def montar_readiness_payload():
    checks = {"database": "error", "cache": "error"}

    try:
        checks["database"] = verificar_banco()
    except Exception:
        checks["database"] = "error"

    try:
        checks["cache"] = verificar_cache()
    except Exception:
        checks["cache"] = "error"

    ready = all(status == "ok" for status in checks.values())
    return {
        "status": "ok" if ready else "degraded",
        "service": "schoolar-s",
        "checks": checks,
        "timestamp": timezone.now().isoformat(),
    }, ready
