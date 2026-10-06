from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsRequesterOrStaff(BasePermission):
    """Requesters can access their tickets; staff can support every ticket."""

    def has_object_permission(self, request, view, obj):
        if request.user.is_staff:
            return True
        if request.method in SAFE_METHODS:
            return obj.requester_id == request.user.id
        if request.method == "DELETE":
            return False
        return obj.requester_id == request.user.id
