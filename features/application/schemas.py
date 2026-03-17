import typing
from datetime import date
from typing import Any
from uuid import UUID

from ninja import ModelSchema, Schema

from features.application.models import Application
from features.helper.schemas import HelperProfileResponseSchema
from features.host.schemas import VacancyResponseSchema


class ApplicationCreateSchema(Schema):
    """Schema for creating an application."""

    vacancy_id: str
    start_date: date
    end_date: date


class ApplicationStatusUpdateSchema(Schema):
    """Schema for updating an application's status."""

    status: str


class ApplicationResponseSchema(ModelSchema):
    """Schema for Application response."""

    id: UUID
    helper: HelperProfileResponseSchema | dict[str, Any] | None = None
    vacancy: VacancyResponseSchema | dict[str, Any] | None = None

    class Meta:
        model = Application
        exclude: typing.ClassVar[tuple[str, ...]] = (
            "created_at",
            "created_by_user",
            "updated_at",
            "updated_by_user",
        )
