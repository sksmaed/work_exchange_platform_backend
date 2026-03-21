from typing import ClassVar

from django.db import models

from common.models import BaseModel
from utils.storage import get_model_file_path


class AlbumPhoto(BaseModel):
    """Represents a photo in a host's album.

    Each host has exactly one implicit album; the album is the collection of all
    AlbumPhoto records belonging to that host.

    Attributes:
    ----------
    host : ForeignKey
        The host who owns this photo.
    image : ImageField
        The uploaded image file.
    order : IntegerField
        Display order within the album (lower = earlier).
    """

    host = models.ForeignKey(
        "host.Host",
        on_delete=models.CASCADE,
        related_name="album_photos",
    )
    image = models.ImageField(upload_to=get_model_file_path)
    order = models.IntegerField(default=0)

    class Meta:
        ordering: ClassVar[list[str]] = ["order", "created_at"]
        indexes: ClassVar = [
            models.Index(fields=["host"]),
        ]

    def __str__(self) -> str:
        """String representation of AlbumPhoto."""
        return f"AlbumPhoto(host={self.host_id}, id={self.id})"
