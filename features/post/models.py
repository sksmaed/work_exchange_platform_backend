from typing import ClassVar

from django.db import models

from common.models import BaseModel
from utils.storage import get_model_file_path


class Post(BaseModel):
    """Represents a post published by a host.

    Attributes:
    ----------
    host : ForeignKey
        Reference to the associated host.
    content : TextField
        The text content of the post.
    like_count : IntegerField
        Number of likes the post has received.
    comment_count : IntegerField
        Number of comments on the post.
    """

    host = models.ForeignKey(
        "host.Host",
        on_delete=models.CASCADE,
        related_name="posts",
    )
    content = models.TextField()
    like_count = models.IntegerField(default=0)
    comment_count = models.IntegerField(default=0)

    class Meta:
        ordering: ClassVar[list[str]] = ["-created_at"]
        indexes: ClassVar = [
            models.Index(fields=["host", "-created_at"]),
        ]

    def __str__(self) -> str:
        """Return a string representation of the post."""
        return f"Post by {self.host.name} on {self.created_at.date()}"


class PostPhoto(BaseModel):
    """Represents a photo attached to an post.

    Attributes:
    ----------
    post : ForeignKey
        Reference to the associated post.
    image : ImageField
        The image file of the photo in the post.
    order : IntegerField
        The display order of the photo (lowest first).
    """

    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name="photos",
    )
    image = models.ImageField(
        upload_to=get_model_file_path,
    )
    order = models.IntegerField(
        default=0,
    )

    class Meta:
        ordering: ClassVar[list[str]] = ["order", "created_at"]
        indexes: ClassVar = [
            models.Index(fields=["post", "order", "created_at"]),
        ]

    def __str__(self) -> str:
        """Return a string representation of the photo."""
        return f"Photo {self.id} for post {self.post_id}"


class Comment(BaseModel):
    """Represents a comment on a post by a user.

    Attributes:
    ----------
    post : ForeignKey
        Reference to the associated post.
    user : ForeignKey
        Reference to the associated user who made the comment.
    content : TextField
        The text content of the comment.
    """

    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name="comments",
    )
    user = models.ForeignKey(
        "core.User",
        on_delete=models.CASCADE,
    )
    content = models.TextField()

    class Meta:
        ordering: ClassVar[list[str]] = ["-created_at"]
        indexes: ClassVar = [
            models.Index(fields=["post", "-created_at"]),
        ]

    def __str__(self) -> str:
        """Return a string representation of the comment."""
        return f"Comment by {self.user.username} on post {self.post_id}"


class PostLike(BaseModel):
    """Represents a like on a post by a user.

    Attributes:
    ----------
    post : ForeignKey
        Reference to the associated post.
    user : ForeignKey
        Reference to the associated user who liked the post.
    """

    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name="likes",
    )
    user = models.ForeignKey(
        "core.User",
        on_delete=models.CASCADE,
    )

    class Meta:
        unique_together: ClassVar = ("post", "user")
        indexes: ClassVar = [models.Index(fields=["post", "user"])]

    def __str__(self) -> str:
        """Return a string representation of the like."""
        return f"Like by {self.user.username} on post {self.post_id}"
