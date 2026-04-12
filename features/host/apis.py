import base64
import re

from django.core.files.base import ContentFile
from django.core.handlers.wsgi import WSGIRequest
from django.db import transaction
from django.db.models import Exists, F, OuterRef, Q, QuerySet
from ninja import File, UploadedFile
from ninja_extra import api_controller, route
from ninja_extra.ordering import Ordering, ordering
from ninja_extra.pagination import PageNumberPagination, paginate
from ninja_extra.permissions import AllowAny, IsAuthenticated
from ninja_extra.schemas import NinjaPaginationResponseSchema
from ninja_extra.searching import Searching, searching

from common.exceptions import (
    ErrorCode,
    ErrorDetail,
    Http400BadRequestException,
    Http403ForbiddenException,
    KeyNotFoundException,
)
from features.core.models import User
from features.host.exceptions import HostNotFoundError, VacancyNotFoundError
from features.host.models import Host, HostReview, HostReviewImage, Vacancy, VacancyAvailability
from features.host.schemas import (
    HostCreateSchema,
    HostResponseSchema,
    HostReviewCreateSchema,
    HostReviewResponseSchema,
    HostReviewSummarySchema,
    HostUpdateSchema,
    VacancyCreateSchema,
    VacancyResponseSchema,
    VacancyUpdateSchema,
)

_MAX_REVIEW_IMAGE_BYTES = 2 * 1024 * 1024
_ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/gif", "image/webp"}
_DATA_URL_RE = re.compile(
    r"^data:image/(jpeg|jpg|png|gif|webp);base64,(.+)$",
    re.IGNORECASE | re.DOTALL,
)


def _replace_review_images_from_data_urls(review: HostReview, photos: list[str], user: User) -> None:
    """Replace review images with decoded data URLs from the client (ReviewModal)."""
    review.images.all().delete()
    for i, data_url in enumerate(photos):
        m = _DATA_URL_RE.match(data_url.strip())
        if not m:
            raise Http400BadRequestException(
                [
                    ErrorDetail(
                        ErrorCode("host", "invalid_review_photo"),
                        {"message": "Each photo must be data:image/jpeg|png|gif|webp;base64,..."},
                    )
                ]
            )
        ext = m.group(1).lower()
        b64 = m.group(2)
        if ext == "jpg":
            ext = "jpeg"
        try:
            raw = base64.b64decode(b64, validate=True)
        except (ValueError, TypeError):
            raise Http400BadRequestException(
                [
                    ErrorDetail(
                        ErrorCode("host", "invalid_review_photo"),
                        {"message": "Invalid base64 image data"},
                    )
                ]
            )
        if len(raw) > _MAX_REVIEW_IMAGE_BYTES:
            raise Http400BadRequestException(
                [
                    ErrorDetail(
                        ErrorCode("host", "invalid_review_photo"),
                        {"message": f"Each image must be at most {_MAX_REVIEW_IMAGE_BYTES // (1024 * 1024)}MB"},
                    )
                ]
            )
        suffix = ".jpg" if ext == "jpeg" else f".{ext}"
        name = f"review_{i}{suffix}"
        hi = HostReviewImage(review=review)
        hi.image.save(name, ContentFile(raw), save=False)
        hi.save(user=user)


@api_controller(prefix_or_class="hosts", tags=["hosts"], permissions=[IsAuthenticated])
class HostControllerAPI:
    """API endpoints for managing hosts."""

    @route.get(
        "",
        response={200: NinjaPaginationResponseSchema[HostResponseSchema]},
        auth=None,
        permissions=[AllowAny],
    )
    @paginate(PageNumberPagination)
    @searching(Searching, search_fields=["description", "type", "address"])
    @ordering(Ordering, ordering_fields=["created_at", "avg_rating"])
    def list_hosts(
        self,
        request: WSGIRequest,  # noqa: ARG002
        address: str | None = None,
        host_type: str | None = None,
        month: int | None = None,
        duration: str | None = None,
    ) -> QuerySet[Host]:
        """Retrieve a list of hosts created by the authenticated user, with optional filtering by frequency."""
        filters = Q()
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
            .prefetch_related("vacancy_set__availabilities")
            .order_by("-created_at")
        )

    @route.get(
        "/me",
        response={200: NinjaPaginationResponseSchema[HostResponseSchema]},
    )
    @paginate(PageNumberPagination)
    def my_hosts(self, request: WSGIRequest) -> QuerySet[Host]:
        """Return only hosts owned by the authenticated user."""
        return (
            Host.objects.filter(user=request.user)
            .select_related("user")
            .prefetch_related("vacancy_set__availabilities")
            .order_by("-created_at")
        )

    @route.post("", response=HostResponseSchema)
    def create_host(self, request: WSGIRequest, data: HostCreateSchema) -> Host:
        """Create a new host entry."""
        user = request.user
        host = Host(
            user=user,
            name=data.name or "",
            description=data.description or "",
            address=data.address or "",
            type=data.type or "",
            phone_number=data.phone_number or "",
            contact_information=data.contact_information or [],
            pocket_money=data.pocket_money or 0,
            meals_offered=data.meals_offered or "",
            dayoffs=data.dayoffs or "",
            allowance=data.allowance or "",
            facilities=data.facilities or "",
            other=data.other or "",
            expected_duration=data.expected_duration or "",
            vehicle=data.vehicle or "",
            recruitment_slogan=data.recruitment_slogan or "",
        )
        host.save(user=user)
        return host

    @route.get("/{host_id}", response={200: HostResponseSchema}, auth=None, permissions=[AllowAny])
    def get_host(self, request: WSGIRequest, host_id: str) -> Host:  # noqa: ARG002
        """Retrieve a single host by ID."""
        try:
            return Host.objects.get(id=host_id)
        except Host.DoesNotExist:
            raise KeyNotFoundException(HostNotFoundError, host_id)

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

    @route.post("/{host_id}/host-image", response=HostResponseSchema)
    def upload_host_image(
        self,
        request: WSGIRequest,
        host_id: str,
        image: UploadedFile = File(...),
    ) -> Host:
        """Upload or replace host cover image."""
        user = request.user
        try:
            host = Host.objects.get(id=host_id)
        except Host.DoesNotExist:
            raise KeyNotFoundException(HostNotFoundError, host_id)

        if host.user != user:
            raise Http403ForbiddenException("You do not have permission to update this host")

        content_type = getattr(image, "content_type", "") or ""
        if content_type not in _ALLOWED_IMAGE_TYPES:
            raise Http400BadRequestException(
                [
                    ErrorDetail(
                        ErrorCode("host", "invalid_image"),
                        {"message": "Only JPEG, PNG, GIF, and WebP images are allowed"},
                    )
                ]
            )

        host.host_image.save(image.name, image, save=True)
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
        return Vacancy.objects.filter(host=host).prefetch_related("availabilities").order_by("-created_at")

    @route.get("/vacancies/{vacancy_id}", response={200: VacancyResponseSchema})
    def get_vacancy(self, request: WSGIRequest, vacancy_id: str) -> Vacancy:  # noqa: ARG002
        """Retrieve details of a specific vacancy."""
        try:
            return Vacancy.objects.select_related("host").prefetch_related("availabilities").get(id=vacancy_id)
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
            expected_other_requirements=data.expected_other_requirements,
            other_questions=data.other_questions,
            status=data.status,
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

        return Vacancy.objects.select_related("host").prefetch_related("availabilities").get(id=vacancy.id)

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

    @route.post("/vacancies/{vacancy_id}/vacancy-image", response=VacancyResponseSchema)
    def upload_vacancy_image(
        self,
        request: WSGIRequest,
        vacancy_id: str,
        image: UploadedFile = File(...),
    ) -> Vacancy:
        """Upload or replace vacancy image."""
        user = request.user
        try:
            vacancy = Vacancy.objects.select_related("host").get(id=vacancy_id)
        except Vacancy.DoesNotExist:
            raise KeyNotFoundException(VacancyNotFoundError, vacancy_id)

        if vacancy.host.user != user:
            raise Http403ForbiddenException("You do not have permission to update this vacancy")

        content_type = getattr(image, "content_type", "") or ""
        if content_type not in _ALLOWED_IMAGE_TYPES:
            raise Http400BadRequestException(
                [
                    ErrorDetail(
                        ErrorCode("host", "invalid_image"),
                        {"message": "Only JPEG, PNG, GIF, and WebP images are allowed"},
                    )
                ]
            )

        vacancy.vacancy_image.save(image.name, image, save=True)
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

    # ---- Reviews ----

    @route.get(
        "/{host_id}/reviews",
        response={200: HostReviewSummarySchema},
        auth=None,
        permissions=[AllowAny],
    )
    def list_reviews(self, request: WSGIRequest, host_id: str) -> dict:  # noqa: ARG002
        """List all reviews for a host and return a summary."""
        try:
            host = Host.objects.get(id=host_id)
        except Host.DoesNotExist:
            raise KeyNotFoundException(HostNotFoundError, host_id)

        review_list = list(
            HostReview.objects.filter(host=host)
            .select_related("reviewer")
            .prefetch_related("images")
            .order_by("-created_at")
        )
        total = len(review_list)
        avg = sum(r.rating for r in review_list) / total if total else 0.0
        distribution = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
        for r in review_list:
            distribution[r.rating] += 1

        # Return a plain dict so ninja serialises ORM objects via HostReviewSummarySchema.
        # Passing pre-built schema instances would cause resolvers to receive schema
        # objects instead of ORM objects, silently returning default values.
        return {
            "average_rating": round(avg, 2),
            "total_reviews": total,
            "distribution": distribution,
            "reviews": review_list,
        }

    @route.post("/{host_id}/reviews", response={201: HostReviewResponseSchema})
    def create_review(self, request: WSGIRequest, host_id: str, data: HostReviewCreateSchema) -> HostReview:
        """Submit a review for a host (one per user)."""
        user = request.user
        try:
            host = Host.objects.get(id=host_id)
        except Host.DoesNotExist:
            raise KeyNotFoundException(HostNotFoundError, host_id)

        if host.user == user:
            raise Http403ForbiddenException("You cannot review your own host profile")

        with transaction.atomic():
            review, created = HostReview.objects.get_or_create(
                host=host,
                reviewer=user,
                defaults={"rating": data.rating, "comment": data.comment},
            )
            if not created:
                review.rating = data.rating
                review.comment = data.comment
                review.save(user=user)

            _replace_review_images_from_data_urls(review, data.photos, user)

            self._refresh_avg_rating(host)

        return HostReview.objects.select_related("reviewer").prefetch_related("images").get(pk=review.pk)

    @route.delete("/{host_id}/reviews/{review_id}")
    def delete_review(self, request: WSGIRequest, host_id: str, review_id: str) -> dict:
        """Delete the authenticated user's review for a host."""
        user = request.user
        try:
            host = Host.objects.get(id=host_id)
        except Host.DoesNotExist:
            raise KeyNotFoundException(HostNotFoundError, host_id)

        review = HostReview.objects.filter(id=review_id, host=host).first()
        if not review:
            raise KeyNotFoundException(HostNotFoundError, review_id)

        if review.reviewer != user:
            raise Http403ForbiddenException("You can only delete your own review")

        review.delete()
        self._refresh_avg_rating(host)
        return {"detail": "Review deleted"}

    @staticmethod
    def _refresh_avg_rating(host: Host) -> None:
        """Recalculate and persist host.avg_rating from all reviews."""
        from django.db.models import Avg  # noqa: PLC0415

        result = HostReview.objects.filter(host=host).aggregate(avg=Avg("rating"))
        host.avg_rating = result["avg"] or 0.0
        host.save(update_fields=["avg_rating"])


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

        return Vacancy.objects.filter(filters).distinct().order_by("-created_at").select_related("host")
