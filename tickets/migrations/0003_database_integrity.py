from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("tickets", "0002_ticketauditevent")]

    operations = [
        migrations.AddConstraint(
            model_name="ticket",
            constraint=models.CheckConstraint(
                condition=models.Q(("status__in", ["open", "in_progress", "waiting", "resolved", "closed"])),
                name="ticket_status_valid",
            ),
        ),
        migrations.AddConstraint(
            model_name="ticket",
            constraint=models.CheckConstraint(
                condition=models.Q(("priority__in", ["low", "normal", "high", "urgent"])),
                name="ticket_priority_valid",
            ),
        ),
        migrations.AddConstraint(
            model_name="ticketauditevent",
            constraint=models.CheckConstraint(
                condition=models.Q(("field__in", ["status", "priority", "assignee"])),
                name="ticket_audit_field_valid",
            ),
        ),
    ]
