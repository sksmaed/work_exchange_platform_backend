from common.exceptions import ErrorCode


class HostNotFoundError(ErrorCode):
    """Exception raised when a host is not found."""

    prefix = "host"
    name = "host_not_found"


class VacancyNotFoundError(ErrorCode):
    """Exception raised when a vacancy is not found."""

    prefix = "host"
    name = "vacancy_not_found"
