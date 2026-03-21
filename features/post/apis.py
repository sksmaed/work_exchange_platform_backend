from typing import TYPE_CHECKING, ClassVar

from django.core.exceptions import ValidationError
from django.core.handlers.wsgi import WSGIRequest
from django.core.paginator import Paginator
from django.db import transaction
from django.shortcuts import get_object_or_404
from ninja import File, Form, UploadedFile
from ninja_extra import api_controller, route
from ninja_extra.permissions import IsAuthenticated

from common.exceptions import Http403ForbiddenException
from features.core.models import User
from features.host.models import Host
from features.post.exceptions import CommentNotFoundError, PostInvalidImageError, PostNotFoundError
from features.post.models import Comment, Post, PostLike, PostPhoto
from features.post.schemas import (
    CommentListResponseSchema,
    CommentResponseSchema,
    PostLikeResponseSchema,
    PostListResponseSchema,
    PostPhotoResponseSchema,
    PostResponseSchema,
    PostUpdateSchema,
    UserSimpleResponseSchema,
)

if TYPE_CHECKING:
    from django.db.models import QuerySet

ALLOWED_IMAGE_TYPES = ("image/jpeg", "image/png", "image/gif", "image/webp")


def _is_host_owner(request_user: User, host: Host) -> bool:
    return host.user_id == request_user.id


def _transform_post_response(post: Post, request_user: User | None) -> PostResponseSchema:
    photos = [
        PostPhotoResponseSchema(id=photo.id, image_url=photo.image.url, order=photo.order)
        for photo in post.photos.all()
    ]
    is_liked_by_me = False
    if request_user and request_user.is_authenticated:
        is_liked_by_me = post.likes.filter(user=request_user).exists()

    return PostResponseSchema(
        id=post.id,
        host_id=post.host_id,
        content=post.content,
        like_count=post.like_count,
        comment_count=post.comment_count,
        photos=photos,
        is_liked_by_me=is_liked_by_me,
        created_at=post.created_at,
        updated_at=post.updated_at,
    )


@api_controller("/hosts", tags=["post"])
class HostPostControllerAPI:
    """API endpoints for host post operations."""

    MAX_PAGE_SIZE: ClassVar[int] = 100

    @route.post("/{host_id}/posts", permissions=[IsAuthenticated])
    def create_post(
        self,
        request: WSGIRequest,
        host_id: str,
        content: str = Form(...),
        images: list[UploadedFile] | None = File(None),
    ) -> dict[str, str | PostResponseSchema]:
        """Create a post for the host."""
        host = get_object_or_404(Host, id=host_id)
        if not _is_host_owner(request.user, host):
            raise Http403ForbiddenException("Only the host owner can perform this action")

        images = images or []
        for image in images:
            if image.content_type not in ALLOWED_IMAGE_TYPES:
                raise PostInvalidImageError("Unsupported image type")

        with transaction.atomic():
            post = Post(host=host, content=content)
            post.save(user=request.user)

            for index, image in enumerate(images):
                photo = PostPhoto(post=post, image=image, order=index)
                photo.save(user=request.user)

        # Prefetch photos for response
        post = Post.objects.prefetch_related("photos").get(id=post.id)
        return {"data": _transform_post_response(post, request.user)}

    @route.get("/{host_id}/posts")
    def list_posts(
        self,
        request: WSGIRequest,
        host_id: str,
        page: int = 1,
        page_size: int = 20,
    ) -> PostListResponseSchema:
        """List posts for a host."""
        host = get_object_or_404(Host, id=host_id)
        page_size = min(page_size, self.MAX_PAGE_SIZE)

        queryset: QuerySet[Post] = Post.objects.filter(host=host).prefetch_related("photos")
        paginator = Paginator(queryset, page_size)
        page_obj = paginator.get_page(page)

        posts = [_transform_post_response(post, request.user) for post in page_obj.object_list]
        return PostListResponseSchema(
            host_id=host.id,
            posts=posts,
            total=paginator.count,
            page=page,
            page_size=page_size,
            has_next=page_obj.has_next(),
        )


@api_controller("/posts", tags=["post"])
class PostActionControllerAPI:
    """API endpoints for specific post interactions."""

    MAX_PAGE_SIZE: ClassVar[int] = 100

    @route.get("/{post_id}")
    def get_post(self, request: WSGIRequest, post_id: str) -> dict[str, PostResponseSchema]:
        """Get a post by ID."""
        try:
            post = Post.objects.prefetch_related("photos").get(id=post_id)
        except (Post.DoesNotExist, ValidationError):
            raise PostNotFoundError
        return {"data": _transform_post_response(post, request.user)}

    @route.patch("/{post_id}", permissions=[IsAuthenticated])
    def update_post(
        self,
        request: WSGIRequest,
        post_id: str,
        payload: PostUpdateSchema,
    ) -> dict[str, PostResponseSchema]:
        """Update a post's content."""
        try:
            post = Post.objects.prefetch_related("photos").get(id=post_id)
        except (Post.DoesNotExist, ValidationError):
            raise PostNotFoundError

        if not _is_host_owner(request.user, post.host):
            raise Http403ForbiddenException("Only the host owner can perform this action")

        post.content = payload.content
        post.save(user=request.user)
        return {"data": _transform_post_response(post, request.user)}

    @route.delete("/{post_id}", permissions=[IsAuthenticated])
    def delete_post(self, request: WSGIRequest, post_id: str) -> dict[str, str]:
        """Delete a post."""
        try:
            post = Post.objects.get(id=post_id)
        except (Post.DoesNotExist, ValidationError):
            raise PostNotFoundError

        if not _is_host_owner(request.user, post.host):
            raise Http403ForbiddenException("Only the host owner can perform this action")

        post.delete()
        return {"message": "Post deleted successfully"}

    @route.post("/{post_id}/comments", permissions=[IsAuthenticated])
    def create_comment(
        self, request: WSGIRequest, post_id: str, content: str = Form(...)
    ) -> dict[str, CommentResponseSchema]:
        """Create a comment on a post."""
        try:
            post = Post.objects.get(id=post_id)
        except (Post.DoesNotExist, ValidationError):
            raise PostNotFoundError

        with transaction.atomic():
            comment = Comment(post=post, user=request.user, content=content)
            comment.save(user=request.user)
            post.comment_count += 1
            post.save(user=request.user)

        user_schema = UserSimpleResponseSchema(
            id=request.user.id, username=request.user.username, email=request.user.email
        )
        return {
            "data": CommentResponseSchema(
                id=comment.id,
                post_id=post.id,
                user=user_schema,
                content=comment.content,
                created_at=comment.created_at,
            )
        }

    @route.get("/{post_id}/comments")
    def list_comments(
        self,
        request: WSGIRequest,  # noqa: ARG002
        post_id: str,
        page: int = 1,
        page_size: int = 20,
    ) -> CommentListResponseSchema:
        """List comments for a post."""
        try:
            post = Post.objects.get(id=post_id)
        except (Post.DoesNotExist, ValidationError):
            raise PostNotFoundError

        page_size = min(page_size, self.MAX_PAGE_SIZE)

        queryset: QuerySet[Comment] = Comment.objects.filter(post=post).select_related("user")
        paginator = Paginator(queryset, page_size)
        page_obj = paginator.get_page(page)

        comments = [
            CommentResponseSchema(
                id=c.id,
                post_id=c.post_id,
                user=UserSimpleResponseSchema(id=c.user.id, username=c.user.username, email=c.user.email),
                content=c.content,
                created_at=c.created_at,
            )
            for c in page_obj.object_list
        ]

        return CommentListResponseSchema(
            post_id=post.id,
            comments=comments,
            total=paginator.count,
            page=page,
            page_size=page_size,
            has_next=page_obj.has_next(),
        )

    @route.delete("/{post_id}/comments/{comment_id}", permissions=[IsAuthenticated])
    def delete_comment(self, request: WSGIRequest, post_id: str, comment_id: str) -> dict[str, str]:
        """Delete a comment from a post."""
        try:
            post = Post.objects.get(id=post_id)
        except (Post.DoesNotExist, ValidationError):
            raise PostNotFoundError

        try:
            comment = Comment.objects.get(id=comment_id, post=post)
        except (Comment.DoesNotExist, ValidationError):
            raise CommentNotFoundError

        is_comment_owner = comment.user_id == request.user.id
        is_host_owner = _is_host_owner(request.user, post.host)

        if not (is_comment_owner or is_host_owner):
            raise Http403ForbiddenException("Only the comment owner or host owner can perform this action")

        with transaction.atomic():
            comment.delete()
            post.comment_count -= 1
            post.save(user=request.user)

        return {"message": "Comment deleted successfully"}

    @route.post("/{post_id}/likes", permissions=[IsAuthenticated])
    def toggle_like(self, request: WSGIRequest, post_id: str) -> dict[str, PostLikeResponseSchema]:
        """Toggle like status on a post."""
        try:
            post = Post.objects.get(id=post_id)
        except (Post.DoesNotExist, ValidationError):
            raise PostNotFoundError

        liked = False
        with transaction.atomic():
            try:
                # Attempt to retrieve and delete the like
                like = PostLike.objects.get(post=post, user=request.user)
                like.delete()
                post.like_count -= 1
                liked = False
            except PostLike.DoesNotExist:
                # If it doesn't exist, create it
                like = PostLike(post=post, user=request.user)
                like.save(user=request.user)
                post.like_count += 1
                liked = True
            post.save(user=request.user)

        return {
            "data": PostLikeResponseSchema(
                post_id=post.id,
                like_count=post.like_count,
                liked=liked,
            )
        }
