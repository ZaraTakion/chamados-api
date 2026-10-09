import uuid

from django.conf import settings
from django.db import models


class Ticket(models.Model):
    class Status(models.TextChoices):
        OPEN = "open", "Aberto"
        IN_PROGRESS = "in_progress", "Em atendimento"
        WAITING = "waiting", "Aguardando solicitante"
        RESOLVED = "resolved", "Resolvido"
        CLOSED = "closed", "Fechado"

    class Priority(models.TextChoices):
        LOW = "low", "Baixa"
        NORMAL = "normal", "Normal"
        HIGH = "high", "Alta"
        URGENT = "urgent", "Urgente"

    title = models.CharField(max_length=180)
    description = models.TextField(max_length=10_000)
    category = models.CharField(max_length=80, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.OPEN, db_index=True)
    priority = models.CharField(max_length=10, choices=Priority.choices, default=Priority.NORMAL, db_index=True)
    requester = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="requested_tickets")
    assignee = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_tickets",
    )
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at", "-id"]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(status__in=["open", "in_progress", "waiting", "resolved", "closed"]),
                name="ticket_status_valid",
            ),
            models.CheckConstraint(
                condition=models.Q(priority__in=["low", "normal", "high", "urgent"]),
                name="ticket_priority_valid",
            ),
        ]

    def __str__(self):
        return f"CH-{self.pk:06d}: {self.title}"

    @property
    def reference(self):
        return f"CH-{self.pk:06d}" if self.pk else None


class TicketComment(models.Model):
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name="comments")
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="ticket_comments")
    body = models.TextField(max_length=5_000)
    is_internal = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ["created_at", "id"]

    def __str__(self):
        return f"Comentário em {self.ticket.reference} por {self.author}"


class TicketAuditEvent(models.Model):
    """Immutable snapshots of important updates made through the ticket API."""

    class Field(models.TextChoices):
        STATUS = "status", "Status"
        PRIORITY = "priority", "Prioridade"
        ASSIGNEE = "assignee", "Responsável"

    ticket = models.ForeignKey(
        Ticket,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="audit_events",
    )
    ticket_id_snapshot = models.PositiveBigIntegerField()
    ticket_reference = models.CharField(max_length=20)
    field = models.CharField(max_length=12, choices=Field.choices)
    old_value = models.CharField(max_length=150, blank=True)
    new_value = models.CharField(max_length=150, blank=True)
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="ticket_audit_events",
    )
    actor_username = models.CharField(max_length=150)
    actor_was_staff = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ["created_at", "id"]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(field__in=["status", "priority", "assignee"]),
                name="ticket_audit_field_valid",
            ),
        ]

    def __str__(self):
        return f"{self.ticket_reference}: {self.field} ({self.old_value} → {self.new_value})"


class NotificationOutbox(models.Model):
    """Committed notification intent; Celery will materialize an inbox item."""

    class Kind(models.TextChoices):
        CREATED = "ticket_created", "Chamado criado"
        ASSIGNED = "ticket_assigned", "Chamado atribuído"
        STATUS_CHANGED = "status_changed", "Status alterado"
        RESOLVED = "ticket_resolved", "Chamado resolvido"
        PUBLIC_COMMENT = "public_comment", "Comentário público"

    event_key = models.UUIDField(default=uuid.uuid4, editable=False)
    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="notification_outbox"
    )
    kind = models.CharField(max_length=24, choices=Kind.choices)
    ticket_reference = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["id"]
        constraints = [
            models.UniqueConstraint(
                fields=["event_key", "recipient"], name="unique_notification_event_recipient"
            ),
        ]


class TicketNotification(models.Model):
    """Private inbox entry; source is unique to make repeated processing safe."""

    source = models.OneToOneField(
        NotificationOutbox, on_delete=models.CASCADE, related_name="inbox_notification"
    )
    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="ticket_notifications"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at", "-id"]
