import re
import typing
from datetime import date
from uuid import UUID

from ninja import Field, ModelSchema, Schema
from pydantic import field_validator

from features.host.models import Host, HostReview, Vacancy, VacancyAvailability

MONTHS_PER_YEAR = 12


class HostResponseSchema(ModelSchema):
    """Schema for Host response."""

    exclude_children: bool | None = None
    months: list[int] = Field(default_factory=list)
    duration_options: list[str] = Field(default_factory=list)
    keywords: list[str] = Field(default_factory=list)

    class Meta:
        model = Host
        exclude: typing.ClassVar[tuple[str, ...]] = (
            "updated_at",
            "updated_by_user",
        )

    @staticmethod
    def _month_iter(start: date, end: date) -> list[int]:
        if not start or not end:
            return []
        current = date(start.year, start.month, 1)
        end_month = date(end.year, end.month, 1)
        months: list[int] = []
        while current <= end_month:
            months.append(current.month)
            current = (
                date(current.year + 1, 1, 1)
                if current.month == MONTHS_PER_YEAR
                else date(current.year, current.month + 1, 1)
            )
        return months

    @staticmethod
    def resolve_months(obj: Host) -> list[int]:
        """Extract unique months from all vacancy availabilities."""
        months: set[int] = set()
        for vacancy in obj.vacancy_set.all():
            for availability in vacancy.availabilities.all():
                months.update(HostResponseSchema._month_iter(availability.start_date, availability.end_date))
        return sorted(months)

    @staticmethod
    def resolve_duration_options(obj: Host) -> list[str]:
        """Extract unique expected durations from the host's vacancies."""
        durations: set[str] = set()
        for vacancy in obj.vacancy_set.all():
            if vacancy.expected_duration:
                durations.add(vacancy.expected_duration)
        if not durations and obj.expected_duration:
            durations.add(obj.expected_duration)
        return sorted(durations)

    @staticmethod
    def resolve_keywords(obj: Host) -> list[str]:
        """Extract keywords from meals_offered and other text fields."""
        if not obj.meals_offered:
            return []
        return [part.strip() for part in re.split(r"[,\n;/]+", obj.meals_offered) if part.strip()]


class HostCreateSchema(Schema):
    """Schema for creating a new Host."""

    name: str | None = ""
    description: str | None = ""
    address: str | None = ""
    type: str | None = ""
    phone_number: str | None = ""
    contact_information: str | None = ""
    pocket_money: int | None = 0
    meals_offered: str | None = ""
    dayoffs: str | None = ""
    allowance: str | None = ""
    facilities: str | None = ""
    other: str | None = ""
    expected_duration: str | None = ""
    recruitment_slogan: str | None = ""


class HostUpdateSchema(Schema):
    """Schema for updating Host."""

    name: str | None = None
    description: str | None = None
    type: str | None = None
    address: str | None = None
    phone_number: str | None = None
    contact_information: str | None = None
    pocket_money: int | None = None
    meals_offered: str | None = None
    dayoffs: str | None = None
    allowance: str | None = None
    facilities: str | None = None
    other: str | None = None
    expected_duration: str | None = None
    recruitment_slogan: str | None = None


class HostBriefSchema(ModelSchema):
    """Compact host schema for embedding in vacancy responses."""

    class Meta:
        model = Host
        fields = ("id", "name", "address", "type", "avg_rating", "host_image")


class VacancyAvailabilitySchema(ModelSchema):
    """Schema for Vacancy availability."""

    class Meta:
        model = VacancyAvailability
        fields = ("start_date", "end_date", "capacity", "current_helpers")


class VacancyResponseSchema(ModelSchema):
    """Schema for Vacancy response."""

    availabilities: list[VacancyAvailabilitySchema] = Field(default_factory=list)
    host: HostBriefSchema

    class Meta:
        model = Vacancy
        exclude: typing.ClassVar[tuple[str, ...]] = (
            "updated_at",
            "updated_by_user",
        )


class VacancyCreateSchema(Schema):
    """Schema for creating a new Vacancy."""

    name: str
    work_time: str
    description: str
    expected_duration: str
    expected_age: str
    expected_gender: str
    expected_licenses: str
    expected_personality: str
    expected_other_requirements: str
    other_questions: list[str] = Field(default_factory=list)
    status: str = Vacancy.StatusChoices.RECRUITING
    availabilities: list[dict[str, typing.Any]] = Field(
        default_factory=list
    )  # e.g., [{"start_date": "2023-08-01", "end_date": "2023-08-31", "capacity": 1}]


class VacancyUpdateSchema(Schema):
    """Schema for updating a Vacancy."""

    name: str | None = None
    work_time: str | None = None
    description: str | None = None
    expected_duration: str | None = None
    expected_age: str | None = None
    expected_gender: str | None = None
    expected_licenses: str | None = None
    expected_personality: str | None = None
    expected_other_requirements: str | None = None
    other_questions: list[str] | None = None
    status: str | None = None
    availabilities: list[dict[str, typing.Any]] | None = None


# ---------- Host Review Schemas ----------


class HostReviewCreateSchema(Schema):
    """Schema for creating a HostReview."""

    rating: int = Field(..., ge=1, le=5)
    comment: str = ""
    photos: list[str] = Field(default_factory=list)

    @field_validator("photos")
    @classmethod
    def limit_photos(cls, v: list[str]) -> list[str]:
        """Cap at 5 images (data URLs from the client)."""
        return v[:5]


class HostReviewResponseSchema(ModelSchema):
    """Schema for HostReview response, enriched with reviewer display info."""

    reviewer_id: UUID
    reviewer_name: str = ""
    reviewer_avatar: str | None = None
    photo_urls: list[str] = Field(default_factory=list)

    class Meta:
        model = HostReview
        fields = ("id", "rating", "comment", "created_at")

    @staticmethod
    def resolve_reviewer_id(obj: HostReview) -> UUID:
        """Return reviewer's UUID."""
        return obj.reviewer_id  # type: ignore[return-value]

    @staticmethod
    def resolve_reviewer_name(obj: HostReview) -> str:
        """Return reviewer's display name."""
        return obj.reviewer.username

    @staticmethod
    def resolve_reviewer_avatar(obj: HostReview) -> str | None:
        """Return reviewer's avatar URL from User.avatar (same as helper profile)."""
        user = obj.reviewer
        if user.avatar:
            return user.avatar.url
        return None

    @staticmethod
    def resolve_photo_urls(obj: HostReview) -> list[str]:
        """Return absolute media URLs for review images."""
        return [img.image.url for img in obj.images.all()]


class HostReviewSummarySchema(Schema):
    """Aggregated review statistics for a host."""

    average_rating: float
    total_reviews: int
    distribution: dict[int, int]
    reviews: list[HostReviewResponseSchema]
