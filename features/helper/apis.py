from django.core.handlers.wsgi import WSGIRequest
from ninja_extra import api_controller, route
from ninja_extra.permissions import IsAuthenticated

from common.exceptions import DuplicateKeyException, KeyNotFoundException
from features.helper.exceptions import HelperNotFoundError
from features.helper.models import HelperModel
from features.helper.schemas import HelperProfileCreateSchema, HelperProfileResponseSchema, HelperProfileUpdateSchema


@api_controller(prefix_or_class="helpers", tags=["helpers"], permissions=[IsAuthenticated])
class HelperControllerAPI:
    """API endpoints for managing helper profiles."""

    @route.get("/self/", response=HelperProfileResponseSchema)
    def get_self_profile(self, request: WSGIRequest) -> HelperModel:
        """Retrieve the authenticated user's helper profile."""
        user = request.user
        helper = HelperModel.objects.filter(user=user).first()
        if not helper:
            raise KeyNotFoundException(HelperNotFoundError, str(user.id))
        return helper

    @route.post("/", response={201: HelperProfileResponseSchema})
    def create_helper_profile(self, request: WSGIRequest, data: HelperProfileCreateSchema) -> HelperModel:
        """Create a new helper profile for the authenticated user."""
        user = request.user

        if HelperModel.objects.filter(user=user).exists():
            raise DuplicateKeyException(ValueError, "Helper profile already exists")

        time_periods = [
            {"start_date": tp.start_date.isoformat(), "end_date": tp.end_date.isoformat()}
            for tp in (data.expected_time_periods or [])
        ]

        helper = HelperModel(
            user=user,
            description=data.description,
            birthday=data.birthday,
            gender=data.gender,
            residence=data.residence or "",
            expected_place=data.expected_place or [],
            expected_time_periods=time_periods,
            expected_treatments=data.expected_treatments or [],
            personality=data.personality or "",
            motivation=data.motivation or "",
            hobbies=data.hobbies or "",
            licenses=data.licenses or HelperModel.LicenseChoices.NONE,
            languages=data.languages or [],
        )
        helper.save(user=user)
        return helper

    @route.patch("/self/", response=HelperProfileResponseSchema)
    def update_helper_profile(self, request: WSGIRequest, data: HelperProfileUpdateSchema) -> HelperModel:
        """Update the authenticated user's helper profile."""
        user = request.user

        helper = HelperModel.objects.filter(user=user).first()
        if not helper:
            raise KeyNotFoundException(HelperNotFoundError, str(user.id))

        update_data = data.model_dump(exclude_unset=True)

        if "expected_time_periods" in update_data and update_data["expected_time_periods"] is not None:
            update_data["expected_time_periods"] = [
                {"start_date": tp["start_date"].isoformat(), "end_date": tp["end_date"].isoformat()}
                for tp in update_data["expected_time_periods"]
            ]

        for field, value in update_data.items():
            setattr(helper, field, value)

        helper.save(user=user, update_fields=list(update_data.keys()))
        return helper
