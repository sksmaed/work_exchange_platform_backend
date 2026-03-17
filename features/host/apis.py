from django.core.handlers.wsgi import WSGIRequest
from django.db.models import Exists, F, OuterRef, Q, QuerySet
from ninja_extra import api_controller, route
from ninja_extra.ordering import Ordering, ordering
from ninja_extra.pagination import PageNumberPagination, paginate
from ninja_extra.schemas import NinjaPaginationResponseSchema
from ninja_extra.searching import Searching, searching

from common.exceptions import Http403ForbiddenException, KeyNotFoundException
from features.host.exceptions import HostNotFoundError, VacancyNotFoundError
from features.host.models import Host, Vacancy, VacancyAvailability
from features.host.schemas import (
    HostCreateSchema,
    HostResponseSchema,
    HostUpdateSchema,
    VacancyCreateSchema,
    VacancyResponseSchema,
    VacancyUpdateSchema,
)


@api_controller(prefix_or_class="hosts", tags=["hosts"])
class HostControllerAPI:
    """API endpoints for managing hosts."""

    @route.get("", response={200: NinjaPaginationResponseSchema[HostResponseSchema]})
    @paginate(PageNumberPagination)
    @searching(Searching, search_fields=["description", "type", "address"])
    @ordering(Ordering, ordering_fields=["created_at"])
    def list_hosts(
        self,
        request: WSGIRequest,
        address: str | None = None,
        host_type: str | None = None,
        month: int | None = None,
        duration: str | None = None,
    ) -> QuerySet[Host]:
        """Retrieve a list of hosts created by the authenticated user, with optional filtering by frequency."""
        user = request.user

        filters = Q(user=user)
        if address:
            filters &= Q(address__icontains=address)
        if host_type:
            filters &= Q(type__icontains=host_type)
        if month:
            from django.db.models.functions import ExtractMonth  # noqa: PLC0415

            # Filter hosts that have vacancies with available space in the specified month
            month_availabilities = VacancyAvailability.objects.annotate(
                start_month=ExtractMonth("start_date"), end_month=ExtractMonth("end_date")
            ).filter(start_month__lte=month, end_month__gte=month)
            filters &= Q(id__in=month_availabilities.values("vacancy__host"))
        if duration:
            filters &= Q(expected_duration=duration)

        exclude_children_subquery = Vacancy.objects.filter(host_id=OuterRef("id")).exclude(
            Q(expected_age__icontains="18") | Q(expected_age="")
        )

        return (
            Host.objects.filter(filters)
            .annotate(exclude_children=Exists(exclude_children_subquery))
            .select_related("user")
        )

    @route.post("", response=HostResponseSchema)
    def create_host(self, request: WSGIRequest, data: HostCreateSchema) -> Host:
        """Create a new host entry."""
        user = request.user
        host = Host(
            user=user,
            description=data.description,
            address=data.address,
            type=data.type,
            contact_information=data.contact_information or "",
            pocket_money=data.pocket_money or 0,
            meals_offered=data.meals_offered or "",
            dayoffs=data.dayoffs or "",
            allowance=data.allowance or "",
            facilities=data.facilities or "",
            other=data.other or "",
            expected_duration=data.expected_duration or "",
            recruitment_slogan=data.recruitment_slogan or "",
        )
        host.save(user=user)
        return host

    @route.patch("/{host_id}", response=HostResponseSchema)
    def update_host(self, request: WSGIRequest, host_id: str, data: HostUpdateSchema) -> Host:
        """Update an existing host entry."""
        user = request.user

        try:
            host = Host.objects.get(id=host_id)
        except Host.DoesNotExist:
            raise KeyNotFoundException(HostNotFoundError, host_id)

        if host.user != user:
            raise Http403ForbiddenException("You do not have permission to update this host")

        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(host, field, value)

        host.save(user=user, update_fields=list(update_data.keys()))
        return host

    @route.delete("/{host_id}")
    def delete_host(self, request: WSGIRequest, host_id: str) -> dict:
        """Delete a host entry."""
        user = request.user

        host = Host.objects.filter(id=host_id).first()
        if not host:
            raise KeyNotFoundException(HostNotFoundError, host_id)

        if host.user != user:
            raise Http403ForbiddenException("You do not have permission to delete this host")

        host.delete()
        return {"detail": "Host deleted successfully"}

    @route.get("/{host_id}/vacancies", response={200: list[VacancyResponseSchema]})
    def list_vacancies(self, request: WSGIRequest, host_id: str) -> QuerySet[Vacancy]:  # noqa: ARG002
        """Retrieve a list of vacancies for a specific host."""
        try:
            host = Host.objects.get(id=host_id)
        except Host.DoesNotExist:
            raise KeyNotFoundException(HostNotFoundError, host_id)

        # Allow anyone to see vacancies of a host, or restrict to host owner depending on requirements.
        # Here we allow public read for vacancies of a valid host.
        return Vacancy.objects.filter(host=host).order_by("-created_at")

    @route.get("/vacancies/{vacancy_id}", response={200: VacancyResponseSchema})
    def get_vacancy(self, request: WSGIRequest, vacancy_id: str) -> Vacancy:  # noqa: ARG002
        """Retrieve details of a specific vacancy."""
        try:
            return Vacancy.objects.select_related("host").get(id=vacancy_id)
        except Vacancy.DoesNotExist:
            raise KeyNotFoundException(VacancyNotFoundError, vacancy_id)

    @route.post("/{host_id}/vacancies", response={201: VacancyResponseSchema})
    def create_vacancy(self, request: WSGIRequest, host_id: str, data: VacancyCreateSchema) -> Vacancy:
        """Create a new vacancy for a host."""
        user = request.user

        try:
            host = Host.objects.get(id=host_id)
        except Host.DoesNotExist:
            raise KeyNotFoundException(HostNotFoundError, host_id)

        if host.user != user:
            raise Http403ForbiddenException("You do not have permission to add vacancies to this host")

        vacancy = Vacancy(
            host=host,
            name=data.name,
            work_time=data.work_time,
            description=data.description,
            expected_duration=data.expected_duration,
            expected_age=data.expected_age,
            expected_gender=data.expected_gender,
            expected_licenses=data.expected_licenses,
            expected_personality=data.expected_personality,
        )
        vacancy.save(user=user)

        # Create availabilities
        for avail_data in data.availabilities:
            VacancyAvailability.objects.create(
                vacancy=vacancy,
                start_date=avail_data["start_date"],
                end_date=avail_data["end_date"],
                capacity=avail_data.get("capacity", 1),
                current_helpers=avail_data.get("current_helpers", 0),
                created_by_user=user,
                updated_by_user=user,
            )

        return vacancy

    @route.patch("/vacancies/{vacancy_id}", response=VacancyResponseSchema)
    def update_vacancy(self, request: WSGIRequest, vacancy_id: str, data: VacancyUpdateSchema) -> Vacancy:
        """Update an existing vacancy."""
        user = request.user

        try:
            vacancy = Vacancy.objects.select_related("host").get(id=vacancy_id)
        except Vacancy.DoesNotExist:
            raise KeyNotFoundException(VacancyNotFoundError, vacancy_id)

        if vacancy.host.user != user:
            raise Http403ForbiddenException("You do not have permission to update this vacancy")

        update_data = data.model_dump(exclude_unset=True, exclude={"availabilities"})
        for field, value in update_data.items():
            setattr(vacancy, field, value)

        vacancy.save(user=user, update_fields=list(update_data.keys()))

        # Update availabilities if provided
        if data.availabilities is not None:
            # For simplicity, replace all existings with new ones, or you could do a more careful sync
            vacancy.availabilities.all().delete()
            for avail_data in data.availabilities:
                VacancyAvailability.objects.create(
                    vacancy=vacancy,
                    start_date=avail_data["start_date"],
                    end_date=avail_data["end_date"],
                    capacity=avail_data.get("capacity", 1),
                    current_helpers=avail_data.get("current_helpers", 0),
                    created_by_user=user,
                    updated_by_user=user,
                )

        return vacancy

    @route.delete("/vacancies/{vacancy_id}")
    def delete_vacancy(self, request: WSGIRequest, vacancy_id: str) -> dict:
        """Delete a vacancy."""
        user = request.user

        vacancy = Vacancy.objects.filter(id=vacancy_id).select_related("host").first()
        if not vacancy:
            raise KeyNotFoundException(VacancyNotFoundError, vacancy_id)

        if vacancy.host.user != user:
            raise Http403ForbiddenException("You do not have permission to delete this vacancy")

        vacancy.delete()
        return {"detail": "Vacancy deleted successfully"}


@api_controller(prefix_or_class="vacancies", tags=["vacancies"])
class VacancyControllerAPI:
    """API endpoints for managing vacancies across all hosts."""

    @route.get("/search", response={200: NinjaPaginationResponseSchema[VacancyResponseSchema]})
    @paginate(PageNumberPagination)
    @searching(Searching, search_fields=["name", "description", "expected_personality"])
    @ordering(Ordering, ordering_fields=["created_at"])
    def search_vacancies(
        self,
        request: WSGIRequest,  # noqa: ARG002
        start_date: str | None = None,
        end_date: str | None = None,
    ) -> QuerySet[Vacancy]:
        """Search active vacancies with available capacity, optionally matching a specific date range."""
        from django.utils import timezone  # noqa: PLC0415

        filters = Q(status=Vacancy.StatusChoices.RECRUITING)

        # Must have at least one availability that is not full and ending in the future
        avail_filters = Q(end_date__gte=timezone.now().date(), current_helpers__lt=F("capacity"))

        if start_date and end_date:
            avail_filters &= Q(start_date__lte=start_date, end_date__gte=end_date)

        active_availabilities = VacancyAvailability.objects.filter(avail_filters)

        filters &= Q(id__in=active_availabilities.values("vacancy_id"))

        return Vacancy.objects.filter(filters).distinct().order_by("-created_at")
