from datetime import datetime

from ninja import ModelSchema, Schema


class ConversationCreateSchema(Schema):
    """Schema for creating or getting a conversation."""

    participant_id: str


class UserBasicSchema(Schema):
    """Basic user information schema."""

    id: str
    name: str
    email: str
    avatar: str | None = None


class ConversationResponseSchema(Schema):
    """Schema for conversation response."""

    id: str
    participant_1: UserBasicSchema
    participant_2: UserBasicSchema
    last_message_at: datetime | None
    created_at: datetime
    unread_count: int = 0


class MessageCreateSchema(Schema):
    """Schema for creating a new message."""

    content: str


class MessageResponseSchema(Schema):
    """Schema for message response."""

    id: str
    conversation_id: str
    sender: UserBasicSchema
    content: str
    read_at: datetime | None
    created_at: datetime


class MessageListResponseSchema(Schema):
    """Schema for paginated message list response."""

    messages: list[MessageResponseSchema]
    total: int
    page: int
    page_size: int
    has_next: bool


class MarkAsReadSchema(Schema):
    """Schema for marking messages as read."""

    message_ids: list[str] | None = None  # If None, mark all messages in conversation as read
