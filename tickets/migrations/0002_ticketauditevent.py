from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("tickets", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="TicketAuditEvent",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("ticket_id_snapshot", models.PositiveBigIntegerField()),
                ("ticket_reference", models.CharField(max_length=20)),
                ("field", models.CharField(
                    choices=[("status", "Status"), ("priority", "Prioridade"), ("assignee", "Responsável")],
                    max_length=12,
                )),
                ("old_value", models.CharField(blank=True, max_length=150)),
                ("new_value", models.CharField(blank=True, max_length=150)),
                ("actor_username", models.CharField(max_length=150)),
                ("actor_was_staff", models.BooleanField(default=False)),
                ("created_at", models.DateTimeField(auto_now_add=True, db_index=True)),
                ("actor", models.ForeignKey(
                    blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL,
                    related_name="ticket_audit_events", to=settings.AUTH_USER_MODEL,
                )),
                ("ticket", models.ForeignKey(
                    blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL,
                    related_name="audit_events", to="tickets.ticket",
                )),
            ],
            options={"ordering": ["created_at", "id"]},
        ),
    ]
