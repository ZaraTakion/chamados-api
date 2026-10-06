from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = [migrations.swappable_dependency(settings.AUTH_USER_MODEL)]

    operations = [
        migrations.CreateModel(
            name="Ticket",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("title", models.CharField(max_length=180)),
                ("description", models.TextField(max_length=10000)),
                ("category", models.CharField(blank=True, max_length=80)),
                ("status", models.CharField(choices=[("open", "Aberto"), ("in_progress", "Em atendimento"), ("waiting", "Aguardando solicitante"), ("resolved", "Resolvido"), ("closed", "Fechado")], db_index=True, default="open", max_length=20)),
                ("priority", models.CharField(choices=[("low", "Baixa"), ("normal", "Normal"), ("high", "Alta"), ("urgent", "Urgente")], db_index=True, default="normal", max_length=10)),
                ("requester", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="requested_tickets", to=settings.AUTH_USER_MODEL)),
                ("assignee", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="assigned_tickets", to=settings.AUTH_USER_MODEL)),
                ("created_at", models.DateTimeField(auto_now_add=True, db_index=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={"ordering": ["-created_at", "-id"]},
        ),
        migrations.CreateModel(
            name="TicketComment",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("ticket", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="comments", to="tickets.ticket")),
                ("author", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="ticket_comments", to=settings.AUTH_USER_MODEL)),
                ("body", models.TextField(max_length=5000)),
                ("is_internal", models.BooleanField(default=False)),
                ("created_at", models.DateTimeField(auto_now_add=True, db_index=True)),
            ],
            options={"ordering": ["created_at", "id"]},
        ),
    ]
