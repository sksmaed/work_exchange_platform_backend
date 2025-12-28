from django.core.handlers.wsgi import WSGIRequest
from django.db.models import Exists, OuterRef, Q, QuerySet
from ninja_extra import api_controller, route
from ninja_extra.ordering import Ordering, ordering
from ninja_extra.pagination import PageNumberPagination, paginate
from ninja_extra.schemas import NinjaPaginationResponseSchema
from ninja_extra.searching import Searching, searching

from common.exceptions import Http403ForbiddenException, KeyNotFoundException
from features.host.exceptions import HostNotFoundError
from features.host.models import HostModel
from features.host.schemas import HostCreateSchema, HostResponseSchema, HostUpdateSchema


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
    ) -> QuerySet[HostModel]:
        """Retrieve a list of hosts created by the authenticated user, with optional filtering by frequency."""
        user = request.user

        filters = Q(user=user)
        if address:
            filters &= Q(address__icontains=address)
        if host_type:
            filters &= Q(type__icontains=host_type)
        if month:
            # TODO(sks): Implement month-based filtering logic with vacancy dates  # noqa: TD003
            pass
        if duration:
            filters &= Q(expected_duration=duration)

        exclude_children_subquery = HostModel.objects.filter(id=OuterRef("id")).exclude(
            Q(expected_age__icontains="18") | Q(expected_age="")
        )

        return (
            HostModel.objects.filter(filters)
            .annotate(exclude_children=Exists(exclude_children_subquery))
            .select_related("user")
        )

    @route.post("", response=HostResponseSchema)
    def create_host(self, request: WSGIRequest, data: HostCreateSchema) -> HostModel:
        """Create a new host entry."""
        user = request.user
        host = HostModel(
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
            expected_licenses=data.expected_licenses or "None",
            expected_age=data.expected_age or "",
            expected_gender=data.expected_gender or "",
            expected_personality=data.expected_personality or "",
            expected_other_requirements=data.expected_other_requirements or "",
            recruitment_slogan=data.recruitment_slogan or "",
        )
        host.save(user=user)
        return host

    @route.patch("/{host_id}", response=HostResponseSchema)
    def update_host(self, request: WSGIRequest, host_id: str, data: HostUpdateSchema) -> HostModel:
        """Update an existing host entry."""
        user = request.user

        try:
            host = HostModel.objects.get(id=host_id)
        except HostModel.DoesNotExist:
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

        host = HostModel.objects.filter(id=host_id).first()
        if not host:
            raise KeyNotFoundException(HostNotFoundError, host_id)

        if host.user != user:
            raise Http403ForbiddenException("You do not have permission to delete this host")

        host.delete()
        return {"detail": "Host deleted successfully"}
