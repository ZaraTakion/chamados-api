"""CHM-501: Celery integration and read-only queue summary behavior."""

from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings

from tickets.models import Ticket
from tickets.tasks import ticket_queue_summary


class QueueMetricsTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.requester = get_user_model().objects.create_user(username="queue-metrics-tester", password=None)
        Ticket.objects.create(requester=cls.requester, title="A", description="Test", status=Ticket.Status.OPEN)
        Ticket.objects.create(requester=cls.requester, title="B", description="Test", status=Ticket.Status.OPEN)
        Ticket.objects.create(requester=cls.requester, title="C", description="Test", status=Ticket.Status.WAITING)

    def test_summary_aggregates_real_ticket_statuses(self):
        summary = ticket_queue_summary.run()
        self.assertEqual(summary["total"], 3)
        self.assertEqual(summary["by_status"]["open"], 2)
        self.assertEqual(summary["by_status"]["waiting"], 1)
        self.assertEqual(summary["by_status"]["resolved"], 0)
        self.assertEqual(summary["by_status"]["closed"], 0)
        self.assertEqual(summary["by_status"]["in_progress"], 0)

    def test_repeat_execution_is_read_only_and_idempotent(self):
        with self.assertNumQueries(1):
            first = ticket_queue_summary.run()
        with self.assertNumQueries(1):
            second = ticket_queue_summary.run()
        self.assertEqual(first, second)
        self.assertEqual(Ticket.objects.count(), 3)

    @override_settings(CELERY_TASK_ALWAYS_EAGER=True, CELERY_TASK_EAGER_PROPAGATES=True)
    def test_shared_task_can_run_eagerly_without_redis(self):
        result = ticket_queue_summary.delay()
        self.assertTrue(result.successful())
        self.assertEqual(result.get(timeout=5)["total"], 3)

    def test_aggregate_does_not_include_user_content(self):
        output = str(ticket_queue_summary.run())
        self.assertNotIn(self.requester.username, output)
        self.assertNotIn("queue-metrics-tester", output)
        self.assertNotIn("Test", output)
        self.assertEqual(set(ticket_queue_summary.run()), {"total", "by_status"})

    def test_task_retry_and_timeout_are_explicit(self):
        self.assertEqual(ticket_queue_summary.name, "tickets.queue_summary")
        self.assertEqual(ticket_queue_summary.max_retries, 3)
        self.assertEqual(ticket_queue_summary.soft_time_limit, 20)
        self.assertEqual(ticket_queue_summary.time_limit, 30)
