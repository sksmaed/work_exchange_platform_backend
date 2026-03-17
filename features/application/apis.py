from django.core.handlers.wsgi import WSGIRequest
from django.db import IntegrityError
from django.db.models import F, Q, QuerySet
from django.shortcuts import get_object_or_404
from ninja_extra import api_controller, route
from ninja_extra.permissions import IsAuthenticated

from common.exceptions import (
    DuplicateKeyException,
    Http400BadRequestException,
    Http403ForbiddenException,
    KeyNotFoundException,
)
from features.application.exceptions import ApplicationAlreadyExistsError, ApplicationNotFoundError
from features.application.models import Application
from features.application.schemas import (
    ApplicationCreateSchema,
    ApplicationResponseSchema,
    ApplicationStatusUpdateSchema,
)
from features.helper.models import HelperModel
from features.host.models import Host, Vacancy

MAX_VACANCY_CAPACITY = 20


@api_controller(prefix_or_class="applications", tags=["applications"], permissions=[IsAuthenticated])
class ApplicationControllerAPI:
    """API endpoints for managing applications."""

    @route.post("", response={201: ApplicationResponseSchema})
    def create_application(self, request: WSGIRequest, data: ApplicationCreateSchema) -> Application:
        """Helper submits an application to a vacancy."""
        user = request.user

        # Get the helper profile
        helper = get_object_or_404(HelperModel, user_id=user.id)

        # Get the vacancy
        vacancy = get_object_or_404(Vacancy, id=data.vacancy_id)

        # Validate start_date and end_date
        if data.start_date > data.end_date:
            raise Http400BadRequestException("Start date cannot be after end date")

        # Check if the requested dates fall within any of the vacancy's availability periods with enough capacity
        from features.host.models import VacancyAvailability  # noqa: PLC0415

        valid_availability = VacancyAvailability.objects.filter(
            vacancy=vacancy,
            start_date__lte=data.start_date,
            end_date__gte=data.end_date,
            current_helpers__lt=F("capacity"),
        ).first()

        if not valid_availability:
            raise Http400BadRequestException(
                "The requested dates are not available or the vacancy is full for this period."
            )

        # Check if application already exists
        try:
            application = Application(
                helper=helper,
                vacancy=vacancy,
                start_date=data.start_date,
                end_date=data.end_date,
                status=Application.StatusChoices.PENDING,
            )
            application.save(user=user)
        except IntegrityError:
            # Duplicate application (unique_together constraint)
            raise DuplicateKeyException(ApplicationAlreadyExistsError, data.vacancy_id)
        else:
            return application

    @route.get("/self/", response={200: list[ApplicationResponseSchema]})
    def get_self_applications(self, request: WSGIRequest) -> QuerySet[Application]:
        """View applications where user is either the helper or the vacancy host."""
        user = request.user

        # Get applications where user is the helper OR the vacancy's host
        # Try to get helper profile (may not exist if user is only a host)
        helper = HelperModel.objects.filter(user=user).first()
        # Try to get host profiles (user may have multiple hosts)
        hosts = Host.objects.filter(user=user)

        # Build query: applications where user is helper OR vacancy's host

        filters = Q()
        if helper:
            filters |= Q(helper=helper)
        if hosts.exists():
            filters |= Q(vacancy__host__in=hosts)

        if not filters:
            # User is neither helper nor host, return empty queryset
            return Application.objects.none()

        return Application.objects.filter(filters).select_related(
            "helper", "vacancy", "vacancy__host", "helper__user", "vacancy__host__user"
        )

    @route.get("/{application_id}", response={200: ApplicationResponseSchema})
    def get_application(self, request: WSGIRequest, application_id: str) -> Application:
        """Get a specific application by ID. Accessible by both helper and vacancy host."""
        user = request.user

        try:
            application = Application.objects.select_related(
                "helper", "vacancy", "vacancy__host", "helper__user", "vacancy__host__user"
            ).get(id=application_id)
        except Application.DoesNotExist:
            raise KeyNotFoundException(ApplicationNotFoundError, application_id)

        # Both the helper who created the application AND the vacancy's host can view it
        is_helper = application.helper.user == user
        is_host = application.vacancy.host.user == user

        if not (is_helper or is_host):
            raise Http403ForbiddenException("You do not have permission to view this application")

        return application

    @route.delete("/{application_id}")
    def withdraw_application(self, request: WSGIRequest, application_id: str) -> dict:
        """Helper withdraws their application."""
        user = request.user

        application = Application.objects.filter(id=application_id).first()
        if not application:
            raise KeyNotFoundException(ApplicationNotFoundError, application_id)

        # Only the helper who created the application can withdraw it
        if application.helper.user != user:
            raise Http403ForbiddenException("You do not have permission to withdraw this application")

        old_status = application.status
        if old_status == Application.StatusChoices.ACCEPTED:
            from features.calendar.models import CalendarEvent  # noqa: PLC0415
            from features.host.models import VacancyAvailability  # noqa: PLC0415

            availability = VacancyAvailability.objects.filter(
                vacancy=application.vacancy,
                start_date__lte=application.start_date,
                end_date__gte=application.end_date,
            ).first()

            if availability:
                availability.current_helpers = F("current_helpers") - 1
                availability.save(update_fields=["current_helpers"])

            # Delete associated calendar event
            CalendarEvent.objects.filter(application=application).delete()

        # Update status to withdrawn instead of deleting
        application.status = Application.StatusChoices.WITHDRAWN
        application.save(user=user, update_fields=["status"])

        return {"detail": "Application withdrawn successfully"}

    @route.patch("/{application_id}/status", response={200: ApplicationResponseSchema})
    def update_application_status(
        self, request: WSGIRequest, application_id: str, data: ApplicationStatusUpdateSchema
    ) -> Application:
        """Vacancy host updates application status (accept/reject)."""
        user = request.user

        try:
            application = Application.objects.select_related(
                "helper", "vacancy", "vacancy__host", "vacancy__host__user"
            ).get(id=application_id)
        except Application.DoesNotExist:
            raise KeyNotFoundException(ApplicationNotFoundError, application_id)

        # Only the vacancy's host can update application status
        if application.vacancy.host.user != user:
            raise Http403ForbiddenException("Only the vacancy host can update application status")

        # Validate status
        if data.status not in [Application.StatusChoices.ACCEPTED, Application.StatusChoices.REJECTED]:
            raise Http403ForbiddenException(
                f"Status must be '{Application.StatusChoices.ACCEPTED}' or '{Application.StatusChoices.REJECTED}'"
            )

        from features.calendar.models import CalendarEvent  # noqa: PLC0415
        from features.host.models import VacancyAvailability  # noqa: PLC0415

        old_status = application.status
        new_status = data.status

        # Capacity and Calendar management
        if old_status != new_status:
            availability = VacancyAvailability.objects.filter(
                vacancy=application.vacancy,
                start_date__lte=application.start_date,
                end_date__gte=application.end_date,
            ).first()

            if availability:
                if new_status == Application.StatusChoices.ACCEPTED:
                    # Check capacity
                    if (
                        availability.current_helpers >= availability.capacity
                        or availability.current_helpers >= MAX_VACANCY_CAPACITY
                    ):
                        raise Http400BadRequestException("The vacancy has reached its capacity limit.")
                    availability.current_helpers = F("current_helpers") + 1
                    availability.save(update_fields=["current_helpers"])

                    # Create calendar event
                    CalendarEvent.objects.create(
                        host=application.vacancy.host,
                        helper=application.helper,
                        application=application,
                        start_date=application.start_date,
                        end_date=application.end_date,
                        remarks=f"Application accepted for {application.vacancy.name}.",
                    )
                elif (
                    old_status == Application.StatusChoices.ACCEPTED
                    and new_status == Application.StatusChoices.REJECTED
                ):
                    # Deduct capacity
                    availability.current_helpers = F("current_helpers") - 1
                    availability.save(update_fields=["current_helpers"])

                    # Remove calendar event
                    CalendarEvent.objects.filter(application=application).delete()

        # Update status
        application.status = new_status
        application.save(user=user, update_fields=["status"])

        return application
