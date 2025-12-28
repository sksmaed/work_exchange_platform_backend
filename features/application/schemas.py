from datetime import date, datetime

from ninja import ModelSchema, Schema

from features.application.models import Application
from features.helper.schemas import HelperResponseSchema


class ApplicationCreateSchema(Schema):
    """Schema for creating a new Application."""

    vacancy_id: str
    start_date: date
    end_date: date


class ApplicationResponseSchema(ModelSchema):
    """Schema for Application response."""

    helper_id: str | None = None
    vacancy_id: str | None = None

    class Meta:
        model = Application
        exclude = [
            "helper",
            "vacancy",
            "created_by_user",
            "updated_at",
            "updated_by_user",
        ]

    @staticmethod
    def resolve_helper_id(obj: Application) -> str:
        """Resolve helper_id from the helper relationship."""
        return str(obj.helper.id)

    @staticmethod
    def resolve_vacancy_id(obj: Application) -> str:
        """Resolve vacancy_id from the vacancy relationship."""
        return str(obj.vacancy.id)


class ApplicationWithDetailsSchema(Schema):
    """Schema for Application with helper and vacancy details."""

    id: str
    status: str
    start_date: date
    end_date: date
    created_at: datetime
    helper: HelperResponseSchema
    vacancy_id: str


class ApplicationStatusUpdateSchema(Schema):
    """Schema for updating application status (accept/reject)."""

    status: str  # "accepted" or "rejected"

