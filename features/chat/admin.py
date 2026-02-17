from django.contrib import admin

from features.chat.models import Conversation, Message


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    """Admin interface for Conversation model."""

    list_display = ["id", "participant_1", "participant_2", "last_message_at", "created_at"]
    list_filter = ["created_at", "last_message_at"]
    search_fields = ["participant_1__email", "participant_2__email"]
    readonly_fields = ["id", "created_at", "updated_at"]
    date_hierarchy = "created_at"


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    """Admin interface for Message model."""

    list_display = ["id", "conversation", "sender", "content_preview", "read_at", "created_at"]
    list_filter = ["created_at", "read_at"]
    search_fields = ["sender__email", "content"]
    readonly_fields = ["id", "created_at", "updated_at"]
    date_hierarchy = "created_at"

    def content_preview(self, obj):
        """Return a preview of the message content."""
        return obj.content[:50] + "..." if len(obj.content) > 50 else obj.content

    content_preview.short_description = "Content"
