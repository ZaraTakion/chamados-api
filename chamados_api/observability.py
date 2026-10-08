"""Request correlation and deliberately minimal, structured HTTP logging.

No request path, query string, body, authorization header, exception text, or
traceback is included. The JSON formatter also suppresses untrusted messages
from framework loggers routed through it.
"""

import json
import logging
import re
import time
from contextvars import ContextVar
from datetime import datetime, timezone
from uuid import uuid4

_request_id = ContextVar("chamados_request_id", default=None)
request_logger = logging.getLogger("chamados_api.http")
_REQUEST_ID_PATTERN = re.compile(r"[0-9a-f]{32}\Z")
_EVENTS = {"http.request", "http.server_error", "http.unhandled_exception"}
_METHODS = {"GET", "POST", "PUT", "PATCH", "DELETE", "HEAD", "OPTIONS"}


def get_request_id():
    """Current request ID, or None outside an HTTP request."""
    return _request_id.get()


class SafeJSONFormatter(logging.Formatter):
    """Serialize only explicitly allowed, non-sensitive logging fields."""

    def format(self, record):
        event = getattr(record, "event", None)
        if event not in _EVENTS:
            event = "framework.error"

        result = {
            "timestamp": datetime.fromtimestamp(record.created, tz=timezone.utc).isoformat(timespec="milliseconds"),
            "level": record.levelname,
            "logger": record.name,
            "event": event,
        }

        request_id = getattr(record, "request_id", None) or get_request_id()
        if isinstance(request_id, str) and _REQUEST_ID_PATTERN.fullmatch(request_id):
            result["request_id"] = request_id

        if event in _EVENTS:
            method = getattr(record, "method", None)
            result["method"] = method if method in _METHODS else "OTHER"
            route = getattr(record, "route", None)
            result["route"] = route if isinstance(route, str) else "unmatched"
            status_code = getattr(record, "status_code", None)
            if type(status_code) is int and 100 <= status_code <= 599:
                result["status_code"] = status_code
            duration_ms = getattr(record, "duration_ms", None)
            if isinstance(duration_ms, (float, int)) and not isinstance(duration_ms, bool):
                result["duration_ms"] = round(max(duration_ms, 0), 2)

        # Never call record.getMessage() or format exc_info/stack_info: third-party
        # error messages can contain URLs, headers, credentials or user input.
        return json.dumps(result, ensure_ascii=False, separators=(",", ":"))


class RequestLoggingMiddleware:
    """Generate a server-owned ID and log safe request completion metadata."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request_id = uuid4().hex  # Intentionally ignore untrusted X-Request-ID input.
        context_token = _request_id.set(request_id)
        request.request_id = request_id
        start = time.perf_counter()
        try:
            response = self.get_response(request)
            response["X-Request-ID"] = request_id
            self._record(request, request_id, response.status_code, start)
            return response
        except Exception:
            # No exception message or traceback is sent to the HTTP logger.
            self._record(request, request_id, 500, start, unhandled=True)
            raise
        finally:
            _request_id.reset(context_token)

    @staticmethod
    def _record(request, request_id, status_code, start, unhandled=False):
        if unhandled:
            event = "http.unhandled_exception"
        elif status_code >= 500:
            event = "http.server_error"
        else:
            event = "http.request"

        route = getattr(getattr(request, "resolver_match", None), "route", None) or "unmatched"
        level = logging.ERROR if status_code >= 500 else logging.INFO
        request_logger.log(
            level,
            event,
            extra={
                "event": event,
                "request_id": request_id,
                "method": request.method,
                "route": route,
                "status_code": status_code,
                "duration_ms": (time.perf_counter() - start) * 1000,
            },
        )
