from django.core.handlers.wsgi import WSGIRequest
from django.http import JsonResponse
from ninja.openapi.docs import Redoc
from ninja_extra import NinjaExtraAPI

from common.exceptions import BaseAPIException

api = NinjaExtraAPI(
    title="Work Exchange Platform API",
    app_name="work_exchange_platform",
    docs=Redoc(),
    docs_url="docs/",
)


@api.exception_handler(BaseAPIException)
def base_exception_handler(request: WSGIRequest, exc: BaseAPIException):  # noqa: ARG001
    """Handle BaseAPIException and return a JSON response."""
    return JsonResponse(
        {"errors": exc.to_dict()},
        status=exc.status_code,
    )


@api.get("", tags=["health_check"])
def api_root_health_check(request: WSGIRequest):  # noqa: ARG001
    """Check api health."""
    return {"status": "healthy"}


@api.get("health_check/", tags=["health_check"])
def health_check(request: WSGIRequest):  # noqa: ARG001
    """Check api health."""
    return {"status": "healthy"}
