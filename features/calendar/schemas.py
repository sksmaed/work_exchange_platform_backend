import typing
from datetime import date
from uuid import UUID

from ninja import ModelSchema, Schema

from features.calendar.models import CalendarEvent
from features.helper.schemas import HelperProfileResponseSchema


class CalendarEventResponseSchema(ModelSchema):
    """Schema for CalendarEvent response."""

    id: UUID
    helper: HelperProfileResponseSchema | None = None

    class Meta:
        model = CalendarEvent
        exclude: typing.ClassVar[tuple[str, ...]] = (
            "created_at",
            "created_by_user",
            "updated_at",
            "updated_by_user",
        )


class CalendarEventOccupancySchema(Schema):
    """Public occupancy payload for helper-side vacancy calendars."""

    start_date: date
    end_date: date


class CalendarEventUpdateSchema(Schema):
    """Schema for updating a calendar event."""

    start_date: date | None = None
    end_date: date | None = None
    remarks: str | None = None
