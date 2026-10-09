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


def _eligible_assignee_id(ticket):
    """Do not deliver new ticket notices to deactivated or former staff."""
    if not ticket.assignee_id:
        return None
    return (
        get_user_model().objects.filter(
            pk=ticket.assignee_id, is_staff=True, is_active=True
        ).values_list("pk", flat=True).first()
    )


def ticket_updated(ticket, actor, audit_events):
    for event in audit_events:
        if event.field == TicketAuditEvent.Field.ASSIGNEE:
            assignee_id = _eligible_assignee_id(ticket)
            if assignee_id and assignee_id != actor.pk:
                _create_events(ticket, NotificationOutbox.Kind.ASSIGNED, [assignee_id])
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
    recipients = {comment.ticket.requester_id, _eligible_assignee_id(comment.ticket)}
    recipients.discard(comment.author_id)
    _create_events(comment.ticket, NotificationOutbox.Kind.PUBLIC_COMMENT, recipients)
