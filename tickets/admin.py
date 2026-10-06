from django.contrib import admin

from tickets.models import Ticket, TicketComment


class TicketCommentInline(admin.TabularInline):
    model = TicketComment
    extra = 0
    readonly_fields = ["author", "created_at"]


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ["reference", "title", "status", "priority", "requester", "assignee", "created_at"]
    list_filter = ["status", "priority", "category", "created_at"]
    search_fields = ["title", "description", "requester__username", "requester__email"]
    readonly_fields = ["created_at", "updated_at"]
    inlines = [TicketCommentInline]


@admin.register(TicketComment)
class TicketCommentAdmin(admin.ModelAdmin):
    list_display = ["ticket", "author", "is_internal", "created_at"]
    list_filter = ["is_internal", "created_at"]
    search_fields = ["body", "ticket__title", "author__username"]
    readonly_fields = ["created_at"]
