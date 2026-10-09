"""CHM-502 regression tests: privacy, commits, eventual delivery and retries."""

import uuid
from unittest.mock import patch

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.db import IntegrityError, OperationalError, transaction
from django.test import TestCase, override_settings
from django.urls import reverse
from rest_framework.test import APIClient

from tickets.models import NotificationOutbox, Ticket, TicketComment, TicketNotification
from tickets.tasks import deliver_pending_notifications

User = get_user_model()


class NotificationFlowTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.requester = User.objects.create_user(username="notify-requester", password=None)
        cls.other = User.objects.create_user(username="notify-other", password=None)
        cls.staff = User.objects.create_user(username="notify-staff", password=None, is_staff=True)
        cls.assignee = User.objects.create_user(username="notify-assignee", password=None, is_staff=True)
        cls.ticket = Ticket.objects.create(
            requester=cls.requester,
            title="Private ticket title",
            description="private-token-in-description",
        )

    def setUp(self):
        cache.clear()
        self.client = APIClient()
        self.client.force_authenticate(user=self.requester)

    def test_creation_persists_outbox_without_calling_redis_or_publishing(self):
        with patch("tickets.tasks.deliver_pending_notifications.delay", side_effect=OSError("redis down")) as publish:
            response = self.client.post(reverse("ticket-list"), {
                "title": "Do not copy private title",
                "description": "Do not copy secret",
            }, format="json")
        self.assertEqual(response.status_code, 201)
        self.assertFalse(publish.called)
        events = list(NotificationOutbox.objects.filter(kind=NotificationOutbox.Kind.CREATED))
        self.assertEqual({event.recipient_id for event in events}, {self.staff.pk, self.assignee.pk})
        self.assertEqual(TicketNotification.objects.count(), 0)
        self.assertNotIn("Do not copy", str([(event.kind, event.ticket_reference) for event in events]))

    def test_status_and_assignee_changes_notify_only_relevant_recipients(self):
        self.client.force_authenticate(user=self.staff)
        response = self.client.patch(reverse("ticket-detail", args=[self.ticket.pk]), {
            "status": "in_progress", "assignee": self.assignee.pk,
        }, format="json")
        self.assertEqual(response.status_code, 200)
        events = list(NotificationOutbox.objects.all())
        self.assertEqual({(e.kind, e.recipient_id) for e in events}, {
            (NotificationOutbox.Kind.STATUS_CHANGED, self.requester.pk),
            (NotificationOutbox.Kind.ASSIGNED, self.assignee.pk),
        })
        repeated = self.client.patch(reverse("ticket-detail", args=[self.ticket.pk]), {
            "status": "in_progress", "assignee": self.assignee.pk,
        }, format="json")
        self.assertEqual(repeated.status_code, 200)
        self.assertEqual(NotificationOutbox.objects.count(), 2)

    def test_resolved_status_generates_one_specific_event(self):
        self.ticket.status = Ticket.Status.IN_PROGRESS
        self.ticket.save(update_fields=["status"])
        self.client.force_authenticate(user=self.staff)
        response = self.client.patch(reverse("ticket-detail", args=[self.ticket.pk]), {
            "status": "resolved",
        }, format="json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            list(NotificationOutbox.objects.values_list("kind", "recipient_id")),
            [(NotificationOutbox.Kind.RESOLVED, self.requester.pk)],
        )

    def test_public_comment_notifies_requester_and_assignee_but_not_author(self):
        self.ticket.assignee = self.assignee
        self.ticket.save(update_fields=["assignee"])
        self.client.force_authenticate(user=self.staff)
        response = self.client.post(reverse("ticket-comments", args=[self.ticket.pk]), {
            "body": "confidential-body",
        }, format="json")
        self.assertEqual(response.status_code, 201)
        self.assertEqual(
            set(NotificationOutbox.objects.values_list("recipient_id", flat=True)),
            {self.requester.pk, self.assignee.pk},
        )
        self.assertNotIn("confidential-body", str(list(
            NotificationOutbox.objects.values_list("kind", "ticket_reference")
        )))

    def test_internal_comment_never_generates_user_notification(self):
        self.client.force_authenticate(user=self.staff)
        response = self.client.post(reverse("ticket-comments", args=[self.ticket.pk]), {
            "body": "strictly internal secret", "is_internal": True,
        }, format="json")
        self.assertEqual(response.status_code, 201)
        self.assertEqual(NotificationOutbox.objects.count(), 0)
        self.assertTrue(TicketComment.objects.filter(is_internal=True).exists())

    def test_rolled_back_ticket_and_notification_are_not_visible_to_worker(self):
        with self.assertRaisesRegex(RuntimeError, "abort"):
            with transaction.atomic():
                response = self.client.post(reverse("ticket-list"), {
                    "title": "rolled back", "description": "also rolled back",
                }, format="json")
                self.assertEqual(response.status_code, 201)
                self.assertTrue(NotificationOutbox.objects.exists())
                raise RuntimeError("abort")
        self.assertFalse(Ticket.objects.filter(title="rolled back").exists())
        self.assertFalse(NotificationOutbox.objects.exists())
        self.assertEqual(deliver_pending_notifications.run()["processed"], 0)

    def test_worker_consumes_event_once_even_when_run_again(self):
        NotificationOutbox.objects.create(
            recipient=self.requester, kind=NotificationOutbox.Kind.RESOLVED,
            ticket_reference=self.ticket.reference,
        )
        self.assertEqual(deliver_pending_notifications.run(), {"processed": 1})
        self.assertEqual(deliver_pending_notifications.run(), {"processed": 0})
        self.assertEqual(TicketNotification.objects.count(), 1)
        self.assertIsNotNone(NotificationOutbox.objects.get().processed_at)

    def test_worker_failure_leaves_outbox_recoverable(self):
        event = NotificationOutbox.objects.create(
            recipient=self.requester, kind=NotificationOutbox.Kind.CREATED,
            ticket_reference=self.ticket.reference,
        )
        with patch(
            "tickets.tasks.TicketNotification.objects.get_or_create",
            side_effect=OperationalError("private-db-password"),
        ):
            with self.assertRaises(OperationalError):
                deliver_pending_notifications.run()
        event.refresh_from_db()
        self.assertIsNone(event.processed_at)
        self.assertFalse(TicketNotification.objects.exists())
        self.assertEqual(deliver_pending_notifications.run(), {"processed": 1})

    def test_private_inbox_filters_recipient_and_never_exposes_content(self):
        event = NotificationOutbox.objects.create(
            recipient=self.requester, kind=NotificationOutbox.Kind.STATUS_CHANGED,
            ticket_reference=self.ticket.reference,
        )
        deliver_pending_notifications.run()
        response = self.client.get(reverse("notifications"))
        self.assertEqual(response.status_code, 200)
        row = response.data["results"][0]
        self.assertEqual(row["ticket_reference"], self.ticket.reference)
        self.assertEqual(row["kind"], event.kind)
        self.assertEqual(set(row), {"id", "kind", "ticket_reference", "created_at"})
        self.assertNotIn("private-token", str(response.data))
        self.client.force_authenticate(user=self.other)
        other_response = self.client.get(reverse("notifications"))
        self.assertEqual(other_response.status_code, 200)
        self.assertEqual(other_response.data["count"], 0)
        self.client.force_authenticate(user=None)
        self.assertEqual(self.client.get(reverse("notifications")).status_code, 401)

    def test_database_rejects_duplicate_event_recipient_keys(self):
        key = uuid.uuid4()
        NotificationOutbox.objects.create(
            recipient=self.requester, event_key=key,
            kind=NotificationOutbox.Kind.CREATED, ticket_reference=self.ticket.reference,
        )
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                NotificationOutbox.objects.create(
                    recipient=self.requester, event_key=key,
                    kind=NotificationOutbox.Kind.CREATED, ticket_reference=self.ticket.reference,
                )

    def test_worker_configuration_is_bounded_and_periodic(self):
        schedule = settings.CELERY_BEAT_SCHEDULE["deliver-notification-outbox"]
        self.assertEqual(schedule["task"], "tickets.deliver_pending_notifications")
        self.assertEqual(schedule["schedule"], 30.0)
        self.assertEqual(deliver_pending_notifications.max_retries, 3)
        self.assertEqual(deliver_pending_notifications.soft_time_limit, 20)
        self.assertEqual(deliver_pending_notifications.time_limit, 30)

    @override_settings(CELERY_TASK_ALWAYS_EAGER=True, CELERY_TASK_EAGER_PROPAGATES=True)
    def test_eager_worker_processes_real_outbox_without_broker(self):
        NotificationOutbox.objects.create(
            recipient=self.staff, kind=NotificationOutbox.Kind.CREATED,
            ticket_reference=self.ticket.reference,
        )
        result = deliver_pending_notifications.delay()
        self.assertTrue(result.successful())
        self.assertEqual(result.get(timeout=5), {"processed": 1})
        self.assertEqual(TicketNotification.objects.get().recipient_id, self.staff.pk)
