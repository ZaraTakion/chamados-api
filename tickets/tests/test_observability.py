"""CHM-401 regression tests: correlation, safe logging and error diagnosis."""

import json
import logging
import re
from unittest.mock import patch

from django.test import override_settings
from django.urls import reverse

from chamados_api.observability import SafeJSONFormatter, get_request_id
from tickets.tests.base import APITestBase
from tickets.views import TicketViewSet


class RequestObservabilityTests(APITestBase):
    def test_request_id_is_unique_and_not_taken_from_client_headers(self):
        with patch("chamados_api.observability.request_logger.log") as log:
            first = self.client.get(reverse("health"), HTTP_X_REQUEST_ID="client-controlled-value")
            second = self.client.get(reverse("health"), HTTP_X_REQUEST_ID="client-controlled-value")

        first_id, second_id = first["X-Request-ID"], second["X-Request-ID"]
        self.assertRegex(first_id, r"^[0-9a-f]{32}$")
        self.assertNotEqual(first_id, second_id)
        self.assertNotEqual(first_id, "client-controlled-value")
        self.assertEqual(log.call_count, 2)
        self.assertEqual(log.call_args.kwargs["extra"]["request_id"], second_id)
        self.assertIsNone(get_request_id())

    def test_request_metadata_uses_route_template_not_sensitive_url(self):
        with patch("chamados_api.observability.request_logger.log") as log:
            response = self.client.get(reverse("health") + "?password=private-password&token=private-jwt")

        self.assertEqual(response.status_code, 200)
        extra = log.call_args.kwargs["extra"]
        self.assertEqual(extra["event"], "http.request")
        self.assertEqual(extra["method"], "GET")
        self.assertEqual(extra["route"], "api/health/")
        self.assertEqual(extra["status_code"], 200)
        self.assertGreaterEqual(extra["duration_ms"], 0)
        self.assertNotIn("password", str(extra))
        self.assertNotIn("private-jwt", str(extra))

    def test_missing_authentication_preserves_contract_and_correlation(self):
        with patch("chamados_api.observability.request_logger.log") as log:
            response = self.client.get(reverse("ticket-list"))

        self.assertEqual(response.status_code, 401)
        self.assertRegex(response["X-Request-ID"], r"^[0-9a-f]{32}$")
        self.assertEqual(response.data["error"]["code"], "authentication_error")
        self.assertEqual(log.call_args.kwargs["extra"]["status_code"], 401)

    def test_unmatched_request_path_is_not_written_to_logs(self):
        with patch("chamados_api.observability.request_logger.log") as log:
            response = self.client.get("/private-secret-segment/?authorization=private-token")

        self.assertEqual(response.status_code, 404)
        extra = log.call_args.kwargs["extra"]
        self.assertEqual(extra["route"], "unmatched")
        self.assertNotIn("private-secret", str(extra))
        self.assertNotIn("private-token", str(extra))
        self.assertIn("X-Request-ID", response)

    def test_5xx_emits_error_with_id_without_exception_text(self):
        self.authenticate(self.requester)
        self.client.raise_request_exception = False
        with override_settings(DEBUG=False):
            with patch.object(TicketViewSet, "list", side_effect=RuntimeError("private-password-and-token")):
                with patch("chamados_api.observability.request_logger.log") as log:
                    response = self.client.get(reverse("ticket-list"))

        self.assertEqual(response.status_code, 500)
        self.assertRegex(response["X-Request-ID"], r"^[0-9a-f]{32}$")
        level, event = log.call_args.args
        extra = log.call_args.kwargs["extra"]
        self.assertEqual(level, logging.ERROR)
        self.assertEqual(event, "http.server_error")
        self.assertEqual(extra["request_id"], response["X-Request-ID"])
        self.assertEqual(extra["route"], "api/tickets/$")
        self.assertNotIn("private-password-and-token", str(extra))
        self.assertIsNone(get_request_id())

    def test_json_formatter_allowlists_fields_even_when_message_is_sensitive(self):
        record = logging.LogRecord(
            name="chamados_api.http",
            level=logging.ERROR,
            pathname=__file__,
            lineno=1,
            msg="Authorization: Bearer sensitive-token, password=private-password",
            args=(),
            exc_info=None,
        )
        record.event = "http.server_error"
        record.request_id = "0" * 32
        record.method = "GET"
        record.route = "api/tickets/<int:pk>/"
        record.status_code = 500
        record.duration_ms = 3.12
        record.request_body = "private-body"
        record.query_string = "token=private-query"

        formatted = SafeJSONFormatter().format(record)
        data = json.loads(formatted)
        self.assertEqual(data["event"], "http.server_error")
        self.assertEqual(data["request_id"], "0" * 32)
        self.assertEqual(data["status_code"], 500)
        self.assertEqual(data["route"], "api/tickets/<int:pk>/")
        self.assertFalse(re.search(r"password|sensitive-token|private-body|private-query", formatted))

    def test_framework_logs_do_not_serialize_raw_message_or_traceback(self):
        record = logging.LogRecord(
            name="django.request",
            level=logging.ERROR,
            pathname=__file__,
            lineno=1,
            msg="Internal Server Error at /auth/?token=private-token",
            args=(),
            exc_info=None,
        )
        record.stack_info = "private-stack-data"
        formatted = SafeJSONFormatter().format(record)
        data = json.loads(formatted)
        self.assertEqual(data["event"], "framework.error")
        self.assertNotIn("private-token", formatted)
        self.assertNotIn("private-stack-data", formatted)
        self.assertNotIn("route", data)
