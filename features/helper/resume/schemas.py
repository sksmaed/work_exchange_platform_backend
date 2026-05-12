from typing import Any

from ninja import Schema


class ResumeBase(Schema):
    """Base schema for helper resumes, with all fields optional for flexibility in create/update operations."""

    title: str | None = None
    summary: str | None = None
    experiences: list[str] | None = None
    skills: list[str] | None = None
    certifications: list[str] | None = None
    availability: list[dict[str, Any]] | None = None
    preferred_locations: list[str] | None = None
    contact_email: str | None = None
    contact_phone: str | None = None


class ResumeCreate(ResumeBase):
    """Schema for creating a resume, where all fields are optional."""


class ResumeUpdate(ResumeBase):
    """Schema for updating a resume, where all fields are optional."""


class ResumeOut(ResumeBase):
    """Schema for outputting resume data, including the ID."""

    id: str
