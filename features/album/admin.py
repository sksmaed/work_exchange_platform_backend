from typing import ClassVar

from django.contrib import admin

from features.album.models import AlbumPhoto


@admin.register(AlbumPhoto)
class AlbumPhotoAdmin(admin.ModelAdmin):
    """Admin configuration for AlbumPhoto."""

    list_display: ClassVar = ["id", "host", "order", "created_at"]
    list_filter: ClassVar = ["host"]
    ordering: ClassVar = ["host", "order", "created_at"]
    search_fields: ClassVar = ["host__name"]
