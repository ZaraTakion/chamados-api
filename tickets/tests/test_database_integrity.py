"""Database integrity tests shared by SQLite and PostgreSQL.

PostgreSQL-only coverage checks a nullable LEFT JOIN with a ticket row lock.
"""

from django.db import IntegrityError, connection, transaction
from django.urls import reverse
from rest_framework import status

from tickets.models import Ticket, TicketAuditEvent
from tickets.tests.base import APITestBase


class DatabaseIntegrityTests(APITestBase):
    def assert_rejected_by_database(self, operation):
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                operation()

    def test_invalid_status_is_rejected_by_check_constraint(self):
        self.assert_rejected_by_database(
            lambda: Ticket.objects.filter(pk=self.ticket.pk).update(status="invalid")
        )
        self.ticket.refresh_from_db()
        self.assertEqual(self.ticket.status, Ticket.Status.OPEN)

    def test_invalid_priority_is_rejected_by_check_constraint(self):
        self.assert_rejected_by_database(
            lambda: Ticket.objects.filter(pk=self.ticket.pk).update(priority="invalid")
        )
        self.ticket.refresh_from_db()
        self.assertEqual(self.ticket.priority, Ticket.Priority.NORMAL)

    def test_invalid_audit_field_is_rejected_by_check_constraint(self):
        def insert_invalid_event():
            TicketAuditEvent.objects.create(
                ticket=self.ticket,
                ticket_id_snapshot=self.ticket.pk,
                ticket_reference=self.ticket.reference,
                field="invalid",
                old_value="",
                new_value="",
                actor=self.staff,
                actor_username=self.staff.username,
                actor_was_staff=True,
            )

        self.assert_rejected_by_database(insert_invalid_event)
        self.assertFalse(TicketAuditEvent.objects.exists())

    def test_valid_status_priority_and_audit_event_are_accepted(self):
        self.ticket.status = Ticket.Status.IN_PROGRESS
        self.ticket.priority = Ticket.Priority.HIGH
        self.ticket.save(update_fields=["status", "priority"])

        event = TicketAuditEvent.objects.create(
            ticket=self.ticket,
            ticket_id_snapshot=self.ticket.pk,
            ticket_reference=self.ticket.reference,
            field=TicketAuditEvent.Field.STATUS,
            old_value="open",
            new_value=Ticket.Status.IN_PROGRESS,
            actor=self.staff,
            actor_username=self.staff.username,
            actor_was_staff=True,
        )
        self.assertEqual(event.field, "status")

    def test_staff_update_with_nullable_assignee_succeeds_on_postgresql(self):
        if connection.vendor != "postgresql":
            self.skipTest("Row-locking with an outer join is specific to PostgreSQL")

        self.assertIsNone(self.ticket.assignee)
        self.authenticate(self.staff)
        response = self.client.patch(
            reverse("ticket-detail", args=[self.ticket.pk]),
            {"status": Ticket.Status.IN_PROGRESS, "priority": Ticket.Priority.HIGH},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(TicketAuditEvent.objects.filter(ticket=self.ticket).count(), 2)
        self.ticket.refresh_from_db()
        self.assertEqual(self.ticket.status, Ticket.Status.IN_PROGRESS)
