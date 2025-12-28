from ninja import ModelSchema, Schema

from features.host.models import HostModel


class HostResponseSchema(ModelSchema):
    """Schema for HostModel response."""

    exclude_children: bool | None = None

    class Config:
        model = HostModel
        exclude = (
            "updated_at",
            "updated_by_user",
            "is_deleted",
            "deleted_at",
            "deleted_by_user",
        )


class HostCreateSchema(Schema):
    """Schema for creating a new HostModel."""

    description: str
    address: str
    type: str
    contact_information: str | None = ""
    pocket_money: int | None = 0
    meals_offered: str | None = ""
    dayoffs: str | None = ""
    allowance: str | None = ""
    facilities: str | None = ""
    other: str | None = ""
    expected_duration: str | None = ""
    expected_licenses: str | None = "None"
    expected_age: str | None = ""
    expected_gender: str | None = ""
    expected_personality: str | None = ""
    expected_other_requirements: str | None = ""
    recruitment_slogan: str | None = ""


class HostUpdateSchema(Schema):
    """Schema for updating HostModel."""

    description: str | None = None
    type: str | None = None
    address: str | None = None
    contact_information: str | None = None
    pocket_money: int | None = None
    meals_offered: str | None = None
    dayoffs: str | None = None
    allowance: str | None = None
    facilities: str | None = None
    other: str | None = None
    expected_duration: str | None = None
    expected_licenses: str | None = None
    expected_age: str | None = None
    expected_gender: str | None = None
    expected_personality: str | None = None
    expected_other_requirements: str | None = None
    recruitment_slogan: str | None = None
