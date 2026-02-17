from django.contrib import admin

from features.forum.models import ForumCategory, ForumReply, ForumThread


@admin.register(ForumCategory)
class ForumCategoryAdmin(admin.ModelAdmin):
    """Admin interface for ForumCategory model."""

    list_display = ["name", "order", "created_at"]
    list_editable = ["order"]
    search_fields = ["name", "description"]
    ordering = ["order", "name"]


@admin.register(ForumThread)
class ForumThreadAdmin(admin.ModelAdmin):
    """Admin interface for ForumThread model."""

    list_display = ["title", "author", "category", "created_at"]
    list_filter = ["category", "created_at"]
    search_fields = ["title", "content", "author__email"]
    readonly_fields = ["id", "created_at", "updated_at"]
    date_hierarchy = "created_at"


@admin.register(ForumReply)
class ForumReplyAdmin(admin.ModelAdmin):
    """Admin interface for ForumReply model."""

    list_display = ["thread", "author", "content_preview", "created_at"]
    list_filter = ["created_at"]
    search_fields = ["content", "author__email"]
    readonly_fields = ["id", "created_at", "updated_at"]
    date_hierarchy = "created_at"

    def content_preview(self, obj):
        """Return a preview of the reply content."""
        return obj.content[:50] + "..." if len(obj.content) > 50 else obj.content

    content_preview.short_description = "Content"
