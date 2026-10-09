"""Tests for running notification delivery locally without a broker."""

from io import StringIO
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.core.management.base import CommandError
from django.db import OperationalError
from django.test import TestCase, override_settings

from tickets.models import NotificationOutbox, TicketNotification


@override_settings(DEBUG=True)
class OfflineNotificationTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username="offline-test-user")
        self.event = NotificationOutbox.objects.create(
            recipient=self.user,
            kind=NotificationOutbox.Kind.CREATED,
            ticket_reference="CH-000123",
        )

    def test_one_shot_is_idempotent_without_redis(self):
        out = StringIO()
        with patch("tickets.tasks.deliver_pending_notifications.delay") as publish:
            call_command("process_notifications", stdout=out)
            call_command("process_notifications", stdout=out)
        publish.assert_not_called()
        self.assertEqual(TicketNotification.objects.count(), 1)
        self.assertIn("Notificacoes processadas: 1", out.getvalue())
        self.assertIn("Notificacoes processadas: 0", out.getvalue())

    def test_watch_processes_and_stops(self):
        out = StringIO()
        with patch(
            "tickets.management.commands.process_notifications.time.sleep",
            side_effect=KeyboardInterrupt,
        ):
            call_command("process_notifications", "--watch", stdout=out)
        self.assertEqual(TicketNotification.objects.count(), 1)
        self.assertIn("Processador local encerrado.", out.getvalue())

    @override_settings(DEBUG=False)
    def test_never_available_in_production(self):
        with self.assertRaises(CommandError):
            call_command("process_notifications")

    def test_invalid_interval_rejected(self):
        with self.assertRaises(CommandError):
            call_command("process_notifications", "--interval", "0")

    def test_transient_database_error_does_not_lose_outbox(self):
        with patch(
            "tickets.management.commands.process_notifications.deliver_pending_notifications.run",
            side_effect=OperationalError("temporary database failure"),
        ):
            with self.assertRaises(CommandError):
                call_command("process_notifications")
        self.event.refresh_from_db()
        self.assertIsNone(self.event.processed_at)
        call_command("process_notifications", stdout=StringIO())
        self.assertEqual(TicketNotification.objects.count(), 1)

    def test_watch_handles_database_failure_without_exposing_details(self):
        output = StringIO()
        errors = StringIO()
        with (
            patch(
                "tickets.management.commands.process_notifications.deliver_pending_notifications.run",
                side_effect=[OperationalError("private database details"), {"processed": 0}],
            ) as runner,
            patch(
                "tickets.management.commands.process_notifications.time.sleep",
                side_effect=[None, KeyboardInterrupt],
            ),
        ):
            call_command(
                "process_notifications", "--watch", "--interval", "1",
                stdout=output, stderr=errors,
            )
        self.assertEqual(runner.call_count, 2)
        self.assertIn("proximo ciclo", errors.getvalue())
        self.assertNotIn("private database details", errors.getvalue())
