from common.exceptions import ErrorCode


class HostNotFoundError(ErrorCode):
    """Exception raised when a host is not found."""

    prefix = "host"
    name = "host_not_found"
