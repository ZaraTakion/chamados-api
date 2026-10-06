from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from tickets.models import Ticket, TicketComment

User = get_user_model()


class AccountsAndTicketsAPITests(APITestCase):
    def setUp(self):
        self.requester = User.objects.create_user(
            username="solicitante", email="requester@example.com", password="Strong-test-pass-2026!"
        )
        self.other_user = User.objects.create_user(
            username="outra", email="other@example.com", password="Strong-test-pass-2026!"
        )
        self.staff = User.objects.create_user(
            username="suporte", email="support@example.com", password="Strong-test-pass-2026!", is_staff=True
        )
        self.ticket = Ticket.objects.create(
            requester=self.requester,
            title="Não consigo entrar",
            description="O login retorna um erro.",
            category="Acesso",
        )

    def authenticate(self, user):
        response = self.client.post(
            reverse("token_obtain_pair"),
            {"username": user.username, "password": "Strong-test-pass-2026!"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {response.data['access']}")

    def test_registration_hashes_password_and_login_returns_jwt(self):
        registration = self.client.post(
            reverse("register"),
            {"username": "nova-pessoa", "email": "NEW@example.com", "password": "Other-strong-test-pass-2026!"},
            format="json",
        )
        self.assertEqual(registration.status_code, status.HTTP_201_CREATED)
        account = User.objects.get(username="nova-pessoa")
        self.assertTrue(account.check_password("Other-strong-test-pass-2026!"))
        self.assertNotIn("password", registration.data)

        login = self.client.post(
            reverse("token_obtain_pair"),
            {"username": "nova-pessoa", "password": "Other-strong-test-pass-2026!"},
            format="json",
        )
        self.assertEqual(login.status_code, status.HTTP_200_OK)
        self.assertIn("access", login.data)
        self.assertIn("refresh", login.data)

    def test_authenticated_users_only_see_their_own_tickets(self):
        unauthorized = self.client.get("/api/tickets/")
        self.assertEqual(unauthorized.status_code, status.HTTP_401_UNAUTHORIZED)

        self.authenticate(self.requester)
        response = self.client.get(reverse("ticket-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["id"], self.ticket.id)

        self.authenticate(self.other_user)
        response = self.client.get(reverse("ticket-list"))
        self.assertEqual(response.data["count"], 0)
        hidden = self.client.get(reverse("ticket-detail", args=[self.ticket.id]))
        self.assertEqual(hidden.status_code, status.HTTP_404_NOT_FOUND)

    def test_requester_creates_ticket_but_cannot_set_staff_fields(self):
        self.authenticate(self.requester)
        created = self.client.post(
            reverse("ticket-list"),
            {"title": "Novo problema", "description": "Detalhes do problema", "priority": "high"},
            format="json",
        )
        self.assertEqual(created.status_code, status.HTTP_201_CREATED)
        self.assertEqual(created.data["requester"], self.requester.username)
        self.assertTrue(created.data["reference"].startswith("CH-"))

        status_change = self.client.patch(
            reverse("ticket-detail", args=[self.ticket.id]), {"status": "resolved"}, format="json"
        )
        self.assertEqual(status_change.status_code, status.HTTP_400_BAD_REQUEST)

    def test_staff_can_assign_and_transition_ticket(self):
        self.authenticate(self.staff)
        updated = self.client.patch(
            reverse("ticket-detail", args=[self.ticket.id]),
            {"status": "in_progress", "assignee": self.staff.id},
            format="json",
        )
        self.assertEqual(updated.status_code, status.HTTP_200_OK)
        self.assertEqual(updated.data["status"], "in_progress")
        self.assertEqual(updated.data["assignee"], self.staff.id)

    def test_internal_comments_are_hidden_from_requesters(self):
        public_comment = TicketComment.objects.create(
            ticket=self.ticket, author=self.staff, body="Estamos analisando."
        )
        internal_comment = TicketComment.objects.create(
            ticket=self.ticket, author=self.staff, body="Verificar logs internos.", is_internal=True
        )
        self.authenticate(self.requester)
        requester_comments = self.client.get(reverse("ticket-comments", args=[self.ticket.id]))
        self.assertEqual(requester_comments.status_code, status.HTTP_200_OK)
        self.assertEqual([item["id"] for item in requester_comments.data], [public_comment.id])

        denied = self.client.post(
            reverse("ticket-comments", args=[self.ticket.id]),
            {"body": "Nota privada", "is_internal": True},
            format="json",
        )
        self.assertEqual(denied.status_code, status.HTTP_400_BAD_REQUEST)

        self.authenticate(self.staff)
        staff_comments = self.client.get(reverse("ticket-comments", args=[self.ticket.id]))
        self.assertEqual({item["id"] for item in staff_comments.data}, {public_comment.id, internal_comment.id})

    def test_list_filters_search_and_ordering(self):
        self.authenticate(self.requester)
        response = self.client.get(reverse("ticket-list"), {"status": "open", "search": "login", "ordering": "-created_at"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)


class HealthAndSchemaTests(APITestCase):
    def test_health_and_openapi_endpoints_are_public(self):
        self.assertEqual(self.client.get(reverse("health")).status_code, status.HTTP_200_OK)
        self.assertEqual(self.client.get(reverse("schema")).status_code, status.HTTP_200_OK)
