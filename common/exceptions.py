from typing import ClassVar

from ninja_extra import status
from ninja_extra.exceptions import APIException


class ErrorMeta(type):
    """Metaclass for error codes."""

    def __str__(cls) -> str:
        """Return a string representation of the error code."""
        if hasattr(cls, "prefix") and hasattr(cls, "name"):
            return f"{cls.prefix}:{cls.name}"
        return super().__str__()


class ErrorCode(metaclass=ErrorMeta):
    """Class representing an error code with a prefix and name."""

    def __init__(self, prefix: str, name: str) -> None:
        """Initialize the ErrorCode instance.

        :param prefix: The prefix of the error code.
        :param name: The name of the error code.
        """
        self.prefix = prefix
        self.name = name

    def __repr__(self) -> str:
        """Return a string representation of the error code."""
        return f"{self.prefix}:{self.name}"

    def __dict__(self) -> dict:
        """Return a dictionary representation of the error code."""
        return {"prefix": self.prefix, "name": self.name}


class ErrorDetail:
    """Class representing an error detail with an error code and extra data."""

    error_code = ErrorCode("common", "error")
    extra_data: dict

    def __init__(self, error_code: ErrorCode, extra_data: dict) -> None:
        """Initialize the ErrorDetail instance."""
        self.error_code = error_code
        self.extra_data = extra_data

    def __str__(self) -> str:
        """Return a string representation of the error details."""
        return f"{self.error_code}:{self.extra_data}"

    def __repr__(self) -> str:
        """Return a string representation of the error details."""
        return f"{self.error_code}:{self.extra_data}"

    def to_dict(self) -> dict:
        """Return a dictionary representation of the error details."""
        return {"error_code": str(self.error_code), "extra_data": self.extra_data}


class BaseAPIException(APIException):
    """base exception for all exceptions."""

    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    errors: ClassVar[list[ErrorDetail]] = []
    detail = None

    def __init__(self, errors: ErrorDetail | list[ErrorDetail]) -> None:
        """Initialize the BaseAPIException.

        :param errors: A single ErrorDetail or a list of ErrorDetail instances.
        """
        self.errors = errors if isinstance(errors, list) else [errors]

    def to_dict(self) -> dict:
        """Return a dictionary representation of the exception."""
        return {"errors": [error.to_dict() for error in self.errors]}


class Http400BadRequestException(BaseAPIException):
    """base exception for Bad Request."""

    status_code = status.HTTP_400_BAD_REQUEST


class Http401UnauthorizedException(BaseAPIException):
    """base exception for Unauthorized."""

    status_code = status.HTTP_401_UNAUTHORIZED


class Http403ForbiddenException(BaseAPIException):
    """base exception for Forbidden."""

    status_code = status.HTTP_403_FORBIDDEN
    errors: ClassVar[list[ErrorDetail]] = [ErrorDetail(ErrorCode("common", "forbidden"), {})]

    def __init__(self, message: str | None = None) -> None:
        """Initialize the Http403ForbiddenException."""
        self.errors = [ErrorDetail(ErrorCode("common", "forbidden"), {"message": message})]


class Http404NotFoundException(BaseAPIException):
    """base exception for Not Found."""

    status_code = status.HTTP_404_NOT_FOUND


class KeyNotFoundException(BaseAPIException):
    """Exception for 404 Not Found errors."""

    status_code = status.HTTP_404_NOT_FOUND

    def __init__(self, error_code: ErrorCode, keys: list[str] | str) -> None:
        """Initialize the Http404NotFoundException."""
        if not isinstance(keys, list):
            keys = [keys]
        errors = [ErrorDetail(error_code, {"id": key}) for key in keys]
        super().__init__(errors)


class PermissionDeniedException(BaseAPIException):
    """Exception for 403 Forbidden errors."""

    status_code = status.HTTP_403_FORBIDDEN

    def __init__(self, error_code: ErrorCode, required_permissions: list[str] | str) -> None:
        """Initialize the PermissionDeniedException."""
        if not isinstance(required_permissions, list):
            required_permissions = [required_permissions]

        errors = [
            ErrorDetail(
                error_code,
                {
                    "missing_permissions": required_permissions,
                },
            ),
        ]
        super().__init__(errors)


class ValidationFailedException(BaseAPIException):
    """Exception for 422 Unprocessable Entity errors."""

    status_code = status.HTTP_422_UNPROCESSABLE_ENTITY

    def __init__(self, error_code: ErrorCode, missing_fields: list[str] | str) -> None:
        """Initialize the ValidationFailedException."""
        if not isinstance(missing_fields, list):
            missing_fields = [missing_fields]

        errors = [
            ErrorDetail(
                error_code,
                {"missing_fields": missing_fields},
            ),
        ]
        super().__init__(errors)


class DuplicateKeyException(BaseAPIException):
    """Exception for 400 Conflict errors."""

    status_code = status.HTTP_400_BAD_REQUEST

    def __init__(self, error_code: ErrorCode, duplicate_keys: list[str] | str) -> None:
        """Initialize the DuplicateKeyException."""
        if not isinstance(duplicate_keys, list):
            duplicate_keys = [duplicate_keys]

        errors = [
            ErrorDetail(
                error_code,
                {"duplicate_keys": duplicate_keys},
            ),
        ]
        super().__init__(errors)
