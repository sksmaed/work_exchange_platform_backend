from typing import Any

from ninja import Schema


class ResumeBase(Schema):
    title: str | None = None
    summary: str | None = None
    experiences: list[dict[str, Any]] | None = None
    skills: list[str] | None = None
    certifications: list[str] | None = None
    availability: list[dict[str, Any]] | None = None
    preferred_locations: list[str] | None = None
    contact_email: str | None = None
    contact_phone: str | None = None


class ResumeCreate(ResumeBase):
    pass


class ResumeUpdate(ResumeBase):
    pass


class ResumeOut(ResumeBase):
    id: str 