"""Read-only, repeatable queue metrics for background execution."""

from celery import shared_task
from django.db import OperationalError, transaction
from django.utils import timezone
from django.db.models import Count

from tickets.models import NotificationOutbox, Ticket, TicketNotification


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


@shared_task(
    name="tickets.deliver_pending_notifications",
    autoretry_for=(OperationalError,),
    retry_backoff=True,
    retry_jitter=True,
    retry_kwargs={"max_retries": 3},
    soft_time_limit=20,
    time_limit=30,
)
def deliver_pending_notifications():
    """Drain up to 100 committed events into per-recipient private inboxes.

    A unique source relation makes retries and concurrent workers idempotent.
    External email/push delivery is intentionally NOT attempted.
    """
    pending_ids = list(
        NotificationOutbox.objects.filter(processed_at__isnull=True)
        .order_by("pk").values_list("pk", flat=True)[:100]
    )
    delivered = 0
    for event_id in pending_ids:
        with transaction.atomic():
            event = NotificationOutbox.objects.select_for_update(of=("self",)).get(pk=event_id)
            if event.processed_at is not None:
                continue
            TicketNotification.objects.get_or_create(
                source=event,
                defaults={"recipient_id": event.recipient_id},
            )
            event.processed_at = timezone.now()
            event.save(update_fields=["processed_at"])
            delivered += 1
    return {"processed": delivered}
