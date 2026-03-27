import logging
import time
import uuid

from core.request_context import clear_current_request, set_current_request

logger = logging.getLogger("schoolar.request")
SLOW_REQUEST_THRESHOLD_MS = 800


class RequestContextMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
        request.tenant_id = request.headers.get("X-Tenant-ID")
        request.started_at = time.perf_counter()
        set_current_request(request)

        status_code = 500
        try:
            response = self.get_response(request)
            status_code = response.status_code
            return response
        finally:
            clear_current_request()
            duration_ms = round((time.perf_counter() - request.started_at) * 1000, 2)
            log_payload = {
                "request_id": request.request_id,
                "tenant_id": request.tenant_id,
                "method": request.method,
                "path": request.get_full_path(),
                "status_code": status_code,
                "duration_ms": duration_ms,
            }
            if duration_ms >= SLOW_REQUEST_THRESHOLD_MS:
                logger.warning("slow_request", extra=log_payload)
            else:
                logger.info("request_finished", extra=log_payload)


class ResponseHeadersMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        response["X-Request-ID"] = getattr(request, "request_id", "-")
        tenant_id = getattr(request, "tenant_id", None)
        if tenant_id:
            response["X-Tenant-ID"] = tenant_id
        return response
