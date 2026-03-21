from django.core.handlers.wsgi import WSGIRequest
from django.http import JsonResponse
from ninja.openapi.docs import Redoc
from ninja_extra import NinjaExtraAPI

from common.exceptions import BaseAPIException
from features.album.apis import AlbumControllerAPI
from features.application.apis import ApplicationControllerAPI
from features.calendar.apis import CalendarControllerAPI
from features.chat.apis import ChatControllerAPI
from features.core.api import SocialAuthController
from features.forum.apis import ForumControllerAPI
from features.helper.apis import HelperControllerAPI
from features.helper.resume.apis import HelperResumeAPI
from features.host.apis import HostControllerAPI, VacancyControllerAPI
from features.post.apis import HostPostControllerAPI, PostActionControllerAPI

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


api.register_controllers(HelperResumeAPI)
api.register_controllers(SocialAuthController)
api.register_controllers(HostControllerAPI)
api.register_controllers(ChatControllerAPI)
api.register_controllers(ForumControllerAPI)
api.register_controllers(HelperControllerAPI)
api.register_controllers(ApplicationControllerAPI)
api.register_controllers(VacancyControllerAPI)
api.register_controllers(CalendarControllerAPI)
api.register_controllers(AlbumControllerAPI)
api.register_controllers(HostPostControllerAPI)
api.register_controllers(PostActionControllerAPI)
