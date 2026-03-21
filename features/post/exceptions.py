from common.exceptions import BaseAPIException, ErrorCode


class PostNotFoundError(BaseAPIException):
    """Exception raised when a post is not found."""

    def __init__(self) -> None:
        """Initialize the exception."""
        super().__init__(error_code=ErrorCode.NOT_FOUND_ERROR, message="貼文不存在")


class CommentNotFoundError(BaseAPIException):
    """Exception raised when a comment is not found."""

    def __init__(self) -> None:
        """Initialize the exception."""
        super().__init__(error_code=ErrorCode.NOT_FOUND_ERROR, message="留言不存在")


class PostInvalidImageError(BaseAPIException):
    """Exception raised when an invalid image is uploaded."""

    def __init__(self, detail_msg: str) -> None:
        """Initialize the exception."""
        super().__init__(
            error_code=ErrorCode.VALIDATION_ERROR,
            message=detail_msg,
            details={"image": detail_msg},
        )
