import uuid

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import exception_handler


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is None:
        return Response(
            {
                "error": {
                    "code": "INTERNAL_ERROR",
                    "message": "Error interno del servidor",
                    "details": {},
                    "trace_id": str(uuid.uuid4()),
                }
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    trace_id = str(uuid.uuid4())

    if isinstance(response.data, dict):
        details = response.data
        message = "Error de validacion"
        code = "VALIDATION_ERROR"
    elif isinstance(response.data, list):
        details = {"non_field_errors": response.data}
        message = "Error de validacion"
        code = "VALIDATION_ERROR"
    else:
        details = {"detail": str(response.data)}
        message = str(response.data)
        code = "ERROR"

    code_map = {
        400: "VALIDATION_ERROR",
        401: "UNAUTHORIZED",
        403: "FORBIDDEN",
        404: "NOT_FOUND",
        409: "CONFLICT",
        422: "UNPROCESSABLE_ENTITY",
    }

    response.data = {
        "error": {
            "code": code_map.get(response.status_code, code),
            "message": message,
            "details": details,
            "trace_id": trace_id,
        }
    }

    return response
