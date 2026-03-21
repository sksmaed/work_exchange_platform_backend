from typing import ClassVar

from django.core.handlers.wsgi import WSGIRequest
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404
from ninja import File, UploadedFile
from ninja_extra import api_controller, route
from ninja_extra.permissions import IsAuthenticated

from common.exceptions import (
    ErrorDetail,
    Http400BadRequestException,
    Http403ForbiddenException,
    KeyNotFoundException,
)
from features.album.exceptions import AlbumInvalidImageError, AlbumPhotoNotFoundError
from features.album.models import AlbumPhoto
from features.album.schemas import (
    AlbumPhotoUploadResponseSchema,
    AlbumResponseSchema,
)
from features.host.models import Host


@api_controller(prefix_or_class="hosts", tags=["album"])
class AlbumControllerAPI:
    """API endpoints for host album photo management."""

    ALLOWED_IMAGE_TYPES: ClassVar[set[str]] = {"image/jpeg", "image/png", "image/gif", "image/webp"}
    MAX_PAGE_SIZE: ClassVar[int] = 100

    def _get_host(self, host_id: str) -> Host:
        """Retrieve a host by ID or raise 404."""
        return get_object_or_404(Host, id=host_id)

    def _assert_host_owner(self, host: Host, request: WSGIRequest) -> None:
        """Raise 403 if the authenticated user is not the host owner."""
        if host.user_id != request.user.id:
            raise Http403ForbiddenException("Only the host owner can manage album photos")

    def _validate_image(self, file: UploadedFile) -> None:
        """Validate that the uploaded file is an allowed image type."""
        content_type = getattr(file, "content_type", "") or ""
        if content_type not in self.ALLOWED_IMAGE_TYPES:
            raise Http400BadRequestException(
                [ErrorDetail(AlbumInvalidImageError, {"message": "Only JPEG, PNG, GIF, and WebP images are allowed"})]
            )

    def _photo_to_dict(self, photo: AlbumPhoto) -> dict:
        """Convert an AlbumPhoto to a response dict."""
        return {
            "id": str(photo.id),
            "image_url": photo.image.url if photo.image else None,
            "order": photo.order,
            "created_at": photo.created_at,
        }

    @route.get("/{host_id}/album", response={200: AlbumResponseSchema})
    def get_album(
        self,
        request: WSGIRequest,  # noqa: ARG002
        host_id: str,
        page: int = 1,
        page_size: int = 20,
    ) -> dict:
        """Get all photos in a host's album (public).

        Returns a paginated list of photos belonging to the given host.
        """
        host = self._get_host(host_id)
        page_size = min(page_size, self.MAX_PAGE_SIZE)

        queryset = AlbumPhoto.objects.filter(host=host)
        paginator = Paginator(queryset, page_size)
        page_obj = paginator.get_page(page)

        return {
            "host_id": str(host.id),
            "photos": [self._photo_to_dict(p) for p in page_obj.object_list],
            "total": paginator.count,
            "page": page,
            "page_size": page_size,
            "has_next": page_obj.has_next(),
        }

    @route.post(
        "/{host_id}/album/photos",
        response={201: AlbumPhotoUploadResponseSchema},
        permissions=[IsAuthenticated],
    )
    def upload_photos(
        self,
        request: WSGIRequest,
        host_id: str,
        images: list[UploadedFile] | None = File(default=None),
    ) -> dict:
        """Upload one or more photos to the host's album (host owner only)."""
        host = self._get_host(host_id)
        self._assert_host_owner(host, request)

        images = images or []
        if not images:
            return {"image_urls": []}

        urls = []
        for file in images:
            self._validate_image(file)
            photo = AlbumPhoto(host=host)
            photo.image.save(file.name, file, save=False)
            photo.save(user=request.user)
            urls.append(photo.image.url)

        return {"image_urls": urls}

    @route.delete(
        "/{host_id}/album/photos/{photo_id}",
        response={200: dict},
        permissions=[IsAuthenticated],
    )
    def delete_photo(
        self,
        request: WSGIRequest,
        host_id: str,
        photo_id: str,
    ) -> dict:
        """Delete a specific photo from the host's album (host owner only)."""
        host = self._get_host(host_id)
        self._assert_host_owner(host, request)

        try:
            photo = AlbumPhoto.objects.get(id=photo_id, host=host)
        except AlbumPhoto.DoesNotExist:
            raise KeyNotFoundException(AlbumPhotoNotFoundError, photo_id)

        photo.image.delete(save=False)
        photo.delete()
        return {"detail": "Photo deleted successfully"}
