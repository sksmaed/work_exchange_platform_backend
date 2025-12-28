from typing import Any

from allauth.socialaccount.providers.facebook.views import FacebookOAuth2Adapter
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from dj_rest_auth.registration.views import SocialLoginView
from django.core.handlers.wsgi import WSGIRequest
from django.http import HttpRequest
from ninja import Router
from ninja_extra import api_controller
from ninja_extra.controllers import ControllerBase
from ninja_extra.controllers.route import Route
from pydantic import BaseModel

# Note: Authentication is now handled by allauth.headless at /api/auth/
# This file includes social authentication endpoints and future business logic

router = Router()

# HTTP status code constants
HTTP_OK = 200


class FacebookLoginRequestSchema(BaseModel):
    """Schema for Facebook login request."""

    access_token: str


class GoogleLoginRequestSchema(BaseModel):
    """Schema for Google login request."""

    access_token: str


class FacebookLoginView(SocialLoginView):
    """Facebook OAuth2 login view."""

    adapter_class = FacebookOAuth2Adapter


class GoogleLoginView(SocialLoginView):
    """Google OAuth2 login view."""

    adapter_class = GoogleOAuth2Adapter


@api_controller("/social-auth", tags=["Social Authentication"])
class SocialAuthController(ControllerBase):
    """Social authentication controller for Facebook and Google login."""

    @Route.post("/facebook/", url_name="facebook_login")
    def facebook_login(self, request: WSGIRequest, data: FacebookLoginRequestSchema) -> dict[str, Any]:
        """Facebook OAuth2 Login.

        Exchange Facebook access token for JWT tokens.

        Args:
            request: The HTTP request object
            data: Facebook login data containing access_token

        Returns:
            JWT tokens and user information
        """
        try:
            view = FacebookLoginView()
            view.request = request

            # Create a mock request with the access token data
            mock_request = HttpRequest()
            mock_request.method = "POST"
            mock_request.POST = {"access_token": data.access_token}

            response = view.post(mock_request)

            if response.status_code == HTTP_OK:
                return response.data
        except Exception as e:
            return {"error": "Facebook login error", "message": str(e)}
        else:
            return {"error": "Facebook login failed", "details": response.data}

    @Route.post("/google/", url_name="google_login")
    def google_login(self, request: WSGIRequest, data: GoogleLoginRequestSchema) -> dict[str, Any]:
        """Google OAuth2 Login.

        Exchange Google access token for JWT tokens.

        Args:
            request: The HTTP request object
            data: Google login data containing access_token

        Returns:
            JWT tokens and user information
        """
        try:
            view = GoogleLoginView()
            view.request = request

            # Create a mock request with the access token data
            mock_request = HttpRequest()
            mock_request.method = "POST"
            mock_request.POST = {"access_token": data.access_token}

            response = view.post(mock_request)

            if response.status_code == HTTP_OK:
                return response.data
        except Exception as e:
            return {"error": "Google login error", "message": str(e)}
        else:
            return {"error": "Google login failed", "details": response.data}
