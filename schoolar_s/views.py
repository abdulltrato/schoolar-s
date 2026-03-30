import json
# Parsing de payloads JSON.
import logging
# Logger do projeto.

from django.contrib.auth import authenticate, login, logout
# Funções de autenticação do Django.
from django.middleware.csrf import get_token
# Gera/renova token CSRF.
from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie
# Decoradores para controlar CSRF.
from django.http import JsonResponse
# Respostas JSON simples.
from django.views.decorators.http import require_GET, require_POST
# Restringe métodos.

from application.monitoring import build_health_payload, build_readiness_payload
# Helpers de health/readiness.

logger = logging.getLogger("schoolar.api")


def _read_json_body(request):
    """Lê body JSON retornando dict vazio em caso de erro de parsing."""
    try:
        body = request.body.decode("utf-8") if request.body else "{}"
        return json.loads(body)
    except (UnicodeDecodeError, json.JSONDecodeError):
        return {}


def _build_auth_log_payload(request, *, user=None, username=None, event=None):
    """Monta payload padrão de logging para eventos de auth."""
    profile = getattr(user, "school_profile", None) if user is not None else None
    return {
        "event": event,
        "request_id": getattr(request, "request_id", None),
        "tenant_id": getattr(profile, "tenant_id", "") if profile else getattr(request, "tenant_id", None),
        "role": getattr(profile, "role", None) if profile else None,
        "user_id": getattr(user, "id", None) if user is not None else None,
        "username": getattr(user, "username", None) if user is not None else username,
        "path": request.get_full_path(),
        "method": request.method,
        "remote_addr": request.META.get("REMOTE_ADDR"),
    }


def healthcheck(request):
    """Endpoint simples de healthcheck."""
    return JsonResponse(build_health_payload())


def readiness(request):
    """Endpoint de readiness, retorna 503 quando não pronto."""
    payload, ready = build_readiness_payload()
    return JsonResponse(payload, status=200 if ready else 503)


@require_POST
@csrf_exempt
def login_view(request):
    """Autentica usuário via POST JSON, retorna dados básicos do perfil."""
    payload = _read_json_body(request)
    username = str(payload.get("username", "")).strip()
    password = str(payload.get("password", ""))

    user = authenticate(request, username=username, password=password)
    if user is None:
        logger.warning("auth_login_failed", extra=_build_auth_log_payload(request, username=username, event="login_failed"))
        return JsonResponse(
            {
                "ok": False,
                "error": {
                    "code": "invalid_credentials",
                    "message": "Invalid username or password.",
                },
            },
            status=401,
        )

    login(request, user)
    get_token(request)
    profile = getattr(user, "school_profile", None)
    logger.info("auth_login_succeeded", extra=_build_auth_log_payload(request, user=user, event="login_succeeded"))

    return JsonResponse(
        {
            "ok": True,
            "user": {
                "id": user.id,
                "username": user.username,
                "role": getattr(profile, "role", None),
                "tenant_id": getattr(profile, "tenant_id", ""),
                "school_id": getattr(profile, "school_id", None),
            },
        }
    )


@require_POST
def logout_view(request):
    """Finaliza sessão atual."""
    user = request.user if getattr(request, "user", None) and request.user.is_authenticated else None
    logger.info("auth_logout", extra=_build_auth_log_payload(request, user=user, event="logout"))
    logout(request)
    return JsonResponse({"ok": True})


@require_GET
@ensure_csrf_cookie
def me_view(request):
    """Retorna dados do usuário autenticado e renova token CSRF."""
    user = request.user
    if not user.is_authenticated:
        get_token(request)
        logger.info("auth_session_missing", extra=_build_auth_log_payload(request, event="session_missing"))
        return JsonResponse(
            {
                "ok": False,
                "error": {
                    "code": "not_authenticated",
                    "message": "Authentication required.",
                },
            },
            status=401,
        )

    get_token(request)
    profile = getattr(user, "school_profile", None)
    logger.info("auth_session_resolved", extra=_build_auth_log_payload(request, user=user, event="session_resolved"))
    return JsonResponse(
        {
            "ok": True,
            "user": {
                "id": user.id,
                "username": user.username,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "role": getattr(profile, "role", None),
                "tenant_id": getattr(profile, "tenant_id", ""),
                "school_id": getattr(profile, "school_id", None),
                "active": getattr(profile, "active", True) if profile else True,
            },
        }
    )
