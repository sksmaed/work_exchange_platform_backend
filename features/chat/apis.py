from django.core.handlers.wsgi import WSGIRequest
from django.core.paginator import Paginator
from django.db.models import Count, Q, QuerySet
from django.shortcuts import get_object_or_404
from django.utils import timezone
from ninja_extra import api_controller, route
from ninja_extra.permissions import IsAuthenticated

from common.exceptions import Http403ForbiddenException, KeyNotFoundException
from features.chat.exceptions import ConversationNotFoundError, InvalidParticipantError, MessageNotFoundError
from features.chat.models import Conversation, Message
from features.chat.schemas import (
    ConversationCreateSchema,
    ConversationResponseSchema,
    MarkAsReadSchema,
    MessageCreateSchema,
    MessageListResponseSchema,
    MessageResponseSchema,
    UserBasicSchema,
)
from features.core.models import User


@api_controller(prefix_or_class="chat", tags=["chat"], permissions=[IsAuthenticated])
class ChatControllerAPI:
    """API endpoints for managing chat conversations and messages."""

    def _user_to_basic_schema(self, user: User) -> dict:
        """Convert User model to UserBasicSchema dict."""
        return {
            "id": str(user.id),
            "name": user.name or user.email,
            "email": user.email,
            "avatar": user.avatar.url if user.avatar else None,
        }

    def _conversation_to_response(self, conversation: Conversation, current_user: User) -> dict:
        """Convert Conversation model to ConversationResponseSchema dict."""
        # Count unread messages for current user
        unread_count = Message.objects.filter(
            conversation=conversation, read_at__isnull=True
        ).exclude(sender=current_user).count()

        return {
            "id": str(conversation.id),
            "participant_1": self._user_to_basic_schema(conversation.participant_1),
            "participant_2": self._user_to_basic_schema(conversation.participant_2),
            "last_message_at": conversation.last_message_at,
            "created_at": conversation.created_at,
            "unread_count": unread_count,
        }

    def _message_to_response(self, message: Message) -> dict:
        """Convert Message model to MessageResponseSchema dict."""
        return {
            "id": str(message.id),
            "conversation_id": str(message.conversation.id),
            "sender": self._user_to_basic_schema(message.sender),
            "content": message.content,
            "read_at": message.read_at,
            "created_at": message.created_at,
        }

    @route.post("/conversations", response={201: ConversationResponseSchema})
    def create_or_get_conversation(
        self, request: WSGIRequest, data: ConversationCreateSchema
    ) -> dict:
        """Create or get a conversation with another user."""
        user = request.user

        # Get the other participant
        other_user = get_object_or_404(User, id=data.participant_id)

        # Cannot create conversation with yourself
        if user.id == other_user.id:
            raise Http403ForbiddenException("Cannot create a conversation with yourself")

        # Get or create conversation
        conversation, created = Conversation.get_or_create_conversation(user, other_user)

        return self._conversation_to_response(conversation, user)

    @route.get("/conversations", response={200: list[ConversationResponseSchema]})
    def list_conversations(self, request: WSGIRequest) -> list[dict]:
        """List all conversations for the current user."""
        user = request.user

        conversations = Conversation.objects.filter(
            Q(participant_1=user) | Q(participant_2=user)
        ).select_related("participant_1", "participant_2")

        return [self._conversation_to_response(conv, user) for conv in conversations]

    @route.get("/conversations/{conversation_id}/messages", response={200: MessageListResponseSchema})
    def get_conversation_messages(
        self,
        request: WSGIRequest,
        conversation_id: str,
        page: int = 1,
        page_size: int = 50,
    ) -> dict:
        """Get messages in a conversation with pagination."""
        user = request.user

        # Get conversation
        try:
            conversation = Conversation.objects.select_related(
                "participant_1", "participant_2"
            ).get(id=conversation_id)
        except Conversation.DoesNotExist:
            raise KeyNotFoundException(ConversationNotFoundError, conversation_id)

        # Check if user is a participant
        if user not in [conversation.participant_1, conversation.participant_2]:
            raise Http403ForbiddenException("You are not a participant in this conversation")

        # Get messages
        messages = Message.objects.filter(conversation=conversation).select_related("sender").order_by("-created_at")

        # Paginate
        paginator = Paginator(messages, page_size)
        page_obj = paginator.get_page(page)

        # Convert to response schema (reverse to show oldest first on page)
        message_list = [self._message_to_response(msg) for msg in reversed(page_obj.object_list)]

        return {
            "messages": message_list,
            "total": paginator.count,
            "page": page,
            "page_size": page_size,
            "has_next": page_obj.has_next(),
        }

    @route.post("/conversations/{conversation_id}/messages", response={201: MessageResponseSchema})
    def send_message(
        self,
        request: WSGIRequest,
        conversation_id: str,
        data: MessageCreateSchema,
    ) -> dict:
        """Send a message in a conversation."""
        user = request.user

        # Get conversation
        try:
            conversation = Conversation.objects.select_related(
                "participant_1", "participant_2"
            ).get(id=conversation_id)
        except Conversation.DoesNotExist:
            raise KeyNotFoundException(ConversationNotFoundError, conversation_id)

        # Check if user is a participant
        if user not in [conversation.participant_1, conversation.participant_2]:
            raise Http403ForbiddenException("You are not a participant in this conversation")

        # Create message
        message = Message.objects.create(
            conversation=conversation,
            sender=user,
            content=data.content,
        )

        # Update conversation's last_message_at
        conversation.last_message_at = message.created_at
        conversation.save(update_fields=["last_message_at"])

        # Send real-time notification via Channels (if connected)
        self._send_realtime_message(conversation, message, user)

        return self._message_to_response(message)

    @route.patch("/conversations/{conversation_id}/read", response={200: dict})
    def mark_messages_as_read(
        self,
        request: WSGIRequest,
        conversation_id: str,
        data: MarkAsReadSchema,
    ) -> dict:
        """Mark messages as read in a conversation."""
        user = request.user

        # Get conversation
        try:
            conversation = Conversation.objects.get(id=conversation_id)
        except Conversation.DoesNotExist:
            raise KeyNotFoundException(ConversationNotFoundError, conversation_id)

        # Check if user is a participant
        if user not in [conversation.participant_1, conversation.participant_2]:
            raise Http403ForbiddenException("You are not a participant in this conversation")

        # Get unread messages sent by the other user
        unread_messages = Message.objects.filter(
            conversation=conversation,
            read_at__isnull=True,
        ).exclude(sender=user)

        # If specific message IDs provided, filter by them
        if data.message_ids:
            unread_messages = unread_messages.filter(id__in=data.message_ids)

        # Mark as read
        count = unread_messages.update(read_at=timezone.now())

        return {
            "detail": f"{count} message(s) marked as read",
            "count": count,
        }

    @route.delete("/conversations/{conversation_id}", response={200: dict})
    def delete_conversation(self, request: WSGIRequest, conversation_id: str) -> dict:
        """Delete a conversation (soft delete - marks messages as deleted)."""
        user = request.user

        # Get conversation
        try:
            conversation = Conversation.objects.get(id=conversation_id)
        except Conversation.DoesNotExist:
            raise KeyNotFoundException(ConversationNotFoundError, conversation_id)

        # Check if user is a participant
        if user not in [conversation.participant_1, conversation.participant_2]:
            raise Http403ForbiddenException("You are not a participant in this conversation")

        # Delete the conversation
        conversation.delete()

        return {"detail": "Conversation deleted successfully"}

    def _send_realtime_message(self, conversation: Conversation, message: Message, sender: User):
        """Send real-time message notification via Django Channels."""
        try:
            from asgiref.sync import async_to_sync
            from channels.layers import get_channel_layer

            channel_layer = get_channel_layer()
            if channel_layer:
                # Send to conversation group
                async_to_sync(channel_layer.group_send)(
                    f"chat_{conversation.id}",
                    {
                        "type": "chat_message",
                        "message": self._message_to_response(message),
                    },
                )
        except Exception:
            # Fail silently if channels not configured
            pass
