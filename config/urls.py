from allauth.account import app_settings as allauth_account_settings
from allauth.account.signals import user_signed_up
from dj_rest_auth.app_settings import api_settings
from dj_rest_auth.registration.views import RegisterView
from dj_rest_auth.utils import jwt_encode
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.shortcuts import redirect
from django.urls import include, path
from django.views import defaults as default_views

from config.api import api


class FixedRegisterView(RegisterView):
    """JWT-only registration: skips allauth session login to avoid redirect errors."""

    def perform_create(self, serializer):
        user = serializer.save(self.request)
        if allauth_account_settings.EMAIL_VERIFICATION != allauth_account_settings.EmailVerificationMethod.MANDATORY:
            if api_settings.USE_JWT:
                self.access_token, self.refresh_token = jwt_encode(user)
        user_signed_up.send(sender=user.__class__, request=self.request._request, user=user)
        return user


urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("allauth.urls")),
    path("api/auth/", include("dj_rest_auth.urls")),
    path("api/auth/registration/", FixedRegisterView.as_view(), name="rest_register"),
    path("api/", api.urls),
    path("", lambda request: redirect("admin/")),  # noqa: ARG005
]

if settings.DEBUG:
    # This allows the error pages to be debugged during development, just visit
    # these url in browser to see how these error pages look like.
    urlpatterns += staticfiles_urlpatterns()
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += [
        path("400/", default_views.bad_request, kwargs={"exception": Exception("Bad Request!")}),
        path("403/", default_views.permission_denied, kwargs={"exception": Exception("Permission Denied")}),
        path("404/", default_views.page_not_found, kwargs={"exception": Exception("Page not Found")}),
        path("500/", default_views.server_error),
    ]
    if "debug_toolbar" in settings.INSTALLED_APPS:
        import debug_toolbar

        urlpatterns += [path("__debug__/", include(debug_toolbar.urls))]
