from datetime import date
from typing import Any

from ninja import ModelSchema, Schema

from features.helper.models import HelperModel


class HelperResponseSchema(ModelSchema):
    """Schema for HelperModel response."""

    class Meta:
        model = HelperModel
        exclude = [
            "created_by_user",
            "updated_at",
            "updated_by_user",
        ]


class HelperCreateSchema(Schema):
    """Schema for creating a new HelperModel."""

    description: str
    birthday: date
    gender: str
    residence: str | None = ""
    expected_place: list[str] | None = None
    expected_time_periods: list[dict[str, Any]] | None = None
    expected_treatments: list[str] | None = None
    personality: str | None = ""
    motivation: str | None = ""
    work_experience: str | None = ""
    hobbies: str | None = ""
    licenses: str | None = "None"
    languages: list[str] | None = None


class HelperUpdateSchema(Schema):
    """Schema for updating HelperModel."""

    description: str | None = None
    birthday: date | None = None
    gender: str | None = None
    residence: str | None = None
    expected_place: list[str] | None = None
    expected_time_periods: list[dict[str, Any]] | None = None
    expected_treatments: list[str] | None = None
    personality: str | None = None
    motivation: str | None = None
    work_experience: str | None = None
    hobbies: str | None = None
    licenses: str | None = None
    languages: list[str] | None = None

