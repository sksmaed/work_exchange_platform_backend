from common.exceptions import BaseAPIException


class CalendarEventNotFoundError(BaseAPIException):
    """Raised when a calendar event is not found."""

    ERROR_CODE = "CALENDAR_EVENT_NOT_FOUND"
    MESSAGE = "Calendar event with ID {args[0]} was not found."
