from common.exceptions import BaseAPIException


class ResumeNotFound(BaseAPIException):
    """Exception raised when a requested resume is not found.

    Attributes:
    ----------
    status_code : int
        HTTP status code for the exception.
    """

    status_code = 404

    def __init__(self, message: str = "Resume not found") -> None:
        """Initialize the ResumeNotFound exception."""
        super().__init__(message)
