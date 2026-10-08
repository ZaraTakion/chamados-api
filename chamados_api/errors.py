"""Stable, additive error contract for API exceptions handled by DRF.

The original validation fields and HTTP codes are preserved. Only the
`error` member is added to a handled response.
"""

from django.core.exceptions import PermissionDenied as DjangoPermissionDenied
from django.http import Http404
from rest_framework.exceptions import (
    AuthenticationFailed,
    MethodNotAllowed,
    NotAuthenticated,
    NotFound,
    ParseError,
    PermissionDenied,
    Throttled,
    ValidationError,
)
from rest_framework.views import exception_handler


def _has_code(codes, expected):
    """Search nested DRF ValidationError codes without depending on shape."""
    if isinstance(codes, dict):
        return any(_has_code(value, expected) for value in codes.values())
    if isinstance(codes, (list, tuple)):
        return any(_has_code(value, expected) for value in codes)
    return codes == expected


def _error_type(exc):
    """Return a public code and message; never expose traceback details."""
    if isinstance(exc, ValidationError):
        codes = exc.get_codes()
        if _has_code(codes, "invalid_transition"):
            return "invalid_transition", "Transição de status não permitida."
        if _has_code(codes, "forbidden_field"):
            return "forbidden_field", "Campo restrito para este usuário."
        return "validation_error", "Dados inválidos."
    if isinstance(exc, (NotAuthenticated, AuthenticationFailed)):
        return "authentication_error", "Autenticação necessária ou inválida."
    if isinstance(exc, (PermissionDenied, DjangoPermissionDenied)):
        return "permission_denied", "Acesso negado."
    if isinstance(exc, (NotFound, Http404)):
        return "not_found", "Recurso não encontrado."
    if isinstance(exc, Throttled):
        return "rate_limited", "Limite de requisições excedido."
    if isinstance(exc, MethodNotAllowed):
        return "method_not_allowed", "Método HTTP não permitido."
    if isinstance(exc, ParseError):
        return "parse_error", "Corpo da requisição inválido."
    return "api_error", "Não foi possível processar a requisição."


def api_exception_handler(exc, context):
    """Add an error envelope without changing legacy field-level details."""
    response = exception_handler(exc, context)
    if response is None:
        return None

    code, message = _error_type(exc)
    original = response.data
    envelope = {"code": code, "message": message, "details": original}

    if isinstance(original, dict):
        response.data = {**original, "error": envelope}
    else:
        response.data = {"errors": original, "error": envelope}

    return response
