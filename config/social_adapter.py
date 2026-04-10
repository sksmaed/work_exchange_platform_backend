from allauth.socialaccount.adapter import DefaultSocialAccountAdapter

from features.core.models import User


class SocialAccountAdapter(DefaultSocialAccountAdapter):
    """Apply user_type from social signup request (CustomSocialLoginSerializer sets _social_signup_user_type)."""

    def populate_user(self, request, sociallogin, data):  # noqa: ANN001
        user = super().populate_user(request, sociallogin, data)
        if not sociallogin.is_existing:
            desired = getattr(request, "_social_signup_user_type", None)
            if desired in {c[0] for c in User.UserTypeChoices.choices}:
                user.user_type = desired
        # Persist a human-readable display name: allauth maps Google given/family name to
        # first_name/last_name only; core.User.name stays empty unless we copy it here.
        if not (getattr(user, "name", "") or "").strip():
            combined = f"{user.first_name or ''} {user.last_name or ''}".strip()
            if combined:
                user.name = combined[: User._meta.get_field("name").max_length]
        return user
