from django.test import SimpleTestCase
from django.urls import reverse
from rest_framework import status

from tickets.models import Ticket
from tickets.tests.base import APITestBase
from tickets.transitions import (
    ALLOWED_STATUS_TRANSITIONS,
    InvalidStatusTransition,
    validate_ticket_transition,
)


class TicketTransitionDomainTests(SimpleTestCase):
    def test_all_statuses_have_a_defined_transition_set(self):
        self.assertEqual(set(ALLOWED_STATUS_TRANSITIONS), set(Ticket.Status.values))

    def test_all_status_pairs_follow_the_documented_matrix(self):
        for origin in Ticket.Status.values:
            for target in Ticket.Status.values:
                with self.subTest(origin=origin, target=target):
                    allowed = origin == target or target in ALLOWED_STATUS_TRANSITIONS[origin]
                    if allowed:
                        self.assertIsNone(validate_ticket_transition(origin, target))
                    else:
                        with self.assertRaises(InvalidStatusTransition):
                            validate_ticket_transition(origin, target)

    def test_unknown_current_state_is_rejected(self):
        with self.assertRaises(InvalidStatusTransition):
            validate_ticket_transition("unknown", Ticket.Status.OPEN)

    def test_closed_is_terminal(self):
        self.assertEqual(ALLOWED_STATUS_TRANSITIONS[Ticket.Status.CLOSED], frozenset())
        with self.assertRaisesRegex(InvalidStatusTransition, "fechado"):
            validate_ticket_transition(Ticket.Status.CLOSED, Ticket.Status.IN_PROGRESS)


class TicketTransitionAPITests(APITestBase):
    def change_status(self, value):
        return self.client.patch(
            reverse("ticket-detail", args=[self.ticket.id]),
            {"status": value},
            format="json",
        )

    def test_staff_can_follow_full_lifecycle(self):
        self.authenticate(self.staff)

        for next_status in (
            Ticket.Status.IN_PROGRESS,
            Ticket.Status.WAITING,
            Ticket.Status.RESOLVED,
            Ticket.Status.CLOSED,
        ):
            with self.subTest(next_status=next_status):
                response = self.change_status(next_status)
                self.assertEqual(response.status_code, status.HTTP_200_OK)
                self.assertEqual(response.data["status"], next_status)

        self.ticket.refresh_from_db()
        self.assertEqual(self.ticket.status, Ticket.Status.CLOSED)

    def test_staff_can_return_resolved_to_in_progress(self):
        self.ticket.status = Ticket.Status.RESOLVED
        self.ticket.save(update_fields=["status"])
        self.authenticate(self.staff)

        response = self.change_status(Ticket.Status.IN_PROGRESS)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], Ticket.Status.IN_PROGRESS)

    def test_staff_cannot_skip_from_open_to_resolved(self):
        self.authenticate(self.staff)

        response = self.change_status(Ticket.Status.RESOLVED)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("status", response.data)
        self.ticket.refresh_from_db()
        self.assertEqual(self.ticket.status, Ticket.Status.OPEN)

    def test_staff_can_send_current_status_without_transition(self):
        self.ticket.status = Ticket.Status.CLOSED
        self.ticket.save(update_fields=["status"])
        self.authenticate(self.staff)

        response = self.change_status(Ticket.Status.CLOSED)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], Ticket.Status.CLOSED)

    def test_closed_ticket_cannot_be_reopened_but_other_fields_can_be_edited(self):
        self.ticket.status = Ticket.Status.CLOSED
        self.ticket.save(update_fields=["status"])
        self.authenticate(self.staff)

        forbidden = self.change_status(Ticket.Status.IN_PROGRESS)
        allowed = self.client.patch(
            reverse("ticket-detail", args=[self.ticket.id]),
            {"title": "Atualização administrativa"},
            format="json",
        )

        self.assertEqual(forbidden.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("status", forbidden.data)
        self.assertEqual(allowed.status_code, status.HTTP_200_OK)
        self.assertEqual(allowed.data["title"], "Atualização administrativa")
        self.ticket.refresh_from_db()
        self.assertEqual(self.ticket.status, Ticket.Status.CLOSED)

    def test_requester_cannot_change_status_even_to_same_value(self):
        self.authenticate(self.requester)

        response = self.change_status(Ticket.Status.OPEN)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("status", response.data)
