import json
import logging

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer

from features.chat.models import Conversation

logger = logging.getLogger(__name__)


class ChatConsumer(AsyncWebsocketConsumer):
    """WebSocket consumer for handling real-time chat messages."""

    async def connect(self) -> None:
        """Handle WebSocket connection."""
        try:
            user = self.scope["user"]
            self.conversation_id = self.scope["url_route"]["kwargs"]["conversation_id"]

            if not user.is_authenticated:
                await self.close()
                return

            is_participant = await self._check_participant(user, self.conversation_id)
            if not is_participant:
                await self.close()
                return

            self.room_group_name = f"chat_{self.conversation_id}"
            await self.channel_layer.group_add(self.room_group_name, self.channel_name)

            await self.accept()
        except Exception:
            logger.exception("Error during WebSocket connect for conversation %s", getattr(self, "conversation_id", "unknown"))
            await self.close()

    async def disconnect(self, _close_code: int) -> None:
        """Handle WebSocket disconnection."""
        if hasattr(self, "room_group_name"):
            await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data: str) -> None:
        """Handle incoming WebSocket messages."""
        try:
            data = json.loads(text_data)
            message_type = data.get("type")

            if message_type == "typing":
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        "type": "typing_indicator",
                        "user_id": str(self.scope["user"].id),
                        "is_typing": data.get("is_typing", False),
                    },
                )
            elif message_type == "read_receipt":
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        "type": "read_receipt",
                        "message_ids": data.get("message_ids", []),
                        "user_id": str(self.scope["user"].id),
                    },
                )
        except Exception:
            logger.exception("Error handling WebSocket message in conversation %s", getattr(self, "conversation_id", "unknown"))

    async def chat_message(self, event: dict) -> None:
        """Handle chat message event from group send."""
        await self.send(text_data=json.dumps({
            "type": "message",
            "message": event["message"],
        }))

    async def typing_indicator(self, event: dict) -> None:
        """Handle typing indicator event."""
        if str(self.scope["user"].id) != event["user_id"]:
            await self.send(text_data=json.dumps({
                "type": "typing",
                "user_id": event["user_id"],
                "is_typing": event["is_typing"],
            }))

    async def read_receipt(self, event: dict) -> None:
        """Handle read receipt event."""
        if str(self.scope["user"].id) != event["user_id"]:
            await self.send(text_data=json.dumps({
                "type": "read_receipt",
                "message_ids": event["message_ids"],
                "user_id": event["user_id"],
            }))

    @database_sync_to_async
    def _check_participant(self, user, conversation_id: str) -> bool:
        """Check if user is a participant in the conversation."""
        try:
            conversation = Conversation.objects.get(id=conversation_id)
            return user in [conversation.participant_1, conversation.participant_2]
        except Conversation.DoesNotExist:
            return False
