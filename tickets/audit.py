"""Application service for recording ticket changes atomically with updates."""

from tickets.models import TicketAuditEvent


AUDITED_FIELDS = ("status", "priority", "assignee")


def ticket_audit_snapshot(ticket):
    """Capture fields before the serializer saves changes."""
    return {
        "status": ticket.status,
        "priority": ticket.priority,
        "assignee": ticket.assignee_id,
    }


def record_ticket_changes(ticket, actor, previous):
    """Store only effective changes; caller must hold a transaction."""
    current = ticket_audit_snapshot(ticket)
    events = []
    for field in AUDITED_FIELDS:
        old_value = previous[field]
        new_value = current[field]
        if old_value == new_value:
            continue
        events.append(TicketAuditEvent(
            ticket=ticket,
            ticket_id_snapshot=ticket.pk,
            ticket_reference=ticket.reference,
            field=field,
            old_value="" if old_value is None else str(old_value),
            new_value="" if new_value is None else str(new_value),
            actor=actor,
            actor_username=actor.get_username(),
            actor_was_staff=actor.is_staff,
        ))
    if events:
        TicketAuditEvent.objects.bulk_create(events)
    return events
