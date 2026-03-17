import typing

from ninja import Field, ModelSchema, Schema

from features.host.models import Host, Vacancy, VacancyAvailability


class HostResponseSchema(ModelSchema):
    """Schema for Host response."""

    exclude_children: bool | None = None

    class Meta:
        model = Host
        exclude: typing.ClassVar[tuple[str, ...]] = (
            "updated_at",
            "updated_by_user",
        )


class HostCreateSchema(Schema):
    """Schema for creating a new Host."""

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
    recruitment_slogan: str | None = ""


class HostUpdateSchema(Schema):
    """Schema for updating Host."""

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
    recruitment_slogan: str | None = None


class VacancyAvailabilitySchema(ModelSchema):
    """Schema for Vacancy availability."""

    class Meta:
        model = VacancyAvailability
        fields = ("start_date", "end_date", "capacity", "current_helpers")


class VacancyResponseSchema(ModelSchema):
    """Schema for Vacancy response."""

    availabilities: list[VacancyAvailabilitySchema] = Field(default_factory=list)

    class Meta:
        model = Vacancy
        exclude: typing.ClassVar[tuple[str, ...]] = (
            "updated_at",
            "updated_by_user",
        )


class VacancyCreateSchema(Schema):
    """Schema for creating a new Vacancy."""

    host_id: str
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
