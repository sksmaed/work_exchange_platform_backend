from importlib import import_module
from typing import Any, ClassVar, Literal

import requests
from allauth.socialaccount.providers.apple.views import AppleOAuth2Adapter
from allauth.socialaccount.providers.facebook.views import FacebookOAuth2Adapter
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from dj_rest_auth.registration.views import SocialLoginView
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.messages.storage.fallback import FallbackStorage
from django.core.handlers.wsgi import WSGIRequest
from ninja import Router
from ninja_extra import api_controller
from ninja_extra.controllers import ControllerBase
from ninja_extra.controllers.route import Route
from pydantic import BaseModel
from rest_framework.response import Response
from rest_framework.test import APIRequestFactory

from features.core.serializers import CustomSocialLoginSerializer

# Note: Authentication is now handled by allauth.headless at /api/auth/
# This file includes social authentication endpoints and future business logic

router = Router()


class FacebookLoginRequestSchema(BaseModel):
    """Schema for Facebook login request."""

    access_token: str
    user_type: Literal["helper", "host", "both"] = "helper"


class GoogleLoginRequestSchema(BaseModel):
    """Schema for Google login request."""

    access_token: str
    user_type: Literal["helper", "host", "both"] = "helper"


class GoogleLookupRequestSchema(BaseModel):
    """Validate Google access token and check whether the email is already registered."""

    access_token: str


class AppleLoginRequestSchema(BaseModel):
    """Schema for Apple login request."""

    id_token: str
    user_type: Literal["helper", "host", "both"] = "helper"


class FacebookLoginView(SocialLoginView):
    """Facebook OAuth2 login view."""

    adapter_class = FacebookOAuth2Adapter
    serializer_class = CustomSocialLoginSerializer


class GoogleLoginView(SocialLoginView):
    """Google OAuth2 login view."""

    adapter_class = GoogleOAuth2Adapter
    serializer_class = CustomSocialLoginSerializer


class AppleLoginView(SocialLoginView):
    """Apple OAuth2 login view."""

    adapter_class = AppleOAuth2Adapter
    serializer_class = CustomSocialLoginSerializer


@api_controller("/social-auth", tags=["Social Authentication"], auth=None)
class SocialAuthController(ControllerBase):
    """Social authentication controller for Google, Facebook, and Apple login."""

    STATUS_OK: ClassVar[int] = 200
    STATUS_BAD_REQUEST: ClassVar[int] = 400
    STATUS_UNAUTHORIZED: ClassVar[int] = 401
    STATUS_INTERNAL_ERROR: ClassVar[int] = 500
    allowed_status_codes: ClassVar[set[int]] = {STATUS_OK, STATUS_BAD_REQUEST, STATUS_UNAUTHORIZED}

    def _call_social_login_view(
        self,
        incoming_request: WSGIRequest,
        view_cls: type[SocialLoginView],
        payload: dict[str, str],
    ) -> Response:
        """Call a dj-rest-auth social login view with a DRF-compatible request."""
        factory = APIRequestFactory()
        request = factory.post(
            incoming_request.path,
            payload,
            format="json",
            HTTP_HOST=incoming_request.get_host(),
        )

        request.META["wsgi.url_scheme"] = incoming_request.scheme
        if "HTTP_X_FORWARDED_PROTO" in incoming_request.META:
            request.META["HTTP_X_FORWARDED_PROTO"] = incoming_request.META["HTTP_X_FORWARDED_PROTO"]

        if hasattr(incoming_request, "session"):
            request.session = incoming_request.session
        else:
            session_engine = import_module(settings.SESSION_ENGINE)
            request.session = session_engine.SessionStore()

        # allauth may use django messages framework during login flow.
        # APIRequestFactory request does not include message storage by default.
        setattr(request, "_messages", FallbackStorage(request))

        request.user = getattr(incoming_request, "user", None)

        view = view_cls.as_view()
        return view(request)

    def _build_api_response(self, response: Response) -> tuple[int, dict[str, Any]]:
        """Normalize DRF response payload for Ninja and keep known status codes."""
        payload = response.data if isinstance(response.data, dict) else {"data": response.data}
        status_code = (
            response.status_code if response.status_code in self.allowed_status_codes else self.STATUS_INTERNAL_ERROR
        )
        if status_code == self.STATUS_INTERNAL_ERROR:
            payload = {
                "error": "Social login upstream error",
                "upstream_status": response.status_code,
                "details": payload,
            }
        return status_code, payload

    @Route.post("/facebook/", url_name="facebook_login", response={200: dict, 400: dict, 401: dict, 500: dict})
    def facebook_login(self, request: WSGIRequest, data: FacebookLoginRequestSchema) -> tuple[int, dict[str, Any]]:
        """Facebook OAuth2 Login.

        Exchange Facebook access token for JWT tokens.

        Args:
            request: The HTTP request object
            data: Facebook login data containing access_token

        Returns:
            JWT tokens and user information
        """
        try:
            response = self._call_social_login_view(
                request,
                FacebookLoginView,
                {"access_token": data.access_token, "user_type": data.user_type},
            )
            return self._build_api_response(response)
        except Exception as e:
            return self.STATUS_INTERNAL_ERROR, {
                "error": "Facebook login error",
                "exception_type": type(e).__name__,
                "message": str(e) or repr(e),
            }

    @Route.post("/google/lookup/", url_name="google_lookup", response={200: dict})
    def google_lookup(self, _request: WSGIRequest, data: GoogleLookupRequestSchema) -> dict[str, Any]:
        """Check if the Google account email already has a local user (no user is created)."""
        try:
            resp = requests.get(
                "https://www.googleapis.com/oauth2/v3/userinfo",
                headers={"Authorization": f"Bearer {data.access_token}"},
                timeout=10,
            )
            if resp.status_code != self.STATUS_OK:
                return {"error": "invalid_token", "message": "無法驗證 Google 帳號"}
            info = resp.json()
            email = info.get("email")
            if not email:
                return {"error": "no_email", "message": "無法取得 Google 信箱"}
            user_model = get_user_model()
            exists = user_model.objects.filter(email__iexact=email).exists()
        except Exception as e:
            return {"error": "google_lookup_error", "message": str(e)}
        else:
            return {"exists": exists, "email": email}

    @Route.post("/google/", url_name="google_login", response={200: dict, 400: dict, 401: dict, 500: dict})
    def google_login(self, request: WSGIRequest, data: GoogleLoginRequestSchema) -> tuple[int, dict[str, Any]]:
        """Google OAuth2 Login.

        Exchange Google access token for JWT tokens.

        Args:
            request: The HTTP request object
            data: Google login data containing access_token

        Returns:
            JWT tokens and user information
        """
        try:
            response = self._call_social_login_view(
                request,
                GoogleLoginView,
                {"access_token": data.access_token, "user_type": data.user_type},
            )
            return self._build_api_response(response)
        except Exception as e:
            return self.STATUS_INTERNAL_ERROR, {
                "error": "Google login error",
                "exception_type": type(e).__name__,
                "message": str(e) or repr(e),
            }

    @Route.post("/apple/", url_name="apple_login", response={200: dict, 400: dict, 401: dict, 500: dict})
    def apple_login(self, request: WSGIRequest, data: AppleLoginRequestSchema) -> tuple[int, dict[str, Any]]:
        """Apple Sign In OAuth2 Login.

        Exchange Apple identity token (id_token) for JWT tokens.

        Args:
            request: The HTTP request object
            data: Apple login data containing id_token

        Returns:
            JWT tokens and user information
        """
        try:
            response = self._call_social_login_view(
                request,
                AppleLoginView,
                {"id_token": data.id_token, "user_type": data.user_type},
            )
            return self._build_api_response(response)
        except Exception as e:
            return self.STATUS_INTERNAL_ERROR, {
                "error": "Apple login error",
                "exception_type": type(e).__name__,
                "message": str(e) or repr(e),
            }
