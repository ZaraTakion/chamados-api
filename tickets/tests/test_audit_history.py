from unittest.mock import patch

from django.urls import reverse
from rest_framework import status

from tickets.models import Ticket, TicketAuditEvent
from tickets.tests.base import APITestBase


class TicketAuditHistoryTests(APITestBase):
    def history_url(self, ticket=None):
        return reverse("ticket-history", args=[(ticket or self.ticket).pk])

    def update_ticket(self, payload, ticket=None):
        return self.client.patch(
            reverse("ticket-detail", args=[(ticket or self.ticket).pk]),
            payload,
            format="json",
        )

    def test_staff_changes_are_recorded_with_actor_and_old_new_values(self):
        self.authenticate(self.staff)

        response = self.update_ticket({
            "status": Ticket.Status.IN_PROGRESS,
            "priority": Ticket.Priority.URGENT,
            "assignee": self.staff.pk,
        })

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        events = list(TicketAuditEvent.objects.filter(ticket=self.ticket))
        self.assertEqual([event.field for event in events], ["status", "priority", "assignee"])
        self.assertEqual(
            [(event.old_value, event.new_value) for event in events],
            [("open", "in_progress"), ("normal", "urgent"), ("", str(self.staff.pk))],
        )
        for event in events:
            self.assertEqual(event.ticket_reference, self.ticket.reference)
            self.assertEqual(event.ticket_id_snapshot, self.ticket.pk)
            self.assertEqual(event.actor, self.staff)
            self.assertEqual(event.actor_username, self.staff.username)
            self.assertTrue(event.actor_was_staff)
            self.assertIsNotNone(event.created_at)

    def test_staff_sees_all_changes_but_requester_sees_redacted_public_history(self):
        self.authenticate(self.staff)
        self.update_ticket({
            "status": Ticket.Status.IN_PROGRESS,
            "priority": Ticket.Priority.HIGH,
            "assignee": self.staff.pk,
        })

        staff_history = self.client.get(self.history_url())
        self.assertEqual(staff_history.status_code, status.HTTP_200_OK)
        self.assertEqual(staff_history.data["count"], 3)
        self.assertEqual(
            {item["field"] for item in staff_history.data["results"]},
            {"status", "priority", "assignee"},
        )
        self.assertEqual(
            {item["actor_display"] for item in staff_history.data["results"]},
            {self.staff.username},
        )

        self.authenticate(self.requester)
        requester_history = self.client.get(self.history_url())
        self.assertEqual(requester_history.status_code, status.HTTP_200_OK)
        self.assertEqual(requester_history.data["count"], 2)
        self.assertEqual(
            {item["field"] for item in requester_history.data["results"]},
            {"status", "priority"},
        )
        self.assertEqual(
            {item["actor_display"] for item in requester_history.data["results"]},
            {"Equipe de suporte"},
        )
        self.assertNotIn(self.staff.username, str(requester_history.data))

    def test_requester_priority_change_is_recorded_without_exposing_username(self):
        self.authenticate(self.requester)

        changed = self.update_ticket({"priority": Ticket.Priority.HIGH})
        history = self.client.get(self.history_url())

        self.assertEqual(changed.status_code, status.HTTP_200_OK)
        self.assertEqual(history.status_code, status.HTTP_200_OK)
        self.assertEqual(history.data["count"], 1)
        record = history.data["results"][0]
        self.assertEqual(record["field"], "priority")
        self.assertEqual(record["old_value"], "normal")
        self.assertEqual(record["new_value"], "high")
        self.assertEqual(record["actor_display"], "Solicitante")
        self.assertNotIn(self.requester.username, str(history.data))

    def test_invalid_transition_cannot_change_data_or_write_history(self):
        self.authenticate(self.staff)

        changed = self.update_ticket({"status": Ticket.Status.RESOLVED})

        self.assertEqual(changed.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("status", changed.data)
        self.ticket.refresh_from_db()
        self.assertEqual(self.ticket.status, Ticket.Status.OPEN)
        self.assertFalse(TicketAuditEvent.objects.exists())

    def test_requester_cannot_change_status_and_no_history_is_recorded(self):
        self.authenticate(self.requester)

        response = self.update_ticket({"status": Ticket.Status.IN_PROGRESS})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(TicketAuditEvent.objects.exists())

    def test_idempotent_update_and_unrelated_edit_do_not_create_events(self):
        self.authenticate(self.staff)

        self.assertEqual(
            self.update_ticket({"status": Ticket.Status.OPEN, "priority": Ticket.Priority.NORMAL}).status_code,
            status.HTTP_200_OK,
        )
        self.assertEqual(self.update_ticket({"title": "Novo título"}).status_code, status.HTTP_200_OK)
        self.assertEqual(TicketAuditEvent.objects.count(), 0)

    def test_anonymous_and_other_requester_cannot_read_history(self):
        unauthorized = self.client.get(self.history_url())
        self.assertEqual(unauthorized.status_code, status.HTTP_401_UNAUTHORIZED)

        self.authenticate(self.staff)
        self.update_ticket({"status": Ticket.Status.IN_PROGRESS})

        self.authenticate(self.other_user)
        denied = self.client.get(self.history_url())
        self.assertEqual(denied.status_code, status.HTTP_404_NOT_FOUND)

    def test_staff_can_view_history_of_another_requester_ticket(self):
        other_ticket = self.create_ticket(requester=self.other_user)
        self.authenticate(self.staff)

        self.assertEqual(
            self.update_ticket({"priority": Ticket.Priority.HIGH}, ticket=other_ticket).status_code,
            status.HTTP_200_OK,
        )
        history = self.client.get(self.history_url(other_ticket))

        self.assertEqual(history.status_code, status.HTTP_200_OK)
        self.assertEqual(history.data["count"], 1)

    def test_history_endpoint_is_read_only(self):
        self.authenticate(self.staff)

        response = self.client.post(self.history_url(), {"field": "status"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        self.assertFalse(TicketAuditEvent.objects.exists())

    def test_audit_write_failure_rolls_back_ticket_update(self):
        self.authenticate(self.staff)

        with patch("tickets.audit.TicketAuditEvent.objects.bulk_create", side_effect=RuntimeError("database error")):
            with self.assertRaisesRegex(RuntimeError, "database error"):
                self.update_ticket({"priority": Ticket.Priority.HIGH})

        self.ticket.refresh_from_db()
        self.assertEqual(self.ticket.priority, Ticket.Priority.NORMAL)
        self.assertFalse(TicketAuditEvent.objects.exists())

    def test_history_survives_ticket_deletion_with_reference_snapshot(self):
        self.authenticate(self.staff)
        self.assertEqual(
            self.update_ticket({"status": Ticket.Status.IN_PROGRESS}).status_code,
            status.HTTP_200_OK,
        )
        original_reference = self.ticket.reference

        deleted = self.client.delete(reverse("ticket-detail", args=[self.ticket.pk]))

        self.assertEqual(deleted.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(TicketAuditEvent.objects.count(), 1)
        event = TicketAuditEvent.objects.get()
        self.assertIsNone(event.ticket)
        self.assertEqual(event.ticket_reference, original_reference)

    def test_actor_deletion_preserves_name_snapshot(self):
        self.authenticate(self.staff)
        self.update_ticket({"priority": Ticket.Priority.HIGH})
        username = self.staff.username

        self.staff.delete()

        event = TicketAuditEvent.objects.get()
        self.assertIsNone(event.actor)
        self.assertEqual(event.actor_username, username)

    def test_openapi_includes_history_get_endpoint(self):
        self.authenticate(self.staff)
        with self.assertNoLogs("drf_spectacular", level="WARNING"):
            response = self.client.get(reverse("schema"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("/api/tickets/{ticket_pk}/history/", response.data["paths"])
        operations = response.data["paths"]["/api/tickets/{ticket_pk}/history/"]
        self.assertIn("get", operations)
        self.assertNotIn("post", operations)
