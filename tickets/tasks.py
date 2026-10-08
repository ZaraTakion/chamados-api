"""Read-only, repeatable queue metrics for background execution."""

from celery import shared_task
from django.db import OperationalError
from django.db.models import Count

from tickets.models import Ticket


@shared_task(
    name="tickets.queue_summary",
    autoretry_for=(OperationalError,),
    retry_backoff=True,
    retry_jitter=True,
    retry_kwargs={"max_retries": 3},
    soft_time_limit=20,
    time_limit=30,
)
def ticket_queue_summary():
    """Return aggregate status counts; never persist or publish user data.

    Repeat executions do not mutate application state. A snapshot reflects the
    database at query time, so concurrent new tickets can alter later results.
    """
    by_status = {key: 0 for key, _label in Ticket.Status.choices}
    counts = Ticket.objects.order_by().values("status").annotate(total=Count("pk"))
    for item in counts:
        by_status[item["status"]] = item["total"]
    return {"total": sum(by_status.values()), "by_status": by_status}
