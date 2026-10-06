from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import filters, generics, permissions, serializers, status, viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema

from tickets.models import Ticket, TicketComment
from tickets.permissions import IsRequesterOrStaff
from tickets.serializers import TicketCommentSerializer, TicketSerializer


class HealthSerializer(serializers.Serializer):
    status = serializers.CharField()
    timestamp = serializers.DateTimeField()


@api_view(["GET"])
@permission_classes([permissions.AllowAny])
@extend_schema(responses=HealthSerializer)
def health(request):
    return Response({"status": "ok", "timestamp": timezone.now().isoformat()})


class TicketViewSet(viewsets.ModelViewSet):
    serializer_class = TicketSerializer
    permission_classes = [permissions.IsAuthenticated, IsRequesterOrStaff]
    filterset_fields = ["status", "priority", "category", "assignee"]
    search_fields = ["title", "description", "category"]
    ordering_fields = ["created_at", "updated_at", "priority", "status"]
    ordering = ["-created_at", "-id"]

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return Ticket.objects.none()
        tickets = Ticket.objects.select_related("requester", "assignee")
        if self.request.user.is_staff:
            return tickets
        return tickets.filter(requester=self.request.user)

    def perform_create(self, serializer):
        serializer.save(requester=self.request.user)

    def perform_destroy(self, instance):
        if not self.request.user.is_staff:
            raise PermissionDenied("Somente a equipe pode excluir chamados.")
        instance.delete()


class TicketCommentListCreateView(generics.ListCreateAPIView):
    serializer_class = TicketCommentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_ticket(self):
        queryset = Ticket.objects.all()
        if not self.request.user.is_staff:
            queryset = queryset.filter(requester=self.request.user)
        return get_object_or_404(queryset, pk=self.kwargs["ticket_pk"])

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return TicketComment.objects.none()
        ticket = self.get_ticket()
        comments = TicketComment.objects.filter(ticket=ticket).select_related("author")
        if not self.request.user.is_staff:
            comments = comments.filter(is_internal=False)
        return comments

    def perform_create(self, serializer):
        ticket = self.get_ticket()
        serializer.save(ticket=ticket, author=self.request.user)
