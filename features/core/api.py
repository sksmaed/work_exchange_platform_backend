from allauth.socialaccount.providers.apple.views import AppleOAuth2Adapter
from allauth.socialaccount.providers.facebook.views import FacebookOAuth2Adapter
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from dj_rest_auth.registration.views import SocialLoginView
from django.core.handlers.wsgi import WSGIRequest
from django.http import JsonResponse
from ninja import Router
from ninja_extra import api_controller
from ninja_extra.controllers import ControllerBase
from ninja_extra.controllers.route import Route
from pydantic import BaseModel
from rest_framework.response import Response
from rest_framework.test import APIRequestFactory

# Note: Authentication is now handled by allauth.headless at /api/auth/
# This file includes social authentication endpoints and future business logic

router = Router()


class FacebookLoginRequestSchema(BaseModel):
    """Schema for Facebook login request."""

    access_token: str


class GoogleLoginRequestSchema(BaseModel):
    """Schema for Google login request."""

    access_token: str


class AppleLoginRequestSchema(BaseModel):
    """Schema for Apple login request."""

    id_token: str


class FacebookLoginView(SocialLoginView):
    """Facebook OAuth2 login view."""

    adapter_class = FacebookOAuth2Adapter


class GoogleLoginView(SocialLoginView):
    """Google OAuth2 login view."""

    adapter_class = GoogleOAuth2Adapter


class AppleLoginView(SocialLoginView):
    """Apple OAuth2 login view."""

    adapter_class = AppleOAuth2Adapter


@api_controller("/social-auth", tags=["Social Authentication"], auth=None)
class SocialAuthController(ControllerBase):
    """Social authentication controller for Google, Facebook, and Apple login."""

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
        request.user = getattr(incoming_request, "user", None)

        view = view_cls.as_view()
        return view(request)

    @Route.post("/facebook/", url_name="facebook_login")
    def facebook_login(self, request: WSGIRequest, data: FacebookLoginRequestSchema) -> JsonResponse:
        """Facebook OAuth2 Login.

        Exchange Facebook access token for JWT tokens.

        Args:
            request: The HTTP request object
            data: Facebook login data containing access_token

        Returns:
            JWT tokens and user information
        """
        try:
            response = self._call_social_login_view(request, FacebookLoginView, {"access_token": data.access_token})
            payload = response.data if isinstance(response.data, dict) else {"data": response.data}
            return JsonResponse(payload, status=response.status_code)
        except Exception as e:
            return JsonResponse(
                {
                    "error": "Facebook login error",
                    "exception_type": type(e).__name__,
                    "message": str(e) or repr(e),
                },
                status=500,
            )

    @Route.post("/google/", url_name="google_login")
    def google_login(self, request: WSGIRequest, data: GoogleLoginRequestSchema) -> JsonResponse:
        """Google OAuth2 Login.

        Exchange Google access token for JWT tokens.

        Args:
            request: The HTTP request object
            data: Google login data containing access_token

        Returns:
            JWT tokens and user information
        """
        try:
            response = self._call_social_login_view(request, GoogleLoginView, {"access_token": data.access_token})
            payload = response.data if isinstance(response.data, dict) else {"data": response.data}
            return JsonResponse(payload, status=response.status_code)
        except Exception as e:
            return JsonResponse(
                {
                    "error": "Google login error",
                    "exception_type": type(e).__name__,
                    "message": str(e) or repr(e),
                },
                status=500,
            )

    @Route.post("/apple/", url_name="apple_login")
    def apple_login(self, request: WSGIRequest, data: AppleLoginRequestSchema) -> JsonResponse:
        """Apple Sign In OAuth2 Login.

        Exchange Apple identity token (id_token) for JWT tokens.

        Args:
            request: The HTTP request object
            data: Apple login data containing id_token

        Returns:
            JWT tokens and user information
        """
        try:
            response = self._call_social_login_view(request, AppleLoginView, {"id_token": data.id_token})
            payload = response.data if isinstance(response.data, dict) else {"data": response.data}
            return JsonResponse(payload, status=response.status_code)
        except Exception as e:
            return JsonResponse(
                {
                    "error": "Apple login error",
                    "exception_type": type(e).__name__,
                    "message": str(e) or repr(e),
                },
                status=500,
            )
