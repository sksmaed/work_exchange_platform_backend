from datetime import date, datetime
from typing import Any
from uuid import UUID

from ninja import Field, Schema
from pydantic import model_validator


class TimePeriodSchema(Schema):
    """Schema representing a generic time period."""

    start_date: date
    end_date: date

    @model_validator(mode="after")
    def validate_dates(self) -> "TimePeriodSchema":
        """Ensure start_date is not after end_date."""
        if self.start_date > self.end_date:
            raise ValueError("start_date cannot be after end_date")
        return self


class HelperProfileCreateSchema(Schema):
    """Schema for creating a helper profile."""

    description: str
    birthday: date
    gender: str
    residence: str | None = ""
    expected_place: list[str] | None = None
    expected_time_periods: list[TimePeriodSchema] | None = None
    expected_treatments: list[str] | None = None
    personality: str | None = ""
    motivation: str | None = ""
    hobbies: str | None = ""
    licenses: str | None = "None"
    languages: list[str] | None = None

    @model_validator(mode="after")
    def validate_time_periods(self) -> "HelperProfileCreateSchema":
        """Validate that only a single continuous time period is selected."""
        if self.expected_time_periods and len(self.expected_time_periods) > 1:
            raise ValueError("Helpers can only select a single continuous time period.")
        return self


class HelperProfileUpdateSchema(Schema):
    """Schema for updating a helper profile."""

    description: str | None = None
    birthday: date | None = None
    gender: str | None = None
    residence: str | None = None
    expected_place: list[str] | None = None
    expected_time_periods: list[TimePeriodSchema] | None = None
    expected_treatments: list[str] | None = None
    personality: str | None = None
    motivation: str | None = None
    hobbies: str | None = None
    licenses: str | None = None
    languages: list[str] | None = None

    @model_validator(mode="after")
    def validate_time_periods(self) -> "HelperProfileUpdateSchema":
        """Validate that only a single continuous time period is selected."""
        if self.expected_time_periods and len(self.expected_time_periods) > 1:
            raise ValueError("Helpers can only select a single continuous time period.")
        return self


class HelperPhotoResponseSchema(Schema):
    """Schema for a single helper photo."""

    id: UUID
    image_url: str | None = None
    order: int
    created_at: datetime


class HelperProfileResponseSchema(Schema):
    """Schema for the helper profile response."""

    id: UUID
    user_id: UUID | None = None
    description: str
    birthday: date
    gender: str | None = None
    residence: str
    expected_place: list[str]
    expected_time_periods: list[dict[str, Any]]
    expected_treatments: list[str]
    personality: str
    motivation: str
    hobbies: str
    licenses: str
    languages: list[str]
    avg_rating: float
    avatar_url: str | None = None
    photos: list[HelperPhotoResponseSchema] = Field(default_factory=list)


class HelperPhotoUploadResponseSchema(Schema):
    """Schema for helper photo upload response."""

    image_urls: list[str]
