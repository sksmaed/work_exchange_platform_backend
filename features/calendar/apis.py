from django.core.handlers.wsgi import WSGIRequest
from django.db.models import QuerySet
from ninja_extra import api_controller, route
from ninja_extra.permissions import IsAuthenticated

from common.exceptions import Http403ForbiddenException, KeyNotFoundException
from features.application.models import Application
from features.calendar.exceptions import CalendarEventNotFoundError
from features.calendar.models import CalendarEvent
from features.calendar.schemas import (
    CalendarEventOccupancySchema,
    CalendarEventResponseSchema,
    CalendarEventUpdateSchema,
)
from features.host.exceptions import HostNotFoundError
from features.host.models import Host


@api_controller(prefix_or_class="calendar", tags=["calendar"], permissions=[IsAuthenticated])
class CalendarControllerAPI:
    """API endpoints for managing calendar events."""

    @route.get("/hosts/{host_id}/events", response={200: list[CalendarEventResponseSchema]})
    def list_calendar_events(self, request: WSGIRequest, host_id: str) -> QuerySet[CalendarEvent]:
        """Retrieve a list of calendar events for a specific host."""
        user = request.user

        try:
            host = Host.objects.get(id=host_id)
        except Host.DoesNotExist:
            raise KeyNotFoundException(HostNotFoundError, host_id)

        # Keep host events private for host-side calendar operations.
        if host.user != user:
            raise Http403ForbiddenException("You do not have permission to view these calendar events")

        return CalendarEvent.objects.filter(host=host).select_related("helper", "helper__user").order_by("start_date")

    @route.get("/hosts/{host_id}/occupancy", response={200: list[CalendarEventOccupancySchema]})
    def list_host_occupancy(self, request: WSGIRequest, host_id: str) -> QuerySet[CalendarEvent]:
        """Retrieve accepted occupancy date ranges for a host (helper-facing public data)."""
        _ = request.user  # endpoint requires authentication via controller permission

        try:
            host = Host.objects.get(id=host_id)
        except Host.DoesNotExist:
            raise KeyNotFoundException(HostNotFoundError, host_id)

        return CalendarEvent.objects.filter(host=host, application__status=Application.StatusChoices.ACCEPTED).order_by(
            "start_date"
        )

    @route.patch("/events/{event_id}", response={200: CalendarEventResponseSchema})
    def update_calendar_event(
        self, request: WSGIRequest, event_id: str, data: CalendarEventUpdateSchema
    ) -> CalendarEvent:
        """Host updates a calendar event (e.g., modifying dates or remarks)."""
        user = request.user

        try:
            event = CalendarEvent.objects.select_related("host", "helper", "helper__user").get(id=event_id)
        except CalendarEvent.DoesNotExist:
            raise KeyNotFoundException(CalendarEventNotFoundError, event_id)

        # Ensure the user requesting is the host owner
        if event.host.user != user:
            raise Http403ForbiddenException("You do not have permission to edit this calendar event")

        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(event, field, value)

        event.save(user=user, update_fields=list(update_data.keys()))

        return event

    @route.delete("/events/{event_id}")
    def delete_calendar_event(self, request: WSGIRequest, event_id: str) -> dict:
        """Host deletes a calendar event."""
        user = request.user

        try:
            event = CalendarEvent.objects.select_related("host").get(id=event_id)
        except CalendarEvent.DoesNotExist:
            raise KeyNotFoundException(CalendarEventNotFoundError, event_id)

        # Ensure the user requesting is the host owner
        if event.host.user != user:
            raise Http403ForbiddenException("You do not have permission to delete this calendar event")

        event.delete()
        return {"detail": "Calendar event deleted successfully"}
