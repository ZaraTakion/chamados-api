from django.urls import reverse
from rest_framework import status

from tickets.models import Ticket
from tickets.tests.base import APITestBase


class TicketAPITests(APITestBase):
    def test_unauthenticated_user_cannot_list_tickets(self):
        response = self.client.get(reverse("ticket-list"))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_requester_only_sees_own_tickets_and_other_ticket_is_hidden(self):
        self.create_ticket(requester=self.other_user, title="Chamado de outra pessoa")
        self.authenticate(self.requester)

        response = self.client.get(reverse("ticket-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["id"], self.ticket.id)

        self.authenticate(self.other_user)
        hidden = self.client.get(reverse("ticket-detail", args=[self.ticket.id]))
        self.assertEqual(hidden.status_code, status.HTTP_404_NOT_FOUND)

    def test_staff_can_list_all_tickets(self):
        other_ticket = self.create_ticket(requester=self.other_user, title="Outro chamado")
        self.authenticate(self.staff)

        response = self.client.get(reverse("ticket-list"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        ids = {item["id"] for item in response.data["results"]}
        self.assertEqual(ids, {self.ticket.id, other_ticket.id})

    def test_requester_can_create_ticket_and_reference_is_generated(self):
        self.authenticate(self.requester)

        response = self.client.post(
            reverse("ticket-list"),
            {
                "title": "Novo problema",
                "description": "Detalhes do problema.",
                "category": "Conta",
                "priority": "high",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["requester"], self.requester.username)
        self.assertEqual(response.data["priority"], "high")
        self.assertTrue(response.data["reference"].startswith("CH-"))

    def test_requester_can_edit_mutable_fields_but_cannot_change_status_or_assignee(self):
        self.authenticate(self.requester)

        allowed = self.client.patch(
            reverse("ticket-detail", args=[self.ticket.id]),
            {"title": "Título atualizado", "priority": "urgent"},
            format="json",
        )
        forbidden_status = self.client.patch(
            reverse("ticket-detail", args=[self.ticket.id]),
            {"status": "resolved"},
            format="json",
        )
        forbidden_assignee = self.client.patch(
            reverse("ticket-detail", args=[self.ticket.id]),
            {"assignee": self.staff.id},
            format="json",
        )

        self.assertEqual(allowed.status_code, status.HTTP_200_OK)
        self.assertEqual(allowed.data["title"], "Título atualizado")
        self.assertEqual(allowed.data["priority"], "urgent")
        self.assertEqual(forbidden_status.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("status", forbidden_status.data)
        self.assertEqual(forbidden_assignee.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("assignee", forbidden_assignee.data)

    def test_requester_cannot_delete_ticket(self):
        self.authenticate(self.requester)

        response = self.client.delete(reverse("ticket-detail", args=[self.ticket.id]))

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(Ticket.objects.filter(pk=self.ticket.id).exists())

    def test_staff_can_assign_transition_and_delete_ticket(self):
        self.authenticate(self.staff)

        updated = self.client.patch(
            reverse("ticket-detail", args=[self.ticket.id]),
            {"status": "in_progress", "assignee": self.staff.id},
            format="json",
        )
        deleted = self.client.delete(reverse("ticket-detail", args=[self.ticket.id]))

        self.assertEqual(updated.status_code, status.HTTP_200_OK)
        self.assertEqual(updated.data["status"], "in_progress")
        self.assertEqual(updated.data["assignee"], self.staff.id)
        self.assertEqual(deleted.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Ticket.objects.filter(pk=self.ticket.id).exists())

    def test_staff_cannot_assign_ticket_to_non_staff_user(self):
        self.authenticate(self.staff)

        response = self.client.patch(
            reverse("ticket-detail", args=[self.ticket.id]),
            {"assignee": self.other_user.id},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("assignee", response.data)

    def test_closed_ticket_cannot_be_reopened_by_staff(self):
        self.ticket.status = Ticket.Status.CLOSED
        self.ticket.save(update_fields=["status"])
        self.authenticate(self.staff)

        response = self.client.patch(
            reverse("ticket-detail", args=[self.ticket.id]),
            {"status": "in_progress"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("status", response.data)
