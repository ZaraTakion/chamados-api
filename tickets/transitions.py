"""Centralized business rules for ticket status transitions.

This module is independent of API serializers and views. Direct ORM updates do
not automatically apply these rules; API changes must call this validator.
"""

from tickets.models import Ticket


class InvalidStatusTransition(ValueError):
    """A requested ticket status change violates the lifecycle."""


ALLOWED_STATUS_TRANSITIONS = {
    Ticket.Status.OPEN: frozenset({Ticket.Status.IN_PROGRESS, Ticket.Status.CLOSED}),
    Ticket.Status.IN_PROGRESS: frozenset({
        Ticket.Status.WAITING, Ticket.Status.RESOLVED, Ticket.Status.CLOSED,
    }),
    Ticket.Status.WAITING: frozenset({
        Ticket.Status.IN_PROGRESS, Ticket.Status.RESOLVED, Ticket.Status.CLOSED,
    }),
    Ticket.Status.RESOLVED: frozenset({Ticket.Status.IN_PROGRESS, Ticket.Status.CLOSED}),
    Ticket.Status.CLOSED: frozenset(),
}


def validate_ticket_transition(current_status: str, requested_status: str) -> None:
    """Validate a status change; assigning the same status is a no-op."""
    if current_status not in ALLOWED_STATUS_TRANSITIONS:
        raise InvalidStatusTransition(f"Status atual desconhecido: {current_status}.")

    if requested_status == current_status:
        return

    if requested_status not in ALLOWED_STATUS_TRANSITIONS[current_status]:
        if current_status == Ticket.Status.CLOSED:
            raise InvalidStatusTransition("Um chamado fechado não pode ser reaberto.")
        raise InvalidStatusTransition(
            f"Transição de '{current_status}' para '{requested_status}' não permitida."
        )
