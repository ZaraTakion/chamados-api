from django.urls import reverse
from rest_framework import status

from tickets.models import TicketComment
from tickets.tests.base import APITestBase


class TicketCommentAPITests(APITestBase):
    def test_requester_sees_public_comments_but_not_internal_comments(self):
        public = TicketComment.objects.create(
            ticket=self.ticket,
            author=self.staff,
            body="Estamos analisando.",
        )
        TicketComment.objects.create(
            ticket=self.ticket,
            author=self.staff,
            body="Verificar logs internos.",
            is_internal=True,
        )
        self.authenticate(self.requester)

        response = self.client.get(reverse("ticket-comments", args=[self.ticket.id]))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual([item["id"] for item in response.data["results"]], [public.id])

    def test_requester_can_create_public_comment(self):
        self.authenticate(self.requester)

        response = self.client.post(
            reverse("ticket-comments", args=[self.ticket.id]),
            {"body": "Ainda estou com o problema."},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        comment = TicketComment.objects.get(pk=response.data["id"])
        self.assertEqual(comment.author, self.requester)
        self.assertEqual(comment.ticket, self.ticket)
        self.assertFalse(comment.is_internal)

    def test_requester_cannot_create_internal_comment(self):
        self.authenticate(self.requester)

        response = self.client.post(
            reverse("ticket-comments", args=[self.ticket.id]),
            {"body": "Nota privada", "is_internal": True},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("is_internal", response.data)

    def test_staff_can_create_and_read_internal_comment(self):
        self.authenticate(self.staff)

        created = self.client.post(
            reverse("ticket-comments", args=[self.ticket.id]),
            {"body": "Análise interna", "is_internal": True},
            format="json",
        )
        listed = self.client.get(reverse("ticket-comments", args=[self.ticket.id]))

        self.assertEqual(created.status_code, status.HTTP_201_CREATED)
        self.assertTrue(created.data["is_internal"])
        self.assertIn(created.data["id"], {item["id"] for item in listed.data["results"]})

    def test_other_requester_cannot_read_or_comment_on_ticket(self):
        self.authenticate(self.other_user)

        listed = self.client.get(reverse("ticket-comments", args=[self.ticket.id]))
        created = self.client.post(
            reverse("ticket-comments", args=[self.ticket.id]),
            {"body": "Não deveria entrar."},
            format="json",
        )

        self.assertEqual(listed.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(created.status_code, status.HTTP_404_NOT_FOUND)
