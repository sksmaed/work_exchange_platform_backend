from typing import ClassVar

from django.core.handlers.wsgi import WSGIRequest
from ninja import File, UploadedFile
from ninja_extra import api_controller, route
from ninja_extra.permissions import IsAuthenticated

from common.exceptions import (
    DuplicateKeyException,
    ErrorCode,
    ErrorDetail,
    Http400BadRequestException,
    KeyNotFoundException,
)
from features.helper.exceptions import HelperNotFoundError
from features.helper.models import HelperModel, HelperPhoto
from features.helper.schemas import (
    HelperPhotoUploadResponseSchema,
    HelperProfileCreateSchema,
    HelperProfileResponseSchema,
    HelperProfileUpdateSchema,
)


@api_controller(prefix_or_class="helpers", tags=["helpers"], permissions=[IsAuthenticated])
class HelperControllerAPI:
    """API endpoints for managing helper profiles."""

    ALLOWED_IMAGE_TYPES: ClassVar[set[str]] = {"image/jpeg", "image/png", "image/gif", "image/webp"}

    def _get_self_helper(self, request: WSGIRequest) -> HelperModel:
        """Return current user's helper profile or raise 404."""
        helper = HelperModel.objects.filter(user=request.user).first()
        if not helper:
            raise KeyNotFoundException(HelperNotFoundError, str(request.user.id))
        return helper

    def _validate_image(self, file: UploadedFile) -> None:
        """Validate uploaded file type for helper images."""
        content_type = getattr(file, "content_type", "") or ""
        if content_type not in self.ALLOWED_IMAGE_TYPES:
            raise Http400BadRequestException(
                [
                    ErrorDetail(
                        ErrorCode("helper", "invalid_image"),
                        {"message": "Only JPEG, PNG, GIF, and WebP images are allowed"},
                    )
                ]
            )

    def _photo_to_dict(self, photo: HelperPhoto) -> dict:
        """Convert helper photo model to response payload."""
        return {
            "id": str(photo.id),
            "image_url": photo.image.url if photo.image else None,
            "order": photo.order,
            "created_at": photo.created_at,
        }

    def _helper_to_dict(self, helper: HelperModel) -> dict:
        """Build helper response payload with avatar and album photos."""
        photos = [self._photo_to_dict(photo) for photo in helper.photos.all()]
        return {
            "id": str(helper.id),
            "user_id": str(helper.user_id),
            "description": helper.description,
            "birthday": helper.birthday,
            "gender": helper.gender,
            "residence": helper.residence,
            "expected_place": helper.expected_place,
            "expected_time_periods": helper.expected_time_periods,
            "expected_treatments": helper.expected_treatments,
            "personality": helper.personality,
            "motivation": helper.motivation,
            "hobbies": helper.hobbies,
            "licenses": helper.licenses,
            "languages": helper.languages,
            "avg_rating": helper.avg_rating,
            "avatar_url": helper.user.avatar.url if helper.user.avatar else None,
            "photos": photos,
        }

    @route.get("/self/", response=HelperProfileResponseSchema)
    def get_self_profile(self, request: WSGIRequest) -> dict:
        """Retrieve the authenticated user's helper profile."""
        helper = self._get_self_helper(request)
        return self._helper_to_dict(helper)

    @route.post("/", response={201: HelperProfileResponseSchema})
    def create_helper_profile(self, request: WSGIRequest, data: HelperProfileCreateSchema) -> dict:
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
        return self._helper_to_dict(helper)

    @route.patch("/self/", response=HelperProfileResponseSchema)
    def update_helper_profile(self, request: WSGIRequest, data: HelperProfileUpdateSchema) -> dict:
        """Update the authenticated user's helper profile."""
        user = request.user
        helper = self._get_self_helper(request)

        update_data = data.model_dump(exclude_unset=True)

        if "expected_time_periods" in update_data and update_data["expected_time_periods"] is not None:
            update_data["expected_time_periods"] = [
                {"start_date": tp["start_date"].isoformat(), "end_date": tp["end_date"].isoformat()}
                for tp in update_data["expected_time_periods"]
            ]

        for field, value in update_data.items():
            setattr(helper, field, value)

        helper.save(user=user, update_fields=list(update_data.keys()))
        return self._helper_to_dict(helper)

    @route.post("/self/avatar", response=HelperProfileResponseSchema)
    def upload_avatar(self, request: WSGIRequest, image: UploadedFile = File(...)) -> dict:
        """Upload or replace helper avatar (authenticated helper only)."""
        helper = self._get_self_helper(request)
        self._validate_image(image)

        helper.user.avatar.save(image.name, image, save=True)
        return self._helper_to_dict(helper)

    @route.post("/self/photos", response={201: HelperPhotoUploadResponseSchema})
    def upload_helper_photos(
        self,
        request: WSGIRequest,
        images: list[UploadedFile] | None = File(default=None),
    ) -> dict:
        """Upload one or more photos to helper album."""
        helper = self._get_self_helper(request)
        images = images or []
        if not images:
            return {"image_urls": []}

        urls = []
        for file in images:
            self._validate_image(file)
            photo = HelperPhoto(helper=helper)
            photo.image.save(file.name, file, save=False)
            photo.save(user=request.user)
            urls.append(photo.image.url)

        return {"image_urls": urls}

    @route.delete("/self/photos/{photo_id}", response={200: dict})
    def delete_helper_photo(self, request: WSGIRequest, photo_id: str) -> dict:
        """Delete a helper album photo."""
        helper = self._get_self_helper(request)
        try:
            photo = HelperPhoto.objects.get(id=photo_id, helper=helper)
        except HelperPhoto.DoesNotExist:
            raise KeyNotFoundException(ErrorCode("helper", "photo_not_found"), photo_id)

        photo.image.delete(save=False)
        photo.delete()
        return {"detail": "Photo deleted successfully"}
