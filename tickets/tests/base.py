from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from tickets.models import Ticket

User = get_user_model()


class APITestBase(APITestCase):
    password = "Strong-test-pass-2026!"

    def setUp(self):
        self.requester = User.objects.create_user(
            username="solicitante",
            email="requester@example.com",
            password=self.password,
        )
        self.other_user = User.objects.create_user(
            username="outra",
            email="other@example.com",
            password=self.password,
        )
        self.staff = User.objects.create_user(
            username="suporte",
            email="support@example.com",
            password=self.password,
            is_staff=True,
        )
        self.ticket = self.create_ticket(
            requester=self.requester,
            title="Não consigo entrar",
            description="O login retorna um erro.",
            category="Acesso",
        )

    def authenticate(self, user):
        response = self.client.post(
            reverse("token_obtain_pair"),
            {"username": user.username, "password": self.password},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {response.data['access']}")
        return response

    def create_ticket(self, requester=None, **overrides):
        data = {
            "requester": requester or self.requester,
            "title": "Chamado de teste",
            "description": "Descrição do chamado de teste.",
            "category": "Geral",
        }
        data.update(overrides)
        return Ticket.objects.create(**data)
