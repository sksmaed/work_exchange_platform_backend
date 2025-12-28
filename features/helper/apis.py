from django.core.handlers.wsgi import WSGIRequest
from django.db.models import Q, QuerySet
from ninja_extra import api_controller, route
from ninja_extra.ordering import Ordering, ordering
from ninja_extra.pagination import PageNumberPagination, paginate
from ninja_extra.permissions import IsAuthenticated
from ninja_extra.schemas import NinjaPaginationResponseSchema
from ninja_extra.searching import Searching, searching

from common.exceptions import Http403ForbiddenException, KeyNotFoundException
from features.helper.exceptions import HelperAlreadyExistsError, HelperNotFoundError
from features.helper.models import HelperModel
from features.helper.schemas import HelperCreateSchema, HelperResponseSchema, HelperUpdateSchema


@api_controller(prefix_or_class="helpers", tags=["helpers"])
class HelperControllerAPI:
    """API endpoints for managing helper profiles."""

    @route.get("", response={200: NinjaPaginationResponseSchema[HelperResponseSchema]})
    @paginate(PageNumberPagination)
    @searching(Searching, search_fields=["description", "residence", "personality", "motivation"])
    @ordering(Ordering, ordering_fields=["created_at", "avg_rating"])
    def list_helpers(
        self,
        request: WSGIRequest,
        residence: str | None = None,
        gender: str | None = None,
        licenses: str | None = None,
        min_rating: float | None = None,
    ) -> QuerySet[HelperModel]:
        """Retrieve a list of helpers with optional filtering."""
        filters = Q()

        # Apply filters
        if residence:
            filters &= Q(residence__icontains=residence)
        if gender:
            filters &= Q(gender=gender)
        if licenses:
            filters &= Q(licenses=licenses)
        if min_rating is not None:
            filters &= Q(avg_rating__gte=min_rating)

        return HelperModel.objects.filter(filters).select_related("user")

    @route.get("/self/", response={200: HelperResponseSchema})
    def get_self_profile(self, request: WSGIRequest) -> HelperModel:
        """Retrieve the authenticated user's helper profile."""
        user = request.user
        try:
            helper = HelperModel.objects.select_related("user").get(user=user)
            return helper
        except HelperModel.DoesNotExist:
            raise KeyNotFoundException(HelperNotFoundError, str(user.id))

    @route.get("/{helper_id}", response={200: HelperResponseSchema})
    def get_helper(self, request: WSGIRequest, helper_id: str) -> HelperModel:  # noqa: ARG002
        """Retrieve a specific helper profile by ID."""
        try:
            helper = HelperModel.objects.select_related("user").get(id=helper_id)
            return helper
        except HelperModel.DoesNotExist:
            raise KeyNotFoundException(HelperNotFoundError, helper_id)

    @route.post("", response={201: HelperResponseSchema}, permissions=[IsAuthenticated])
    def create_helper(self, request: WSGIRequest, data: HelperCreateSchema) -> HelperModel:
        """Create a new helper profile for the authenticated user."""
        user = request.user

        # Check if user already has a helper profile
        if HelperModel.objects.filter(user=user).exists():
            raise KeyNotFoundException(HelperAlreadyExistsError, str(user.id))

        helper = HelperModel(
            user=user,
            description=data.description,
            birthday=data.birthday,
            gender=data.gender,
            residence=data.residence or "",
            expected_place=data.expected_place or [],
            expected_time_periods=data.expected_time_periods or [],
            expected_treatments=data.expected_treatments or [],
            personality=data.personality or "",
            motivation=data.motivation or "",
            work_experience=data.work_experience or "",
            hobbies=data.hobbies or "",
            licenses=data.licenses or "None",
            languages=data.languages or [],
        )
        helper.save(user=user)
        return helper

    @route.patch("/{helper_id}", response={200: HelperResponseSchema}, permissions=[IsAuthenticated])
    def update_helper(self, request: WSGIRequest, helper_id: str, data: HelperUpdateSchema) -> HelperModel:
        """Update an existing helper profile."""
        user = request.user

        try:
            helper = HelperModel.objects.get(id=helper_id)
        except HelperModel.DoesNotExist:
            raise KeyNotFoundException(HelperNotFoundError, helper_id)

        # Only allow users to update their own profile
        if helper.user != user:
            raise Http403ForbiddenException("You do not have permission to update this helper profile")

        # Update fields
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(helper, field, value)

        helper.save(user=user, update_fields=list(update_data.keys()))
        return helper

    @route.patch("/self/", response={200: HelperResponseSchema}, permissions=[IsAuthenticated])
    def update_self_profile(self, request: WSGIRequest, data: HelperUpdateSchema) -> HelperModel:
        """Update the authenticated user's helper profile."""
        user = request.user

        try:
            helper = HelperModel.objects.get(user=user)
        except HelperModel.DoesNotExist:
            raise KeyNotFoundException(HelperNotFoundError, str(user.id))

        # Update fields
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(helper, field, value)

        helper.save(user=user, update_fields=list(update_data.keys()))
        return helper

    @route.delete("/{helper_id}", permissions=[IsAuthenticated])
    def delete_helper(self, request: WSGIRequest, helper_id: str) -> dict:
        """Delete a helper profile."""
        user = request.user

        helper = HelperModel.objects.filter(id=helper_id).first()
        if not helper:
            raise KeyNotFoundException(HelperNotFoundError, helper_id)

        # Only allow users to delete their own profile
        if helper.user != user:
            raise Http403ForbiddenException("You do not have permission to delete this helper profile")

        helper.delete()
        return {"detail": "Helper profile deleted successfully"}

