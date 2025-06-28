from allauth.account.adapter import DefaultAccountAdapter
from allauth.account.utils import get_next_redirect_url
from django.conf import settings
from django.http import HttpRequest
from django.urls import reverse


class AccountAdapter(DefaultAccountAdapter):
    """Custom account adapter."""

    def get_login_redirect_url(self, request: HttpRequest) -> str:
        """Get the redirect URL after login.

        If a next parameter is provided, it will be used for redirection.
        If the user is staff, redirect to the admin index page.
        Otherwise, redirect to the frontend URL.
        """
        redirect_url = get_next_redirect_url(request)
        if redirect_url:
            return redirect_url

        if request.user.is_staff:
            return reverse("admin:index")
        return settings.FRONTEND_URL
