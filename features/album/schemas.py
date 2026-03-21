from datetime import datetime

from ninja import Schema


class AlbumPhotoResponseSchema(Schema):
    """Schema for a single album photo."""

    id: str
    image_url: str
    order: int
    created_at: datetime


class AlbumResponseSchema(Schema):
    """Schema for a host's full album (paginated)."""

    host_id: str
    photos: list[AlbumPhotoResponseSchema]
    total: int
    page: int
    page_size: int
    has_next: bool


class AlbumPhotoUploadResponseSchema(Schema):
    """Schema for the response after uploading photos."""

    image_urls: list[str]
