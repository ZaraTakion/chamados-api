"""Low-cost health probes for orchestrators and external monitors."""

from django.db import DatabaseError, connections
from django.utils import timezone
from drf_spectacular.utils import extend_schema
from rest_framework import permissions, serializers, status
from rest_framework.decorators import api_view, permission_classes, throttle_classes
from rest_framework.response import Response


class HealthSerializer(serializers.Serializer):
    status = serializers.CharField()
    timestamp = serializers.DateTimeField()


def _health_response(ready=True):
    response = Response(
        {"status": "ok" if ready else "unavailable", "timestamp": timezone.now().isoformat()},
        status=status.HTTP_200_OK if ready else status.HTTP_503_SERVICE_UNAVAILABLE,
    )
    response["Cache-Control"] = "no-store"
    return response


@extend_schema(responses=HealthSerializer)
@api_view(["GET"])
@permission_classes([permissions.AllowAny])
@throttle_classes([])
def health(request):
    """Legacy liveness alias: keep the existing response contract."""
    return _health_response()


@extend_schema(responses=HealthSerializer)
@api_view(["GET"])
@permission_classes([permissions.AllowAny])
@throttle_classes([])
def liveness(request):
    """Process is serving HTTP; intentionally avoid touching the database."""
    return _health_response()


@extend_schema(responses={200: HealthSerializer, 503: HealthSerializer})
@api_view(["GET"])
@permission_classes([permissions.AllowAny])
@throttle_classes([])
def readiness(request):
    """Depend on the primary database only; never expose connection errors."""
    try:
        with connections["default"].cursor() as cursor:
            cursor.execute("SELECT 1")
            is_ready = cursor.fetchone() == (1,)
    except DatabaseError:
        is_ready = False
    return _health_response(ready=is_ready)
