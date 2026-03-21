from django.contrib import admin

from features.post.models import Comment, Post, PostLike, PostPhoto


class PostPhotoInline(admin.TabularInline):
    """Inline for PostPhoto model."""

    model = PostPhoto
    extra = 1


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    """Admin interface for Post model."""

    MAX_CONTENT_LENGTH = 50

    list_display = ("id", "host", "content_snippet", "like_count", "comment_count", "created_at")
    list_filter = ("created_at",)
    search_fields = ("host__name", "content")
    inlines = (PostPhotoInline,)
    readonly_fields = ("like_count", "comment_count", "created_at", "updated_at")

    def content_snippet(self, obj: Post) -> str:
        """Return a snippet of the post content."""
        return obj.content[: self.MAX_CONTENT_LENGTH] + ("..." if len(obj.content) > self.MAX_CONTENT_LENGTH else "")

    content_snippet.short_description = "Content Snippet"


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    """Admin interface for Comment model."""

    MAX_CONTENT_LENGTH = 50

    list_display = ("id", "post", "user", "content_snippet", "created_at")
    list_filter = ("created_at",)
    search_fields = ("user__username", "content", "post__host__name")
    readonly_fields = ("created_at", "updated_at")

    def content_snippet(self, obj: Comment) -> str:
        """Return a snippet of the comment content."""
        return obj.content[: self.MAX_CONTENT_LENGTH] + ("..." if len(obj.content) > self.MAX_CONTENT_LENGTH else "")


@admin.register(PostLike)
class PostLikeAdmin(admin.ModelAdmin):
    """Admin interface for PostLike model."""

    list_display = ("id", "post", "user", "created_at")
    list_filter = ("created_at",)
    search_fields = ("user__username", "post__host__name")
    readonly_fields = ("created_at", "updated_at")
