from typing import ClassVar

from django.db import models
from django.db.models import Q

from common.models import BaseModel


class Conversation(BaseModel):
    """Model representing a conversation between two users.

    Attributes:
    ----------
    participant_1 : ForeignKey
        First participant in the conversation.
    participant_2 : ForeignKey
        Second participant in the conversation.
    last_message_at : DateTimeField
        Timestamp of the last message in the conversation.
    """

    participant_1 = models.ForeignKey(
        "core.User",
        on_delete=models.CASCADE,
        related_name="conversations_as_participant_1",
    )
    participant_2 = models.ForeignKey(
        "core.User",
        on_delete=models.CASCADE,
        related_name="conversations_as_participant_2",
    )
    last_message_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering: ClassVar[list[str]] = ["-last_message_at", "-created_at"]
        indexes: ClassVar = [
            models.Index(fields=["participant_1", "participant_2"]),
            models.Index(fields=["-last_message_at"]),
        ]

    def __str__(self) -> str:
        """String representation of the Conversation."""
        return f"Conversation({self.participant_1.email} <-> {self.participant_2.email})"

    def get_other_participant(self, user):
        """Get the other participant in the conversation."""
        return self.participant_2 if self.participant_1 == user else self.participant_1

    @classmethod
    def get_or_create_conversation(cls, user1, user2):
        """Get or create a conversation between two users.

        Args:
            user1: First user
            user2: Second user

        Returns:
            Tuple of (conversation, created)
        """
        # Ensure consistent ordering to prevent duplicates
        if user1.id > user2.id:
            user1, user2 = user2, user1

        conversation = cls.objects.filter(
            Q(participant_1=user1, participant_2=user2) | Q(participant_1=user2, participant_2=user1)
        ).first()

        if conversation:
            return conversation, False

        conversation = cls.objects.create(participant_1=user1, participant_2=user2)
        return conversation, True


class Message(BaseModel):
    """Model representing a message in a conversation.

    Attributes:
    ----------
    conversation : ForeignKey
        Reference to the conversation this message belongs to.
    sender : ForeignKey
        User who sent the message.
    content : TextField
        Content of the message.
    read_at : DateTimeField
        Timestamp when the message was read by the recipient.
    """

    conversation = models.ForeignKey(
        Conversation,
        on_delete=models.CASCADE,
        related_name="messages",
    )
    sender = models.ForeignKey(
        "core.User",
        on_delete=models.CASCADE,
        related_name="sent_messages",
    )
    content = models.TextField()
    read_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering: ClassVar[list[str]] = ["created_at"]
        indexes: ClassVar = [
            models.Index(fields=["conversation", "created_at"]),
            models.Index(fields=["sender"]),
        ]

    def __str__(self) -> str:
        """String representation of the Message."""
        return f"Message({self.sender.email} in {self.conversation.id})"

    def mark_as_read(self):
        """Mark the message as read."""
        if not self.read_at:
            from django.utils import timezone

            self.read_at = timezone.now()
            self.save(update_fields=["read_at"])
