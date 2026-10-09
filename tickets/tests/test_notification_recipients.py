"""Regression coverage for revoking access to ticket notification recipients."""

from django.urls import reverse
from rest_framework import status

from tickets.models import NotificationOutbox, TicketAuditEvent
from tickets.notifications import ticket_updated
from tickets.tests.base import APITestBase


class NotificationRecipientAccessTests(APITestBase):
    def setUp(self):
        super().setUp()
        self.ticket.assignee = self.staff
        self.ticket.save(update_fields=["assignee"])

    def post_requester_comment(self):
        self.authenticate(self.requester)
        return self.client.post(
            reverse("ticket-comments", args=[self.ticket.pk]),
            {"body": "Posso receber uma atualização?"},
            format="json",
        )

    def test_active_staff_assignee_receives_new_public_comment(self):
        response = self.post_requester_comment()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(
            list(NotificationOutbox.objects.values_list("recipient_id", flat=True)),
            [self.staff.pk],
        )

    def test_demoted_assignee_does_not_receive_new_public_comment(self):
        self.staff.is_staff = False
        self.staff.save(update_fields=["is_staff"])
        response = self.post_requester_comment()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertFalse(NotificationOutbox.objects.filter(recipient=self.staff).exists())

    def test_deactivated_assignee_does_not_receive_new_public_comment(self):
        self.staff.is_active = False
        self.staff.save(update_fields=["is_active"])
        response = self.post_requester_comment()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertFalse(NotificationOutbox.objects.filter(recipient=self.staff).exists())

    def test_demoted_assignee_does_not_receive_assignment_event(self):
        self.staff.is_staff = False
        self.staff.save(update_fields=["is_staff"])
        ticket_updated(
            self.ticket,
            self.requester,
            [TicketAuditEvent(field=TicketAuditEvent.Field.ASSIGNEE)],
        )
        self.assertFalse(NotificationOutbox.objects.filter(recipient=self.staff).exists())
