from common.exceptions import BaseAPIException


class ResumeNotFound(BaseAPIException):
    status_code = 404

    def __init__(self, message: str = "Resume not found") -> None:
        super().__init__(message) 