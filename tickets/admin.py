"""Django Admin entry points respecting the same ticket lifecycle as the API."""

from django import forms
from django.contrib import admin
from django.db import transaction

from tickets.audit import record_ticket_changes, ticket_audit_snapshot
from tickets.models import Ticket, TicketComment
from tickets.notifications import ticket_created, ticket_updated
from tickets.transitions import InvalidStatusTransition, validate_ticket_transition


class TicketAdminForm(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = "__all__"

    def clean(self):
        values = super().clean()
        requested_status = values.get("status")

        if requested_status is not None:
            if self.instance.pk:
                try:
                    validate_ticket_transition(self.instance.status, requested_status)
                except InvalidStatusTransition as exc:
                    self.add_error("status", str(exc))
            elif requested_status != Ticket.Status.OPEN:
                self.add_error("status", "Novos chamados devem começar abertos.")

        assignee = values.get("assignee")
        if assignee is not None and (not assignee.is_staff or not assignee.is_active):
            self.add_error("assignee", "O responsável deve pertencer à equipe ativa.")

        return values


class TicketCommentInline(admin.TabularInline):
    model = TicketComment
    extra = 0
    readonly_fields = ["author", "created_at"]


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    form = TicketAdminForm
    list_display = ["reference", "title", "status", "priority", "requester", "assignee", "created_at"]
    list_filter = ["status", "priority", "category", "created_at"]
    search_fields = ["title", "description", "requester__username", "requester__email"]
    readonly_fields = ["created_at", "updated_at"]
    inlines = [TicketCommentInline]

    def get_readonly_fields(self, request, obj=None):
        fields = list(super().get_readonly_fields(request, obj))
        if obj is not None:
            # Changing the owner would bypass the API's ownership guarantees.
            fields.append("requester")
        return fields

    @transaction.atomic
    def save_model(self, request, obj, form, change):
        previous = None
        if change:
            # Do not rely on the ModelForm's already modified model instance.
            current = Ticket.objects.select_for_update().get(pk=obj.pk)
            previous = ticket_audit_snapshot(current)
        super().save_model(request, obj, form, change)
        if change:
            events = record_ticket_changes(obj, request.user, previous)
            ticket_updated(obj, request.user, events)
        else:
            ticket_created(obj, request.user)


@admin.register(TicketComment)
class TicketCommentAdmin(admin.ModelAdmin):
    list_display = ["ticket", "author", "is_internal", "created_at"]
    list_filter = ["is_internal", "created_at"]
    search_fields = ["body", "ticket__title", "author__username"]
    readonly_fields = ["created_at"]
