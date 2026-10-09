"""CHM-601: exercise JWT, tickets and private notification inbox end-to-end.

These tests use disposable Django test databases and synthetic users.
They never connect to the user's running localhost or require Redis.
"""

from io import StringIO
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.test import TestCase, override_settings
from django.urls import reverse
from rest_framework.test import APIClient

from tickets.models import NotificationOutbox, TicketNotification


@override_settings(DEBUG=True)
class LocalDemoEndToEndTests(TestCase):
    """Reproduce the Swagger walkthrough using real JWT authentication."""

    def setUp(self):
        self.staff_username = "support-ci-only"
        self.staff_password = "Only-A-Synthetic-Test-Secret-2026!"
        self.requester_username = "requester-ci-only"
        self.requester_password = "Other-Synthetic-Testing-Password-2026!"
        get_user_model().objects.create_user(
            username=self.staff_username,
            password=self.staff_password,
            is_staff=True,
            is_active=True,
        )
        self.anonymous = APIClient()

    def _login(self, username, password):
        response = self.anonymous.post(
            reverse("token_obtain_pair"),
            {"username": username, "password": password},
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("access", response.data)
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION=f"Bearer {response.data['access']}")
        return client

    def test_jwt_ticket_event_worker_inbox_and_user_isolation(self):
        registered = self.anonymous.post(
            reverse("register"),
            {
                "username": self.requester_username,
                "email": "requester-ci-only@example.invalid",
                "password": self.requester_password,
            },
            format="json",
        )
        self.assertEqual(registered.status_code, 201)
        self.assertNotIn("password", registered.data)

        requester = self._login(self.requester_username, self.requester_password)
        self.assertEqual(requester.get(reverse("me")).status_code, 200)

        with patch(
            "tickets.tasks.deliver_pending_notifications.delay",
            side_effect=OSError("No Redis in this test"),
        ) as publish:
            created = requester.post(
                reverse("ticket-list"),
                {
                    "title": "Synthetic support ticket",
                    "description": "Only disposable demo text",
                    "category": "suporte",
                },
                format="json",
            )
        self.assertEqual(created.status_code, 201)
        self.assertFalse(publish.called)
        reference = created.data["reference"]
        event = NotificationOutbox.objects.get(ticket_reference=reference)
        self.assertEqual(event.kind, NotificationOutbox.Kind.CREATED)
        self.assertIsNone(event.processed_at)

        output = StringIO()
        call_command("process_notifications", stdout=output)
        self.assertIn("Notificacoes processadas: 1", output.getvalue())
        event.refresh_from_db()
        self.assertIsNotNone(event.processed_at)

        staff = self._login(self.staff_username, self.staff_password)
        profile = staff.get(reverse("me"))
        self.assertEqual(profile.status_code, 200)
        self.assertEqual(profile.data["username"], self.staff_username)
        self.assertTrue(profile.data["is_staff"])
        inbox = staff.get(reverse("notifications"))
        self.assertEqual(inbox.status_code, 200)
        results = inbox.data["results"]
        self.assertEqual(inbox.data["count"], 1)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["kind"], "ticket_created")
        self.assertEqual(results[0]["ticket_reference"], reference)
        self.assertEqual(
            set(results[0]),
            {"id", "kind", "ticket_reference", "created_at"},
        )
        self.assertEqual(TicketNotification.objects.count(), 1)

        other_inbox = requester.get(reverse("notifications"))
        self.assertEqual(other_inbox.status_code, 200)
        self.assertEqual(other_inbox.data["count"], 0)
        self.assertEqual(self.anonymous.get(reverse("notifications")).status_code, 401)

        # The CLI must remain idempotent, even if invoked repeatedly.
        another_output = StringIO()
        call_command("process_notifications", stdout=another_output)
        self.assertIn("Notificacoes processadas: 0", another_output.getvalue())
        self.assertEqual(TicketNotification.objects.count(), 1)
