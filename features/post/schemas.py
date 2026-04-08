from datetime import datetime
from uuid import UUID

from ninja import Schema


class UserSimpleResponseSchema(Schema):
    """User simple response schema."""

    id: UUID
    username: str
    email: str


class PostPhotoResponseSchema(Schema):
    """Post photo response schema."""

    id: UUID
    image_url: str
    order: int


class PostResponseSchema(Schema):
    """Post response schema."""

    id: UUID
    host_id: UUID
    content: str
    type: str
    like_count: int
    comment_count: int
    photos: list[PostPhotoResponseSchema]
    is_liked_by_me: bool = False
    created_at: datetime
    updated_at: datetime


class PostListResponseSchema(Schema):
    """Post list response schema."""

    host_id: UUID
    posts: list[PostResponseSchema]
    total: int
    page: int
    page_size: int
    has_next: bool


class AllPostListResponseSchema(Schema):
    """All posts list response schema."""

    posts: list[PostResponseSchema]
    total: int
    page: int
    page_size: int
    has_next: bool


class CommentResponseSchema(Schema):
    """Comment response schema."""

    id: UUID
    post_id: UUID
    user: UserSimpleResponseSchema
    parent_id: UUID | None = None
    content: str
    created_at: datetime


class CommentListResponseSchema(Schema):
    """Comment list response schema."""

    post_id: UUID
    comments: list[CommentResponseSchema]
    total: int
    page: int
    page_size: int
    has_next: bool


class PostLikeResponseSchema(Schema):
    """Post like response schema."""

    post_id: UUID
    like_count: int
    liked: bool


class PostUpdateSchema(Schema):
    """Post update schema."""

    content: str
