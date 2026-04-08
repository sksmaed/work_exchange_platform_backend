from django.core.handlers.wsgi import WSGIRequest
from django.core.paginator import Paginator
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404
from ninja import File, UploadedFile
from ninja_extra import api_controller, route
from ninja_extra.permissions import AllowAny, IsAuthenticated

from common.exceptions import (
    ErrorDetail,
    Http400BadRequestException,
    Http403ForbiddenException,
    KeyNotFoundException,
)
from features.core.models import User
from features.forum.exceptions import (
    ForumInvalidImageError,
    ForumReplyImageNotFoundError,
    ForumReplyNotFoundError,
    ForumThreadImageNotFoundError,
    ForumThreadNotFoundError,
)
from features.forum.models import (
    ForumCategory,
    ForumReply,
    ForumReplyImage,
    ForumThread,
    ForumThreadImage,
)
from features.forum.schemas import (
    ForumCategoryResponseSchema,
    ForumImageUploadResponseSchema,
    ForumReplyCreateSchema,
    ForumReplyResponseSchema,
    ForumReplyUpdateSchema,
    ForumThreadCreateSchema,
    ForumThreadDetailResponseSchema,
    ForumThreadListPaginatedSchema,
    ForumThreadListResponseSchema,
    ForumThreadUpdateSchema,
    UserBasicSchema,
)


@api_controller(prefix_or_class="forum", tags=["forum"])
class ForumControllerAPI:
    """API endpoints for forum categories, threads, and replies."""

    ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/gif", "image/webp"}
    MAX_PAGE_SIZE = 100

    def _user_to_basic_schema(self, user: User) -> dict:
        """Convert User model to UserBasicSchema dict."""
        return {
            "id": str(user.id),
            "name": user.name or user.email,
            "email": user.email,
            "avatar": user.avatar.url if user.avatar else None,
        }

    def _thread_image_urls(self, thread: ForumThread) -> list[str]:
        """Get image URLs for a thread."""
        return [img.image.url for img in thread.images.all() if img.image]

    def _reply_image_urls(self, reply: ForumReply) -> list[str]:
        """Get image URLs for a reply."""
        return [img.image.url for img in reply.images.all() if img.image]

    def _thread_response(self, thread: ForumThread, replies: list[ForumReply] | None = None) -> dict:
        """Build thread detail response dict."""
        replies = replies or list(
            thread.replies.select_related("author")
            .prefetch_related("images")
            .order_by("created_at")
        )
        return {
            "id": str(thread.id),
            "title": thread.title,
            "content": thread.content,
            "author": self._user_to_basic_schema(thread.author),
            "category_id": str(thread.category_id) if thread.category_id else None,
            "category_name": thread.category.name if thread.category else None,
            "reply_count": len(replies),
            "like_count": getattr(thread, "like_count", 0),
            "image_urls": self._thread_image_urls(thread),
            "replies": [
                {
                    "id": str(r.id),
                    "thread_id": str(r.thread_id),
                    "author": self._user_to_basic_schema(r.author),
                    "content": r.content,
                    "parent_id": str(r.parent_id) if r.parent_id else None,
                    "like_count": getattr(r, "like_count", 0),
                    "image_urls": self._reply_image_urls(r),
                    "created_at": r.created_at,
                }
                for r in replies
            ],
            "created_at": thread.created_at,
        }

    @route.get("/categories", response={200: list[ForumCategoryResponseSchema]}, auth=None, permissions=[AllowAny])
    def list_categories(self, request: WSGIRequest) -> list[dict]:
        """List all forum categories (public)."""
        categories = ForumCategory.objects.all()
        return [
            {
                "id": str(c.id),
                "name": c.name,
                "description": c.description,
                "order": c.order,
                "created_at": c.created_at,
            }
            for c in categories
        ]

    @route.get("/threads", response={200: ForumThreadListPaginatedSchema}, auth=None, permissions=[AllowAny])
    def list_threads(
        self,
        request: WSGIRequest,
        page: int = 1,
        page_size: int = 20,
        category_id: str | None = None,
        search: str | None = None,
    ) -> dict:
        """List forum threads with pagination (public)."""
        page_size = min(page_size, self.MAX_PAGE_SIZE)
        queryset = (
            ForumThread.objects.select_related("author", "category")
            .prefetch_related("images")
            .annotate(reply_count=Count("replies"))
        )

        if category_id:
            queryset = queryset.filter(category_id=category_id)
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) | Q(content__icontains=search)
            )

        queryset = queryset.order_by("-created_at")
        paginator = Paginator(queryset, page_size)
        page_obj = paginator.get_page(page)

        items = [
            {
                "id": str(t.id),
                "title": t.title,
                "content": t.content[:200] + "..." if len(t.content) > 200 else t.content,
                "author": self._user_to_basic_schema(t.author),
                "category_id": str(t.category_id) if t.category_id else None,
                "category_name": t.category.name if t.category else None,
                    "reply_count": t.reply_count,
                    "like_count": getattr(t, "like_count", 0),
                "image_urls": self._thread_image_urls(t),
                "created_at": t.created_at,
            }
            for t in page_obj.object_list
        ]

        return {
            "items": items,
            "total": paginator.count,
            "page": page,
            "page_size": page_size,
            "has_next": page_obj.has_next(),
        }

    @route.get("/threads/{thread_id}", response={200: ForumThreadDetailResponseSchema}, auth=None, permissions=[AllowAny])
    def get_thread(self, request: WSGIRequest, thread_id: str) -> dict:
        """Get a thread with its replies (public)."""
        try:
            thread = (
                ForumThread.objects.select_related("author", "category")
                .prefetch_related("images")
                .get(id=thread_id)
            )
        except ForumThread.DoesNotExist:
            raise KeyNotFoundException(ForumThreadNotFoundError, thread_id)

        replies = (
            ForumReply.objects.filter(thread=thread)
            .select_related("author")
            .prefetch_related("images")
            .order_by("created_at")
        )
        return self._thread_response(thread, list(replies))

    @route.post("/threads", response={201: ForumThreadDetailResponseSchema}, permissions=[IsAuthenticated])
    def create_thread(self, request: WSGIRequest, data: ForumThreadCreateSchema) -> dict:
        """Create a new forum thread."""
        user = request.user

        category = None
        if data.category_id:
            category = get_object_or_404(ForumCategory, id=data.category_id)

        thread = ForumThread(
            title=data.title,
            content=data.content,
            author=user,
            category=category,
        )
        thread.save(user=user)

        return self._thread_response(thread, [])

    @route.patch("/threads/{thread_id}", response={200: ForumThreadDetailResponseSchema}, permissions=[IsAuthenticated])
    def update_thread(
        self, request: WSGIRequest, thread_id: str, data: ForumThreadUpdateSchema
    ) -> dict:
        """Update a forum thread (author only)."""
        user = request.user

        try:
            thread = (
                ForumThread.objects.select_related("author", "category")
                .prefetch_related("images")
                .get(id=thread_id)
            )
        except ForumThread.DoesNotExist:
            raise KeyNotFoundException(ForumThreadNotFoundError, thread_id)

        if thread.author != user:
            raise Http403ForbiddenException("Only the author can update this thread")

        update_data = data.model_dump(exclude_unset=True)
        update_fields = []

        if "category_id" in update_data:
            cat_id = update_data.pop("category_id")
            thread.category = get_object_or_404(ForumCategory, id=cat_id) if cat_id else None
            update_fields.append("category")

        for field, value in update_data.items():
            setattr(thread, field, value)
            update_fields.append(field)

        thread.save(user=user, update_fields=update_fields if update_fields else None)

        replies = (
            ForumReply.objects.filter(thread=thread)
            .select_related("author")
            .prefetch_related("images")
            .order_by("created_at")
        )
        return self._thread_response(thread, list(replies))

    @route.delete("/threads/{thread_id}", response={200: dict}, permissions=[IsAuthenticated])
    def delete_thread(self, request: WSGIRequest, thread_id: str) -> dict:
        """Delete a forum thread (author only)."""
        user = request.user

        try:
            thread = ForumThread.objects.get(id=thread_id)
        except ForumThread.DoesNotExist:
            raise KeyNotFoundException(ForumThreadNotFoundError, thread_id)

        if thread.author != user:
            raise Http403ForbiddenException("Only the author can delete this thread")

        thread.delete()
        return {"detail": "Thread deleted successfully"}

    @route.post(
        "/threads/{thread_id}/replies",
        response={201: ForumReplyResponseSchema},
        permissions=[IsAuthenticated],
    )
    def create_reply(
        self, request: WSGIRequest, thread_id: str, data: ForumReplyCreateSchema
    ) -> dict:
        """Create a reply to a thread."""
        user = request.user

        thread = get_object_or_404(ForumThread, id=thread_id)
        # If parent_id provided, validate it and that it belongs to the same thread
        parent = None
        if getattr(data, "parent_id", None):
            try:
                parent = ForumReply.objects.get(id=data.parent_id)
            except ForumReply.DoesNotExist:
                raise KeyNotFoundException(ForumReplyNotFoundError, data.parent_id)
            if parent.thread_id != thread.id:
                # Parent must belong to same thread
                raise Http400BadRequestException([ErrorDetail(ForumReplyNotFoundError, {"message": "Parent reply not found in this thread"})])

        reply = ForumReply(thread=thread, author=user, content=data.content, parent=parent)
        reply.save(user=user)

        return {
            "id": str(reply.id),
            "thread_id": str(reply.thread_id),
            "author": self._user_to_basic_schema(reply.author),
            "parent_id": str(reply.parent_id) if reply.parent_id else None,
            "content": reply.content,
            "image_urls": self._reply_image_urls(reply),
            "created_at": reply.created_at,
        }

    @route.patch(
        "/replies/{reply_id}",
        response={200: ForumReplyResponseSchema},
        permissions=[IsAuthenticated],
    )
    def update_reply(
        self, request: WSGIRequest, reply_id: str, data: ForumReplyUpdateSchema
    ) -> dict:
        """Update a reply (author only)."""
        user = request.user

        try:
            reply = ForumReply.objects.select_related("author").get(id=reply_id)
        except ForumReply.DoesNotExist:
            raise KeyNotFoundException(ForumReplyNotFoundError, reply_id)

        if reply.author != user:
            raise Http403ForbiddenException("Only the author can update this reply")

        if data.content is not None:
            reply.content = data.content
            reply.save(user=user, update_fields=["content"])

        return {
            "id": str(reply.id),
            "thread_id": str(reply.thread_id),
            "author": self._user_to_basic_schema(reply.author),
            "content": reply.content,
            "image_urls": self._reply_image_urls(reply),
            "created_at": reply.created_at,
        }

    @route.delete("/replies/{reply_id}", response={200: dict}, permissions=[IsAuthenticated])
    def delete_reply(self, request: WSGIRequest, reply_id: str) -> dict:
        """Delete a reply (author only)."""
        user = request.user

        try:
            reply = ForumReply.objects.get(id=reply_id)
        except ForumReply.DoesNotExist:
            raise KeyNotFoundException(ForumReplyNotFoundError, reply_id)

        if reply.author != user:
            raise Http403ForbiddenException("Only the author can delete this reply")

        reply.delete()
        return {"detail": "Reply deleted successfully"}

    def _validate_image(self, file: UploadedFile) -> None:
        """Validate that the uploaded file is an allowed image type."""
        content_type = getattr(file, "content_type", "") or ""
        if content_type not in self.ALLOWED_IMAGE_TYPES:
            raise Http400BadRequestException(
                [ErrorDetail(ForumInvalidImageError, {"message": "Only JPEG, PNG, GIF, and WebP images are allowed"})]
            )

    @route.post(
        "/threads/{thread_id}/images",
        response={201: ForumImageUploadResponseSchema},
        permissions=[IsAuthenticated],
    )
    def add_thread_images(
        self,
        request: WSGIRequest,
        thread_id: str,
        images: list[UploadedFile] | None = File(default=None),
    ) -> dict:
        """Add images to a thread (author only)."""
        user = request.user

        try:
            thread = ForumThread.objects.get(id=thread_id)
        except ForumThread.DoesNotExist:
            raise KeyNotFoundException(ForumThreadNotFoundError, thread_id)

        if thread.author != user:
            raise Http403ForbiddenException("Only the author can add images to this thread")

        images = images or []
        if not images:
            return {"image_urls": []}

        urls = []
        for file in images:
            self._validate_image(file)
            thread_image = ForumThreadImage(thread=thread)
            thread_image.image.save(file.name, file, save=False)
            thread_image.save(user=user)
            urls.append(thread_image.image.url)

        return {"image_urls": urls}

    @route.delete(
        "/threads/{thread_id}/images/{image_id}",
        response={200: dict},
        permissions=[IsAuthenticated],
    )
    def delete_thread_image(
        self,
        request: WSGIRequest,
        thread_id: str,
        image_id: str,
    ) -> dict:
        """Remove an image from a thread (author only)."""
        user = request.user

        try:
            thread = ForumThread.objects.get(id=thread_id)
        except ForumThread.DoesNotExist:
            raise KeyNotFoundException(ForumThreadNotFoundError, thread_id)

        if thread.author != user:
            raise Http403ForbiddenException("Only the author can remove images from this thread")

        try:
            thread_image = ForumThreadImage.objects.get(id=image_id, thread=thread)
        except ForumThreadImage.DoesNotExist:
            raise KeyNotFoundException(ForumThreadImageNotFoundError, image_id)

        thread_image.image.delete(save=False)
        thread_image.delete()
        return {"detail": "Image removed successfully"}

    @route.post(
        "/replies/{reply_id}/images",
        response={201: ForumImageUploadResponseSchema},
        permissions=[IsAuthenticated],
    )
    def add_reply_images(
        self,
        request: WSGIRequest,
        reply_id: str,
        images: list[UploadedFile] | None = File(default=None),
    ) -> dict:
        """Add images to a reply (author only)."""
        user = request.user

        try:
            reply = ForumReply.objects.get(id=reply_id)
        except ForumReply.DoesNotExist:
            raise KeyNotFoundException(ForumReplyNotFoundError, reply_id)

        if reply.author != user:
            raise Http403ForbiddenException("Only the author can add images to this reply")

        images = images or []
        if not images:
            return {"image_urls": []}

        urls = []
        for file in images:
            self._validate_image(file)
            reply_image = ForumReplyImage(reply=reply)
            reply_image.image.save(file.name, file, save=False)
            reply_image.save(user=user)
            urls.append(reply_image.image.url)

        return {"image_urls": urls}

    @route.delete(
        "/replies/{reply_id}/images/{image_id}",
        response={200: dict},
        permissions=[IsAuthenticated],
    )
    def delete_reply_image(
        self,
        request: WSGIRequest,
        reply_id: str,
        image_id: str,
    ) -> dict:
        """Remove an image from a reply (author only)."""
        user = request.user

        try:
            reply = ForumReply.objects.get(id=reply_id)
        except ForumReply.DoesNotExist:
            raise KeyNotFoundException(ForumReplyNotFoundError, reply_id)

        if reply.author != user:
            raise Http403ForbiddenException("Only the author can remove images from this reply")

        try:
            reply_image = ForumReplyImage.objects.get(id=image_id, reply=reply)
        except ForumReplyImage.DoesNotExist:
            raise KeyNotFoundException(ForumReplyImageNotFoundError, image_id)

        reply_image.image.delete(save=False)
        reply_image.delete()
        return {"detail": "Image removed successfully"}
