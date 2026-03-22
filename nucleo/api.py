import logging

from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import status
from rest_framework.exceptions import ValidationError as DRFValidationError
from rest_framework.response import Response
from rest_framework.views import exception_handler

logger = logging.getLogger("schoolar.api")


def custom_exception_handler(exc, context):
    if isinstance(exc, DjangoValidationError):
        exc = DRFValidationError(getattr(exc, "message_dict", exc.messages))

    response = exception_handler(exc, context)
    request = context.get("request")
    request_id = getattr(request, "request_id", None)
    path = getattr(request, "path", None)

    if response is None:
        logger.exception("unhandled_api_exception", extra={"request_id": request_id, "path": path})
        return Response(
            {
                "ok": False,
                "error": {
                    "code": "internal_error",
                    "message": "Erro interno do servidor.",
                    "details": None,
                },
                "meta": {
                    "request_id": request_id,
                    "path": path,
                },
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    detail = response.data
    if isinstance(detail, dict) and "detail" in detail and len(detail) == 1:
        message = str(detail["detail"])
    else:
        message = "A requisição não pôde ser processada."

    response.data = {
        "ok": False,
        "error": {
            "code": f"http_{response.status_code}",
            "message": message,
            "details": detail,
        },
        "meta": {
            "request_id": request_id,
            "path": path,
        },
    }
    return response
