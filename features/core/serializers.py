from dj_rest_auth.registration.serializers import RegisterSerializer, SocialLoginSerializer
from dj_rest_auth.serializers import LoginSerializer as BaseLoginSerializer
from dj_rest_auth.serializers import UserDetailsSerializer
from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework.exceptions import NotFound

from features.core.models import User


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


class CustomUserDetailsSerializer(UserDetailsSerializer):
    """Adds user_type to the user object returned in login/registration responses."""

    user_type = serializers.CharField(read_only=True)
    # Google/social providers populate first_name/last_name via allauth; our API only
    # exposed `name`, so merge for display when `name` is blank (avoids clients falling back to email).
    name = serializers.SerializerMethodField()

    class Meta(UserDetailsSerializer.Meta):
        # Explicitly export only the fields we want the client to receive.
        # Remove Django's default first_name/last_name from the API output.
        fields = ("pk", "email", "name", "phone", "user_type")

    def get_name(self, obj: User) -> str:
        stored = (getattr(obj, "name", "") or "").strip()
        if stored:
            return stored
        combined = f"{obj.first_name or ''} {obj.last_name or ''}".strip()
        return combined


class CustomSocialLoginSerializer(SocialLoginSerializer):
    """Social login with optional user_type (first-time signup only; applied in SocialAccountAdapter)."""

    user_type = serializers.ChoiceField(
        choices=User.UserTypeChoices.choices,
        default=User.UserTypeChoices.HELPER,
        required=False,
    )

    def validate(self, attrs: dict) -> dict:
        req = self._get_request()
        setattr(req, "_social_signup_user_type", attrs.get("user_type", User.UserTypeChoices.HELPER))
        return super().validate(attrs)


class CustomRegisterSerializer(RegisterSerializer):
    """Extends the default registration serializer to accept user_type."""

    # username is auto-generated in AccountAdapter.save_user — not required from client
    username = serializers.CharField(required=False, allow_blank=True, default="")
    name = serializers.CharField(required=False, allow_blank=True, default="")
    phone = serializers.CharField(required=False, allow_blank=True, default="")

    def validate_username(self, value):
        # Skip allauth's username uniqueness check; adapter will generate a unique username
        return value

    def validate_email(self, email):
        email = super().validate_email(email)
        from features.core.models import User as UserModel
        if UserModel.objects.filter(email__iexact=email).exists():
            from rest_framework import serializers as drf_serializers
            raise drf_serializers.ValidationError("此 Email 已被註冊，請直接登入或使用其他 Email。")
        return email

    user_type = serializers.ChoiceField(
        choices=User.UserTypeChoices.choices,
        default=User.UserTypeChoices.HELPER,
    )

    def get_cleaned_data(self):
        data = super().get_cleaned_data()
        data["user_type"] = self.validated_data.get("user_type", User.UserTypeChoices.HELPER)
        data["name"] = self.validated_data.get("name", "")
        data["phone"] = self.validated_data.get("phone", "")
        return data

    def save(self, request):
        user = super().save(request)
        user.user_type = self.cleaned_data.get("user_type", User.UserTypeChoices.HELPER)
        # Save user_type, name and phone if provided
        user.name = self.cleaned_data.get("name", "")
        user.phone = self.cleaned_data.get("phone", "")
        user.save(update_fields=["user_type", "name", "phone"])
        return user
