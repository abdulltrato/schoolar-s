from django.http import JsonResponse
from aplicacao.monitoramento import montar_health_payload, montar_readiness_payload


def healthcheck(request):
    return JsonResponse(montar_health_payload())


def readiness(request):
    payload, ready = montar_readiness_payload()
    return JsonResponse(payload, status=200 if ready else 503)
