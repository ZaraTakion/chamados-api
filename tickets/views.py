from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions, viewsets
from rest_framework.exceptions import PermissionDenied

from tickets.audit import record_ticket_changes, ticket_audit_snapshot
from tickets.models import Ticket, TicketAuditEvent, TicketComment
from tickets.permissions import IsRequesterOrStaff
from tickets.serializers import TicketAuditEventSerializer, TicketCommentSerializer, TicketSerializer


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
        if getattr(self, "action", None) in {"update", "partial_update"}:
            # Only lock the ticket row; the nullable assignee JOIN cannot be locked on PostgreSQL.
            tickets = tickets.select_for_update(of=("self",))
        if self.request.user.is_staff:
            return tickets
        return tickets.filter(requester=self.request.user)

    @transaction.atomic
    def update(self, request, *args, **kwargs):
        # Validation, ticket update and audit inserts share a single transaction.
        return super().update(request, *args, **kwargs)

    def perform_update(self, serializer):
        previous = ticket_audit_snapshot(serializer.instance)
        ticket = serializer.save()
        record_ticket_changes(ticket, self.request.user, previous)

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


class TicketAuditHistoryView(generics.ListAPIView):
    """History is read-only; requesters never see assignee changes."""

    serializer_class = TicketAuditEventSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = []

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return TicketAuditEvent.objects.none()
        ticket_queryset = Ticket.objects.all()
        if not self.request.user.is_staff:
            ticket_queryset = ticket_queryset.filter(requester=self.request.user)
        ticket = get_object_or_404(ticket_queryset, pk=self.kwargs["ticket_pk"])
        events = TicketAuditEvent.objects.filter(ticket=ticket)
        if not self.request.user.is_staff:
            events = events.filter(field__in=[
                TicketAuditEvent.Field.STATUS,
                TicketAuditEvent.Field.PRIORITY,
            ])
        return events
