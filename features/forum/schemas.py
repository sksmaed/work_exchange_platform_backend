from datetime import datetime

from ninja import Schema


class UserBasicSchema(Schema):
    """Basic user information schema."""

    id: str
    name: str
    email: str
    avatar: str | None = None


class ForumCategoryResponseSchema(Schema):
    """Schema for forum category response."""

    id: str
    name: str
    description: str
    order: int
    created_at: datetime


class ForumCategoryCreateSchema(Schema):
    """Schema for creating a forum category (admin)."""

    name: str
    description: str = ""
    order: int = 0


class ForumThreadCreateSchema(Schema):
    """Schema for creating a forum thread."""

    title: str
    content: str
    category_id: str | None = None


class ForumThreadUpdateSchema(Schema):
    """Schema for updating a forum thread."""

    title: str | None = None
    content: str | None = None
    category_id: str | None = None


class ForumThreadListResponseSchema(Schema):
    """Schema for thread in list view."""

    id: str
    title: str
    content: str
    author: UserBasicSchema
    category_id: str | None
    category_name: str | None
    reply_count: int
    created_at: datetime


class ForumReplyResponseSchema(Schema):
    """Schema for forum reply response."""

    id: str
    thread_id: str
    author: UserBasicSchema
    content: str
    created_at: datetime


class ForumReplyCreateSchema(Schema):
    """Schema for creating a forum reply."""

    content: str


class ForumReplyUpdateSchema(Schema):
    """Schema for updating a forum reply."""

    content: str


class ForumThreadDetailResponseSchema(Schema):
    """Schema for thread detail with replies."""

    id: str
    title: str
    content: str
    author: UserBasicSchema
    category_id: str | None
    category_name: str | None
    reply_count: int
    replies: list[ForumReplyResponseSchema]
    created_at: datetime


class ForumThreadListPaginatedSchema(Schema):
    """Schema for paginated thread list."""

    items: list[ForumThreadListResponseSchema]
    total: int
    page: int
    page_size: int
    has_next: bool
