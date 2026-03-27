from dj_rest_auth.serializers import LoginSerializer as BaseLoginSerializer
from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework.exceptions import NotFound


class LoginSerializer(BaseLoginSerializer):
    """Email-only login with explicit 404 when user does not exist."""

    email = serializers.EmailField(required=True)

    def validate(self, attrs: dict) -> dict:
        """Validate that the email exists in the user model."""
        email = attrs.get("email")
        if email:
            user_model = get_user_model()
            if not user_model.objects.filter(email__iexact=email).exists():
                raise NotFound(detail="USER_NOT_FOUND")
        return super().validate(attrs)
