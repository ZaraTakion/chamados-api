from django.contrib.auth import get_user_model
from rest_framework import serializers

from tickets.models import Ticket, TicketComment
from tickets.transitions import InvalidStatusTransition, validate_ticket_transition

User = get_user_model()


class TicketSerializer(serializers.ModelSerializer):
    reference = serializers.CharField(read_only=True)
    requester = serializers.StringRelatedField(read_only=True)
    assignee = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(is_staff=True, is_active=True), allow_null=True, required=False
    )

    class Meta:
        model = Ticket
        fields = [
            "id", "reference", "title", "description", "category", "status", "priority",
            "requester", "assignee", "created_at", "updated_at",
        ]
        read_only_fields = ["id", "reference", "requester", "created_at", "updated_at"]

    def validate(self, attrs):
        request = self.context["request"]
        is_staff = request.user.is_staff
        if not is_staff and "assignee" in attrs:
            raise serializers.ValidationError({"assignee": "Somente a equipe pode atribuir chamados."})
        if not is_staff and "status" in attrs:
            raise serializers.ValidationError({"status": "Somente a equipe pode alterar o status."})
        if self.instance and is_staff and "status" in attrs:
            try:
                validate_ticket_transition(self.instance.status, attrs["status"])
            except InvalidStatusTransition as exc:
                raise serializers.ValidationError({"status": str(exc)}) from exc
        return attrs


class TicketCommentSerializer(serializers.ModelSerializer):
    author = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = TicketComment
        fields = ["id", "ticket", "author", "body", "is_internal", "created_at"]
        read_only_fields = ["id", "ticket", "author", "created_at"]

    def validate(self, attrs):
        if attrs.get("is_internal", False) and not self.context["request"].user.is_staff:
            raise serializers.ValidationError({"is_internal": "Notas internas são restritas à equipe."})
        return attrs
