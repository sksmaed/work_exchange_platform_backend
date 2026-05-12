from datetime import date, datetime
from typing import Any, ClassVar

from django.core.exceptions import ValidationError
from django.core.handlers.wsgi import WSGIRequest
from django.core.paginator import Paginator
from ninja import File, UploadedFile
from ninja_extra import api_controller, route
from ninja_extra.permissions import AllowAny, IsAuthenticated

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
    HelperListResponseSchema,
    HelperPhotoUploadResponseSchema,
    HelperProfileCreateSchema,
    HelperProfileResponseSchema,
    HelperProfileUpdateSchema,
)


@api_controller(prefix_or_class="helpers", tags=["helpers"], permissions=[IsAuthenticated])
class HelperControllerAPI:
    """API endpoints for managing helper profiles."""

    MAX_PAGE_SIZE: ClassVar[int] = 100
    ALLOWED_IMAGE_TYPES: ClassVar[set[str]] = {"image/jpeg", "image/png", "image/gif", "image/webp"}

    def _normalize_time_value(self, value: any) -> str:  # noqa: PLR0911
        """Return ISO date string when parseable, otherwise keep original text."""
        if isinstance(value, datetime):
            return value.date().isoformat()
        if isinstance(value, date):
            return value.isoformat()
        if isinstance(value, str):
            text = value.strip()
            if not text:
                return value
            try:
                return datetime.fromisoformat(text.replace("Z", "+00:00")).date().isoformat()
            except ValueError:
                try:
                    return date.fromisoformat(text).isoformat()
                except ValueError:
                    return value
        return str(value)

    def _normalize_expected_time_periods(self, periods: list[dict[str, Any]]) -> list[dict[str, str]]:
        """Normalize time period payload while preserving non-parseable strings."""
        normalized: list[dict[str, str]] = []
        for tp in periods:
            if not isinstance(tp, dict):
                continue
            normalized.append(
                {
                    "start_date": self._normalize_time_value(tp.get("start_date", "")),
                    "end_date": self._normalize_time_value(tp.get("end_date", "")),
                }
            )
        return normalized

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
            "name": helper.user.name,
            "phone": getattr(helper.user, "phone", ""),
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

    @route.get("/", response=HelperListResponseSchema, auth=None, permissions=[AllowAny])
    def list_helpers(self, request: WSGIRequest, page: int = 1, page_size: int = 20) -> HelperListResponseSchema:  # noqa: ARG002
        """List helpers with simple page/page_size pagination."""
        page_size = min(page_size, self.MAX_PAGE_SIZE)

        queryset = HelperModel.objects.select_related("user").prefetch_related("photos").order_by("-created_at")
        paginator = Paginator(queryset, page_size)
        page_obj = paginator.get_page(page)
        helpers = [self._helper_to_dict(helper) for helper in page_obj.object_list]

        return HelperListResponseSchema(
            helpers=helpers,
            total=paginator.count,
            page=page,
            page_size=page_size,
            has_next=page_obj.has_next(),
        )

    @route.get("/self/", response=HelperProfileResponseSchema)
    def get_self_profile(self, request: WSGIRequest) -> dict:
        """Retrieve the authenticated user's helper profile."""
        helper = self._get_self_helper(request)
        return self._helper_to_dict(helper)

    @route.patch("/self/", response=HelperProfileResponseSchema)
    def update_helper_profile(self, request: WSGIRequest, data: HelperProfileUpdateSchema) -> dict:
        """Update the authenticated user's helper profile."""
        user = request.user
        helper = self._get_self_helper(request)

        update_data = data.model_dump(exclude_unset=True)

        # Handle user-level fields (name, phone) separately
        user_fields = {}
        for field in ("name", "phone"):
            if field in update_data:
                user_fields[field] = update_data.pop(field)

        if user_fields:
            for field, value in user_fields.items():
                setattr(user, field, value)
            user.save(update_fields=list(user_fields.keys()))

        if "expected_time_periods" in update_data and update_data["expected_time_periods"] is not None:
            update_data["expected_time_periods"] = self._normalize_expected_time_periods(
                update_data["expected_time_periods"]
            )

        # gender column is NOT NULL in DB; coerce None to empty string
        if "gender" in update_data and update_data["gender"] is None:
            update_data["gender"] = ""

        if update_data:
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

    @route.get("/{helper_id}/", response=HelperProfileResponseSchema, auth=None, permissions=[AllowAny])
    def get_helper_profile(self, request: WSGIRequest, helper_id: str) -> dict:  # noqa: ARG002
        """Retrieve a helper profile by helper ID."""
        try:
            helper = HelperModel.objects.select_related("user").prefetch_related("photos").get(id=helper_id)
        except (HelperModel.DoesNotExist, ValidationError):
            raise KeyNotFoundException(HelperNotFoundError, helper_id)
        return self._helper_to_dict(helper)

    @route.post("/", response={201: HelperProfileResponseSchema})
    def create_helper_profile(self, request: WSGIRequest, data: HelperProfileCreateSchema) -> dict:
        """Create a new helper profile for the authenticated user."""
        user = request.user

        if HelperModel.objects.filter(user=user).exists():
            raise DuplicateKeyException(ValueError, "Helper profile already exists")

        time_periods = self._normalize_expected_time_periods(
            [tp.model_dump() for tp in (data.expected_time_periods or [])]
        )

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
