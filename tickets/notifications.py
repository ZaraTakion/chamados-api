"""Record private notification intents in the ticket transaction.

No Redis call takes place inside an HTTP request. Celery Beat later drains
committed outbox rows into recipients' private notification inboxes.
"""

import uuid

from django.contrib.auth import get_user_model

from tickets.models import NotificationOutbox, TicketAuditEvent


def _create_events(ticket, kind, recipient_ids):
    recipients = sorted({pk for pk in recipient_ids if pk is not None})
    if not recipients:
        return
    event_key = uuid.uuid4()
    NotificationOutbox.objects.bulk_create([
        NotificationOutbox(
            event_key=event_key,
            recipient_id=pk,
            kind=kind,
            ticket_reference=ticket.reference,
        )
        for pk in recipients
    ])


def ticket_created(ticket, actor):
    staff_ids = get_user_model().objects.filter(
        is_staff=True, is_active=True
    ).exclude(pk=actor.pk).values_list("pk", flat=True)
    _create_events(ticket, NotificationOutbox.Kind.CREATED, staff_ids)


def ticket_updated(ticket, actor, audit_events):
    for event in audit_events:
        if event.field == TicketAuditEvent.Field.ASSIGNEE:
            if ticket.assignee_id and ticket.assignee_id != actor.pk:
                _create_events(ticket, NotificationOutbox.Kind.ASSIGNED, [ticket.assignee_id])
        elif event.field == TicketAuditEvent.Field.STATUS and ticket.requester_id != actor.pk:
            kind = (
                NotificationOutbox.Kind.RESOLVED
                if ticket.status == "resolved"
                else NotificationOutbox.Kind.STATUS_CHANGED
            )
            _create_events(ticket, kind, [ticket.requester_id])


def public_comment_created(comment):
    if comment.is_internal:
        return
    recipients = {comment.ticket.requester_id, comment.ticket.assignee_id}
    recipients.discard(comment.author_id)
    _create_events(comment.ticket, NotificationOutbox.Kind.PUBLIC_COMMENT, recipients)
