from django.http import JsonResponse

from application.monitoring import build_health_payload, build_readiness_payload


def healthcheck(request):
    return JsonResponse(build_health_payload())


def readiness(request):
    payload, ready = build_readiness_payload()
    return JsonResponse(payload, status=200 if ready else 503)
