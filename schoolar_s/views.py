import json
# Parsing de payloads JSON.
import logging
# Logger do projeto.

from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
# Funções de autenticação do Django e atualização de sessão.
from django.contrib.auth import password_validation
# Validação de nova palavra-passe.
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
                "avatar_url": getattr(profile, "avatar_url", ""),
            },
        }
    )


@require_POST
@csrf_exempt
def change_password_login_view(request):
    """Permite alterar a palavra-passe a partir da tela de login, autenticando com a senha atual."""
    payload = _read_json_body(request)
    username = str(payload.get("username", "")).strip()
    old_password = str(payload.get("old_password", ""))
    new_password = str(payload.get("new_password", ""))

    user = authenticate(request, username=username, password=old_password)
    if user is None:
        logger.warning("auth_password_change_login_failed", extra=_build_auth_log_payload(request, username=username, event="login_failed"))
        return JsonResponse(
            {"ok": False, "error": {"code": "invalid_credentials", "message": "Credenciais inválidas."}},
            status=401,
        )

    try:
        password_validation.validate_password(new_password, user=user)
    except Exception as exc:
        logger.warning("auth_password_validation_error", extra=_build_auth_log_payload(request, user=user, event="password_validation_error"))
        return JsonResponse(
            {
                "ok": False,
                "error": {
                    "code": "invalid_new_password",
                    "message": "; ".join(getattr(exc, "messages", [str(exc)])),
                },
            },
            status=400,
        )

    user.set_password(new_password)
    user.save()
    login(request, user)
    get_token(request)
    profile = getattr(user, "school_profile", None)
    logger.info("auth_password_changed_login", extra=_build_auth_log_payload(request, user=user, event="password_changed"))

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
                "avatar_url": getattr(profile, "avatar_url", ""),
            },
        }
    )


@require_POST
@csrf_exempt
def change_password_view(request):
    """Atualiza a palavra-passe do utilizador autenticado (CSRF-exempt para simplicidade no frontend)."""
    user = request.user
    if not user.is_authenticated:
        logger.info("auth_password_change_denied", extra=_build_auth_log_payload(request, event="not_authenticated"))
        return JsonResponse({"ok": False, "error": {"code": "not_authenticated", "message": "Sessão necessária."}}, status=401)

    payload = _read_json_body(request)
    old_password = str(payload.get("old_password", ""))
    new_password = str(payload.get("new_password", ""))

    if not user.check_password(old_password):
        logger.warning("auth_password_change_failed", extra=_build_auth_log_payload(request, user=user, event="invalid_old_password"))
        return JsonResponse(
            {"ok": False, "error": {"code": "invalid_old_password", "message": "A palavra-passe atual está incorreta."}},
            status=400,
        )

    try:
        password_validation.validate_password(new_password, user=user)
    except Exception as exc:
        logger.warning("auth_password_validation_error", extra=_build_auth_log_payload(request, user=user, event="password_validation_error"))
        return JsonResponse(
            {
                "ok": False,
                "error": {
                    "code": "invalid_new_password",
                    "message": "; ".join(getattr(exc, "messages", [str(exc)])),
                },
            },
            status=400,
        )

    user.set_password(new_password)
    user.save()
    update_session_auth_hash(request, user)
    logger.info("auth_password_changed", extra=_build_auth_log_payload(request, user=user, event="password_changed"))
    return JsonResponse({"ok": True})


@require_POST
@csrf_exempt
def update_profile_view(request):
    """Atualiza dados básicos e avatar do utilizador autenticado (CSRF-exempt para simplicidade no frontend)."""
    user = request.user
    if not user.is_authenticated:
        logger.info("auth_profile_update_denied", extra=_build_auth_log_payload(request, event="not_authenticated"))
        return JsonResponse({"ok": False, "error": {"code": "not_authenticated", "message": "Sessão necessária."}}, status=401)

    payload = _read_json_body(request)
    first_name = str(payload.get("first_name", user.first_name)).strip()
    last_name = str(payload.get("last_name", user.last_name)).strip()
    avatar_url = str(payload.get("avatar_url", "")).strip()

    user.first_name = first_name
    user.last_name = last_name
    user.save(update_fields=["first_name", "last_name"])

    profile = getattr(user, "school_profile", None)
    if profile is not None:
        profile.avatar_url = avatar_url
        profile.save(update_fields=["avatar_url", "updated_at"] if hasattr(profile, "updated_at") else ["avatar_url"])

    logger.info("auth_profile_updated", extra=_build_auth_log_payload(request, user=user, event="profile_updated"))
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
                "avatar_url": getattr(profile, "avatar_url", ""),
            },
        }
    )
