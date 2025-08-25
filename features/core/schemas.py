from typing import Optional

from ninja import Schema


class UserProfileSchema(Schema):
    """Schema for user profile data in business operations."""

    id: str
    email: str
    name: Optional[str]
    username: str
    avatar: Optional[str]


class UpdateUserProfileSchema(Schema):
    """Schema for updating user profile information."""

    name: Optional[str] = None
    username: Optional[str] = None

