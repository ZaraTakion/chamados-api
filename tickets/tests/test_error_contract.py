"""Contract tests for handled API errors.

We preserve legacy field-level errors while exposing a stable `error` object.
"""

from unittest.mock import patch

from django.core.cache import cache
from django.urls import reverse
from rest_framework import status
from rest_framework.exceptions import ValidationError

from chamados_api.errors import api_exception_handler
from tickets.models import Ticket
from tickets.tests.base import APITestBase


class APIErrorContractTests(APITestBase):
    def assert_error(self, response, status_code, code, original_field):
        self.assertEqual(response.status_code, status_code)
        self.assertIn(original_field, response.data)
        self.assertIn("error", response.data)
        self.assertEqual(response.data["error"]["code"], code)
        self.assertTrue(response.data["error"]["message"])
        self.assertIn(original_field, response.data["error"]["details"])

    def test_missing_authentication_retains_401_and_detail(self):
        response = self.client.get(reverse("ticket-list"))
        self.assert_error(response, status.HTTP_401_UNAUTHORIZED, "authentication_error", "detail")

    def test_invalid_jwt_is_classified_as_authentication_error(self):
        self.client.credentials(HTTP_AUTHORIZATION="Bearer invalid.token")
        response = self.client.get(reverse("ticket-list"))
        self.assert_error(response, status.HTTP_401_UNAUTHORIZED, "authentication_error", "detail")

    def test_forbidden_delete_retains_403_and_detail(self):
        self.authenticate(self.requester)
        response = self.client.delete(reverse("ticket-detail", args=[self.ticket.pk]))
        self.assert_error(response, status.HTTP_403_FORBIDDEN, "permission_denied", "detail")

    def test_hidden_foreign_ticket_retains_404_without_exposing_ticket(self):
        self.authenticate(self.other_user)
        response = self.client.get(reverse("ticket-detail", args=[self.ticket.pk]))
        self.assert_error(response, status.HTTP_404_NOT_FOUND, "not_found", "detail")
        self.assertNotIn(self.ticket.title, str(response.data))

    def test_validation_error_retains_field_detail(self):
        self.authenticate(self.requester)
        response = self.client.post(
            reverse("ticket-list"),
            {"title": "", "description": "Dados de teste"},
            format="json",
        )
        self.assert_error(response, status.HTTP_400_BAD_REQUEST, "validation_error", "title")
        self.assertEqual(response.data["title"], response.data["error"]["details"]["title"])

    def test_invalid_transition_is_a_distinct_business_error(self):
        self.authenticate(self.staff)
        response = self.client.patch(
            reverse("ticket-detail", args=[self.ticket.pk]),
            {"status": Ticket.Status.RESOLVED},
            format="json",
        )
        self.assert_error(response, status.HTTP_400_BAD_REQUEST, "invalid_transition", "status")
        self.ticket.refresh_from_db()
        self.assertEqual(self.ticket.status, Ticket.Status.OPEN)

    def test_requester_restricted_field_keeps_legacy_400(self):
        self.authenticate(self.requester)
        response = self.client.patch(
            reverse("ticket-detail", args=[self.ticket.pk]),
            {"status": Ticket.Status.IN_PROGRESS},
            format="json",
        )
        self.assert_error(response, status.HTTP_400_BAD_REQUEST, "forbidden_field", "status")

    def test_restricted_internal_comment_is_classified(self):
        self.authenticate(self.requester)
        response = self.client.post(
            reverse("ticket-comments", args=[self.ticket.pk]),
            {"body": "Nota interna", "is_internal": True},
            format="json",
        )
        self.assert_error(response, status.HTTP_400_BAD_REQUEST, "forbidden_field", "is_internal")

    def test_read_only_history_rejects_post(self):
        self.authenticate(self.staff)
        response = self.client.post(
            reverse("ticket-history", args=[self.ticket.pk]),
            {"field": "status"},
            format="json",
        )
        self.assert_error(response, status.HTTP_405_METHOD_NOT_ALLOWED, "method_not_allowed", "detail")

    def test_malformed_json_is_classified_without_server_error(self):
        self.authenticate(self.requester)
        response = self.client.generic(
            "POST",
            reverse("ticket-list"),
            data='{"broken":',
            content_type="application/json",
        )
        self.assert_error(response, status.HTTP_400_BAD_REQUEST, "parse_error", "detail")

    def test_throttle_preserves_429_and_retry_after(self):
        cache.clear()
        with patch("rest_framework.throttling.AnonRateThrottle.get_rate", return_value="1/minute"):
            first = self.client.get(reverse("health"))
            blocked = self.client.get(reverse("health"))
        self.assertEqual(first.status_code, status.HTTP_200_OK)
        self.assert_error(blocked, status.HTTP_429_TOO_MANY_REQUESTS, "rate_limited", "detail")
        self.assertIn("Retry-After", blocked)

    def test_success_responses_do_not_gain_error_key(self):
        response = self.client.get(reverse("health"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotIn("error", response.data)

    def test_unhandled_exception_is_left_to_django(self):
        self.assertIsNone(api_exception_handler(RuntimeError("internal secret"), {}))

    def test_list_validation_errors_have_consistent_envelope(self):
        response = api_exception_handler(ValidationError(["Invalid item"]), {})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["error"]["code"], "validation_error")
        self.assertIn("errors", response.data)
        self.assertEqual(response.data["errors"], response.data["error"]["details"])
