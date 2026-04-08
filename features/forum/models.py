from typing import ClassVar

from django.db import models

from common.models import BaseModel
from utils.storage import get_model_file_path


class ForumCategory(BaseModel):
    """Model representing a forum category for organizing threads.

    Attributes:
    ----------
    name : CharField
        Name of the category.
    description : TextField
        Description of the category.
    order : IntegerField
        Display order for sorting categories.
    """

    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, default="")
    order = models.IntegerField(default=0)

    class Meta:
        ordering: ClassVar[list[str]] = ["order", "name"]
        verbose_name_plural = "Forum categories"

    def __str__(self) -> str:
        """String representation of the ForumCategory."""
        return self.name


class ForumThread(BaseModel):
    """Model representing a forum discussion thread.

    Attributes:
    ----------
    title : CharField
        Title of the thread.
    content : TextField
        Content/body of the thread.
    author : ForeignKey
        User who created the thread.
    category : ForeignKey
        Optional category this thread belongs to.
    """

    title = models.CharField(max_length=255)
    content = models.TextField()
    author = models.ForeignKey(
        "core.User",
        on_delete=models.CASCADE,
        related_name="forum_threads",
    )
    category = models.ForeignKey(
        ForumCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="threads",
    )
    # Counters
    like_count = models.IntegerField(default=0)

    class Meta:
        ordering: ClassVar[list[str]] = ["-created_at"]
        indexes: ClassVar = [
            models.Index(fields=["category"]),
            models.Index(fields=["-created_at"]),
            models.Index(fields=["author"]),
        ]

    def __str__(self) -> str:
        """String representation of the ForumThread."""
        return self.title


class ForumThreadImage(BaseModel):
    """Image attachment for a forum thread."""

    thread = models.ForeignKey(
        ForumThread,
        on_delete=models.CASCADE,
        related_name="images",
    )
    image = models.ImageField(upload_to=get_model_file_path)

    class Meta:
        ordering: ClassVar[list[str]] = ["created_at"]

    def __str__(self) -> str:
        return f"Image for thread {self.thread_id}"


class ForumReply(BaseModel):
    """Model representing a reply to a forum thread.

    Attributes:
    ----------
    thread : ForeignKey
        The thread this reply belongs to.
    author : ForeignKey
        User who wrote the reply.
    content : TextField
        Content of the reply.
    """

    thread = models.ForeignKey(
        ForumThread,
        on_delete=models.CASCADE,
        related_name="replies",
    )
    author = models.ForeignKey(
        "core.User",
        on_delete=models.CASCADE,
        related_name="forum_replies",
    )
    # Optional parent reply for threaded replies
    parent = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="child_replies",
    )
    # Like counter for replies
    like_count = models.IntegerField(default=0)
    content = models.TextField()

    class Meta:
        ordering: ClassVar[list[str]] = ["created_at"]
        indexes: ClassVar = [
            models.Index(fields=["thread", "created_at"]),
            models.Index(fields=["author"]),
        ]
        verbose_name_plural = "Forum replies"

    def __str__(self) -> str:
        """String representation of the ForumReply."""
        return f"Reply by {self.author} on {self.thread.title}"


class ForumReplyImage(BaseModel):
    """Image attachment for a forum reply."""

    reply = models.ForeignKey(
        ForumReply,
        on_delete=models.CASCADE,
        related_name="images",
    )
    image = models.ImageField(upload_to=get_model_file_path)

    class Meta:
        ordering: ClassVar[list[str]] = ["created_at"]
        verbose_name_plural = "Forum reply images"

    def __str__(self) -> str:
        return f"Image for reply {self.reply_id}"
