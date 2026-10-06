from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email", "is_staff"]
        read_only_fields = fields


class RegisterSerializer(serializers.ModelSerializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, trim_whitespace=False, min_length=10)

    class Meta:
        model = User
        fields = ["id", "username", "email", "password"]
        read_only_fields = ["id"]
        extra_kwargs = {"username": {"min_length": 3, "max_length": 150}}

    def validate_email(self, value):
        email = value.strip().lower()
        if User.objects.filter(email__iexact=email).exists():
            raise serializers.ValidationError("Este e-mail já está cadastrado.")
        return email

    def validate_password(self, value):
        candidate = User(username=self.initial_data.get("username", ""), email=self.initial_data.get("email", ""))
        validate_password(value, user=candidate)
        return value

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)
