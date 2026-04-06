import uuid

from allauth.account.adapter import DefaultAccountAdapter
from allauth.account.utils import get_next_redirect_url
from django.conf import settings
from django.http import HttpRequest
from django.urls import reverse


class AccountAdapter(DefaultAccountAdapter):
    """Custom account adapter."""

    def get_login_redirect_url(self, request: HttpRequest) -> str:
        """Get the redirect URL after login."""
        redirect_url = get_next_redirect_url(request)
        if redirect_url:
            return redirect_url

        if request.user.is_staff:
            return reverse("admin:index")
        return settings.FRONTEND_URL

    def save_user(self, request: HttpRequest, user, form, commit: bool = True):
        """Auto-populate username from email to satisfy the unique constraint."""
        user = super().save_user(request, user, form, commit=False)
        if not user.username:
            base = user.email.split("@")[0][:100]
            user.username = f"{base}_{uuid.uuid4().hex[:8]}"
        if commit:
            user.save()
        return user
