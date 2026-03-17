"""Exceptions for Application feature."""


class ApplicationAlreadyExistsError(Exception):
    """Exception raised when an application already exists."""


class ApplicationNotFoundError(Exception):
    """Exception raised when an application is not found."""
