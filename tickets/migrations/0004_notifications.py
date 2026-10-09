"""Durable notification intents and private inbox entries (CHM-502)."""

import uuid

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("tickets", "0003_database_integrity"),
    ]

    operations = [
        migrations.CreateModel(
            name="NotificationOutbox",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("event_key", models.UUIDField(default=uuid.uuid4, editable=False)),
                ("kind", models.CharField(choices=[
                    ("ticket_created", "Chamado criado"),
                    ("ticket_assigned", "Chamado atribuído"),
                    ("status_changed", "Status alterado"),
                    ("ticket_resolved", "Chamado resolvido"),
                    ("public_comment", "Comentário público"),
                ], max_length=24)),
                ("ticket_reference", models.CharField(max_length=20)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("processed_at", models.DateTimeField(blank=True, null=True)),
                ("recipient", models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name="notification_outbox",
                    to=settings.AUTH_USER_MODEL,
                )),
            ],
            options={
                "ordering": ["id"],
                "constraints": [
                    models.UniqueConstraint(
                        fields=("event_key", "recipient"),
                        name="unique_notification_event_recipient",
                    )
                ],
            },
        ),
        migrations.CreateModel(
            name="TicketNotification",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("recipient", models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name="ticket_notifications",
                    to=settings.AUTH_USER_MODEL,
                )),
                ("source", models.OneToOneField(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name="inbox_notification",
                    to="tickets.notificationoutbox",
                )),
            ],
            options={"ordering": ["-created_at", "-id"]},
        ),
    ]
