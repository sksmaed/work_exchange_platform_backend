from django.db import models

from common.models import BaseModel


class CalendarEvent(BaseModel):
    """Model representing a calendar event for a host, usually generated when an application is accepted.

    Attributes:
    ----------
    host : ForeignKey
        The host whose calendar this event belongs to.
    helper : ForeignKey
        The helper involved in this event (optional, for work exchange context).
    application : ForeignKey
        The application from which this event was generated (optional).
    start_date : DateField
        The start date of the event.
    end_date : DateField
        The end date of the event.
    remarks : TextField
        Additional notes or remarks created by the host.
    """

    host = models.ForeignKey(
        "host.Host",
        on_delete=models.CASCADE,
        related_name="calendar_events",
    )
    helper = models.ForeignKey(
        "helper.HelperModel",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="calendar_events",
    )
    application = models.ForeignKey(
        "application.Application",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="calendar_events",
    )
    start_date = models.DateField()
    end_date = models.DateField()
    remarks = models.TextField(
        blank=True,
        default="",
    )

    def __str__(self) -> str:
        """String representation."""
        return f"CalendarEvent(Host: {self.host.name}, Dates: {self.start_date} to {self.end_date})"
