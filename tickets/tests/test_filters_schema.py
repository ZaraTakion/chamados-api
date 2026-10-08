from django.urls import reverse
from rest_framework import status

from tickets.tests.base import APITestBase


class FiltersPaginationAndSchemaTests(APITestBase):
    def test_filters_search_and_ordering_can_be_combined(self):
        older = self.create_ticket(
            title="Falha de pagamento",
            description="Cartão recusado.",
            category="Financeiro",
            priority="high",
            status="open",
        )
        self.create_ticket(
            title="Problema de perfil",
            description="Não consigo editar avatar.",
            category="Perfil",
            priority="low",
            status="waiting",
        )
        self.authenticate(self.requester)

        filtered = self.client.get(
            reverse("ticket-list"),
            {
                "status": "open",
                "priority": "high",
                "category": "Financeiro",
                "search": "pagamento",
                "ordering": "created_at",
            },
        )

        self.assertEqual(filtered.status_code, status.HTTP_200_OK)
        self.assertEqual(filtered.data["count"], 1)
        self.assertEqual(filtered.data["results"][0]["id"], older.id)

    def test_staff_can_filter_by_assignee_and_order_by_creation(self):
        assigned = self.create_ticket(
            requester=self.other_user,
            title="Chamado atribuído",
            assignee=self.staff,
        )
        self.create_ticket(requester=self.other_user, title="Sem responsável")
        self.authenticate(self.staff)

        filtered = self.client.get(
            reverse("ticket-list"),
            {"assignee": self.staff.id, "ordering": "created_at"},
        )

        self.assertEqual(filtered.status_code, status.HTTP_200_OK)
        self.assertEqual(filtered.data["count"], 1)
        self.assertEqual(filtered.data["results"][0]["id"], assigned.id)

    def test_ordering_by_created_at_is_applied(self):
        second = self.create_ticket(title="Segundo chamado")
        third = self.create_ticket(title="Terceiro chamado")
        self.authenticate(self.requester)

        response = self.client.get(reverse("ticket-list"), {"ordering": "created_at"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        ids = [item["id"] for item in response.data["results"]]
        self.assertEqual(ids[:3], [self.ticket.id, second.id, third.id])

    def test_pagination_uses_twenty_items_per_page(self):
        for index in range(20):
            self.create_ticket(title=f"Chamado {index:02d}")
        self.authenticate(self.requester)

        first_page = self.client.get(reverse("ticket-list"))
        second_page = self.client.get(reverse("ticket-list"), {"page": 2})

        self.assertEqual(first_page.status_code, status.HTTP_200_OK)
        self.assertEqual(first_page.data["count"], 21)
        self.assertEqual(len(first_page.data["results"]), 20)
        self.assertIsNotNone(first_page.data["next"])
        self.assertEqual(second_page.status_code, status.HTTP_200_OK)
        self.assertEqual(len(second_page.data["results"]), 1)

    def test_health_endpoint_is_public_and_has_expected_contract(self):
        response = self.client.get(reverse("health"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], "ok")
        self.assertIn("timestamp", response.data)

    def test_openapi_schema_is_public_contains_core_paths_and_emits_no_warnings(self):
        with self.assertNoLogs("drf_spectacular", level="WARNING"):
            response = self.client.get(reverse("schema"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        paths = response.data["paths"]
        self.assertIn("/api/health/", paths)
        self.assertIn("/api/auth/me/", paths)
        self.assertIn("/api/tickets/", paths)
        self.assertIn("/api/tickets/{id}/", paths)
        self.assertIn("/api/tickets/{ticket_pk}/comments/", paths)
