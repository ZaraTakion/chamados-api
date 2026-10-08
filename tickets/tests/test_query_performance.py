"""SQL query count baselines for critical API endpoints.

The measurements include authentication and pagination queries. We compare
within the same endpoint and role to detect N+1, not request latency.
"""

from django.db import connection
from django.test.utils import CaptureQueriesContext
from django.urls import reverse
from rest_framework import status

from tickets.models import Ticket, TicketAuditEvent, TicketComment
from tickets.serializers import TicketCommentSerializer, TicketSerializer
from tickets.tests.base import APITestBase


class ORMQueryBaselineTests(APITestBase):
    def measure_get(self, name, url, expected_count=None):
        with CaptureQueriesContext(connection) as queries:
            response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        if expected_count is not None:
            self.assertEqual(response.data["count"], expected_count)
            self.assertEqual(len(response.data["results"]), expected_count)
        return len(queries)

    def compare_scaling(self, label, small, large):
        # The same endpoint/role should issue a bounded number of queries,
        # independent of how many related objects it serializes per page.
        print(f"CHM301_BASELINE {label}: 1={small} 20={large}", flush=True)
        self.assertLessEqual(
            large, small + 1,
            f"{label} grows with collection size: 1={small}, 20={large}",
        )

    def add_nineteen_tickets(self, requester=None):
        for index in range(19):
            self.create_ticket(
                requester=requester or self.requester,
                title=f"Chamado de volume {index:02d}",
                assignee=self.staff if index % 2 == 0 else None,
            )

    def test_staff_ticket_list_constant_query_count(self):
        self.authenticate(self.staff)
        url = reverse("ticket-list")
        small = self.measure_get("staff-list", url, expected_count=1)
        self.add_nineteen_tickets(requester=self.other_user)
        large = self.measure_get("staff-list", url, expected_count=20)
        self.compare_scaling("staff_ticket_list", small, large)

    def test_requester_ticket_list_constant_query_count(self):
        self.authenticate(self.requester)
        url = reverse("ticket-list")
        small = self.measure_get("requester-list", url, expected_count=1)
        self.add_nineteen_tickets()
        large = self.measure_get("requester-list", url, expected_count=20)
        self.compare_scaling("requester_ticket_list", small, large)

    def verify_ticket_detail_scaling(self, user, role):
        url = reverse("ticket-detail", args=[self.ticket.pk])
        self.authenticate(user)
        small = self.measure_get(f"{role}-detail", url)
        self.add_nineteen_tickets(requester=self.other_user)
        large = self.measure_get(f"{role}-detail", url)
        self.compare_scaling(f"{role}_ticket_detail", small, large)

    def test_staff_ticket_detail_constant_query_count(self):
        self.verify_ticket_detail_scaling(self.staff, "staff")

    def test_requester_ticket_detail_constant_query_count(self):
        self.verify_ticket_detail_scaling(self.requester, "requester")

    def add_comments(self, count):
        for index in range(count):
            TicketComment.objects.create(
                ticket=self.ticket,
                author=(self.staff, self.requester, self.other_user)[index % 3],
                body=f"Comentário {index:02d}",
                is_internal=False,
            )

    def test_staff_and_requester_comments_constant_query_count(self):
        url = reverse("ticket-comments", args=[self.ticket.pk])
        self.add_comments(1)
        self.authenticate(self.staff)
        staff_small = self.measure_get("staff-comments", url, expected_count=1)
        self.authenticate(self.requester)
        requester_small = self.measure_get("requester-comments", url, expected_count=1)

        self.add_comments(19)
        self.authenticate(self.staff)
        staff_large = self.measure_get("staff-comments", url, expected_count=20)
        self.authenticate(self.requester)
        requester_large = self.measure_get("requester-comments", url, expected_count=20)

        self.compare_scaling("staff_comment_list", staff_small, staff_large)
        self.compare_scaling("requester_comment_list", requester_small, requester_large)

    def add_audit_events(self, count):
        TicketAuditEvent.objects.bulk_create([
            TicketAuditEvent(
                ticket=self.ticket,
                ticket_id_snapshot=self.ticket.pk,
                ticket_reference=self.ticket.reference,
                field=TicketAuditEvent.Field.PRIORITY,
                old_value="normal",
                new_value="high",
                actor=self.staff,
                actor_username=self.staff.username,
                actor_was_staff=True,
            )
            for _ in range(count)
        ])

    def test_staff_and_requester_history_constant_query_count(self):
        url = reverse("ticket-history", args=[self.ticket.pk])
        self.add_audit_events(1)
        self.authenticate(self.staff)
        staff_small = self.measure_get("staff-history", url, expected_count=1)
        self.authenticate(self.requester)
        requester_small = self.measure_get("requester-history", url, expected_count=1)

        self.add_audit_events(19)
        self.authenticate(self.staff)
        staff_large = self.measure_get("staff-history", url, expected_count=20)
        self.authenticate(self.requester)
        requester_large = self.measure_get("requester-history", url, expected_count=20)

        self.compare_scaling("staff_audit_history", staff_small, staff_large)
        self.compare_scaling("requester_audit_history", requester_small, requester_large)

    def test_ticket_serializer_without_join_exhibits_n_plus_one(self):
        self.add_nineteen_tickets()
        def count_queries(qs):
            with CaptureQueriesContext(connection) as queries:
                data = TicketSerializer(qs, many=True).data
                self.assertEqual(len(data), 20)
            return len(queries)

        naive = count_queries(Ticket.objects.order_by("id"))
        joined = count_queries(Ticket.objects.select_related("requester", "assignee").order_by("id"))
        print(f"CHM301_BASELINE ticket_serializer: naive={naive} select_related={joined}", flush=True)
        self.assertGreaterEqual(naive, joined + 10)
        self.assertLessEqual(joined, 2)

    def test_comment_serializer_without_join_exhibits_n_plus_one(self):
        self.add_comments(20)

        def count_queries(qs):
            with CaptureQueriesContext(connection) as queries:
                data = TicketCommentSerializer(qs, many=True).data
                self.assertEqual(len(data), 20)
            return len(queries)

        naive = count_queries(TicketComment.objects.filter(ticket=self.ticket))
        joined = count_queries(
            TicketComment.objects.filter(ticket=self.ticket).select_related("author")
        )
        print(f"CHM301_BASELINE comment_serializer: naive={naive} select_related={joined}", flush=True)
        self.assertGreaterEqual(naive, joined + 10)
        self.assertLessEqual(joined, 2)
