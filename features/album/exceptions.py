from common.exceptions import ErrorCode


class AlbumPhotoNotFoundError(ErrorCode):
    """Error code for album photo not found."""

    prefix = "album"
    name = "photo_not_found"


class AlbumInvalidImageError(ErrorCode):
    """Error code for invalid image type."""

    prefix = "album"
    name = "invalid_image_type"
