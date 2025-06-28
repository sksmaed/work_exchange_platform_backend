import json
import traceback
from typing import Any

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer


class NotificationConsumer(AsyncWebsocketConsumer):
    """WebSocket consumer for handling notifications."""

    @database_sync_to_async
    def _get_user_groups(self, user) -> list:  # noqa: ANN001
        """Retrieve groups for the authenticated user."""
        if user.is_authenticated:
            return list(user.groups.all())
        return []

    async def connect(self):
        """Handle WebSocket connection."""
        try:
            user = self.scope["user"]

            if user.is_authenticated:
                await self.channel_layer.group_add(f"user_{user.id}", self.channel_name)

                groups = await self._get_user_groups(user)
                for group in groups:
                    await self.channel_layer.group_add(f"group_{group.id}", self.channel_name)

            await self.accept()
        except Exception as _:
            traceback.print_exc()
            await self.close()

    async def disconnect(self, code: int):  # noqa: ARG002
        """Handle WebSocket disconnection."""
        user = self.scope["user"]
        if user.is_authenticated:
            await self.channel_layer.group_discard(f"user_{user.id}", self.channel_name)

            groups = await self._get_user_groups(user)
            for group in groups:
                await self.channel_layer.group_discard(f"group_{group.id}", self.channel_name)

    async def notify(self, event: dict[str, Any]):
        """Handle incoming notifications."""
        await self.send(text_data=json.dumps({"title": event["title"], "message": event["message"]}))
