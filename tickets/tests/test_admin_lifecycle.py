"""Guard against lifecycle and audit bypass through the Django admin."""

from django.contrib import admin
from django.contrib.auth import get_user_model
from django.test import RequestFactory
from django.urls import reverse
from rest_framework import status

from tickets.admin import TicketAdminForm
from tickets.models import NotificationOutbox, Ticket, TicketAuditEvent
from tickets.tests.base import APITestBase

User = get_user_model()


class TicketAdminLifecycleTests(APITestBase):
    def setUp(self):
        super().setUp()
        self.operator = User.objects.create_superuser(
            username="admin-operator",
            email="operator@example.test",
            password="Admin-test-pass-2026!",
        )
        self.request = RequestFactory().post("/admin/tickets/ticket/")
        self.request.user = self.operator
        self.model_admin = admin.site._registry[Ticket]

    def form_for(self, ticket, status_value, assignee=""):
        return TicketAdminForm(
            data={
                "title": ticket.title,
                "description": ticket.description,
                "category": ticket.category,
                "status": status_value,
                "priority": ticket.priority,
                "requester": ticket.requester_id,
                "assignee": assignee,
            },
            instance=ticket,
        )

    def test_admin_form_rejects_illegal_status_transition(self):
        form = self.form_for(self.ticket, Ticket.Status.RESOLVED)
        self.assertFalse(form.is_valid())
        self.assertIn("status", form.errors)

    def test_admin_form_preserves_staff_explicit_creation_status(self):
        ticket = Ticket(
            title="Criado no admin",
            description="Teste",
            requester=self.requester,
        )
        form = self.form_for(ticket, Ticket.Status.CLOSED)
        self.assertTrue(form.is_valid(), form.errors)

    def test_admin_form_rejects_inactive_or_nonstaff_assignee(self):
        form = self.form_for(self.ticket, Ticket.Status.OPEN, self.other_user.pk)
        self.assertFalse(form.is_valid())
        self.assertIn("assignee", form.errors)

        self.staff.is_active = False
        self.staff.save(update_fields=["is_active"])
        form = self.form_for(self.ticket, Ticket.Status.OPEN, self.staff.pk)
        self.assertFalse(form.is_valid())
        self.assertIn("assignee", form.errors)

    def test_admin_cannot_change_requester_after_creation(self):
        fields = self.model_admin.get_readonly_fields(self.request, self.ticket)
        self.assertIn("requester", fields)

    def test_admin_update_creates_audit_and_notification_events(self):
        edited = Ticket.objects.get(pk=self.ticket.pk)
        edited.status = Ticket.Status.IN_PROGRESS
        edited.priority = Ticket.Priority.HIGH
        edited.assignee = self.staff

        self.model_admin.save_model(self.request, edited, form=None, change=True)

        self.ticket.refresh_from_db()
        self.assertEqual(self.ticket.status, Ticket.Status.IN_PROGRESS)
        self.assertEqual(
            set(TicketAuditEvent.objects.values_list("field", flat=True)),
            {"status", "priority", "assignee"},
        )
        self.assertEqual(
            set(NotificationOutbox.objects.values_list("recipient_id", "kind")),
            {
                (self.requester.pk, NotificationOutbox.Kind.STATUS_CHANGED),
                (self.staff.pk, NotificationOutbox.Kind.ASSIGNED),
            },
        )

    def test_admin_ticket_creation_notifies_other_active_staff(self):
        new_ticket = Ticket(
            title="Abertura administrativa",
            description="Criado pelo admin",
            requester=self.requester,
        )
        self.model_admin.save_model(self.request, new_ticket, form=None, change=False)
        self.assertIsNotNone(new_ticket.pk)
        self.assertTrue(
            NotificationOutbox.objects.filter(
                recipient=self.staff, kind=NotificationOutbox.Kind.CREATED,
            ).exists()
        )
        self.assertFalse(NotificationOutbox.objects.filter(recipient=self.operator).exists())

    def test_staff_api_can_create_terminal_ticket_under_existing_contract(self):
        self.authenticate(self.staff)
        result = self.client.post(
            reverse("ticket-list"),
            {
                "title": "Pular atendimento",
                "description": "Não deve resolver diretamente.",
                "status": Ticket.Status.RESOLVED,
            },
            format="json",
        )
        self.assertEqual(result.status_code, status.HTTP_201_CREATED)
        self.assertEqual(result.data["status"], Ticket.Status.RESOLVED)
        self.assertTrue(Ticket.objects.filter(title="Pular atendimento").exists())

    def test_staff_api_can_create_open_ticket_explicitly(self):
        self.authenticate(self.staff)
        result = self.client.post(
            reverse("ticket-list"),
            {
                "title": "Abertura válida",
                "description": "Novo chamado na fila.",
                "status": Ticket.Status.OPEN,
            },
            format="json",
        )
        self.assertEqual(result.status_code, status.HTTP_201_CREATED)
        self.assertEqual(result.data["status"], Ticket.Status.OPEN)
