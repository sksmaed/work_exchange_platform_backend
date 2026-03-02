"""Tests for Forum API."""

import json

import pytest
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client
from features.forum.models import ForumCategory, ForumReply, ForumReplyImage, ForumThread, ForumThreadImage

User = get_user_model()


@pytest.fixture
def auth_client(client: Client, user: User) -> Client:
    """Authenticated client using force_login (bypasses email verification)."""
    client.force_login(user)
    return client


@pytest.fixture
@pytest.mark.django_db
def forum_category(db: None) -> ForumCategory:
    """Create a forum category."""
    return ForumCategory.objects.create(
        name="General",
        description="General discussion",
        order=0,
    )


@pytest.fixture
@pytest.mark.django_db
def forum_thread(user: User, forum_category: ForumCategory) -> ForumThread:
    """Create a forum thread."""
    return ForumThread.objects.create(
        title="Test Thread",
        content="This is test thread content.",
        author=user,
        category=forum_category,
    )


@pytest.fixture
@pytest.mark.django_db
def forum_reply(forum_thread: ForumThread, user: User) -> ForumReply:
    """Create a forum reply."""
    return ForumReply.objects.create(
        thread=forum_thread,
        author=user,
        content="This is a test reply.",
    )


@pytest.mark.django_db
class TestForumAPI:
    """Test cases for Forum API."""

    def test_list_categories_public(self, client: Client, forum_category: ForumCategory) -> None:
        """Test listing categories (public, no auth required)."""
        response = client.get("/api/forum/categories")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 1
        assert data[0]["name"] == forum_category.name
        assert data[0]["description"] == forum_category.description

    def test_list_categories_empty(self, client: Client) -> None:
        """Test listing categories when empty."""
        response = client.get("/api/forum/categories")
        assert response.status_code == 200
        assert response.json() == []

    def test_list_threads_public(self, client: Client, forum_thread: ForumThread, user: User) -> None:
        """Test listing threads (public)."""
        response = client.get("/api/forum/threads")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert len(data["items"]) == 1
        assert data["items"][0]["title"] == forum_thread.title
        assert data["items"][0]["author"]["id"] == str(user.id)

    def test_list_threads_pagination(
        self, client: Client, user: User, forum_category: ForumCategory
    ) -> None:
        """Test thread list pagination."""
        for i in range(5):
            ForumThread.objects.create(
                title=f"Thread {i}",
                content=f"Content {i}",
                author=user,
                category=forum_category,
            )
        response = client.get("/api/forum/threads?page_size=2&page=1")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 5
        assert data["page_size"] == 2
        assert len(data["items"]) == 2
        assert data["has_next"] is True

    def test_list_threads_page_size_capped(
        self, client: Client, user: User, forum_category: ForumCategory
    ) -> None:
        """Test that page_size is capped at maximum (100)."""
        response = client.get("/api/forum/threads?page_size=10000")
        assert response.status_code == 200
        data = response.json()
        assert data["page_size"] == 100

    def test_list_threads_filter_by_category(
        self, client: Client, forum_thread: ForumThread, forum_category: ForumCategory
    ) -> None:
        """Test filtering threads by category."""
        response = client.get(f"/api/forum/threads?category_id={forum_category.id}")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert data["items"][0]["category_id"] == str(forum_category.id)

    def test_list_threads_search_by_title(
        self, client: Client, forum_thread: ForumThread, user: User, forum_category: ForumCategory
    ) -> None:
        """Test searching threads by title."""
        matching_thread = ForumThread.objects.create(
            title="UniqueTitle123",
            content="Some content",
            author=user,
            category=forum_category,
        )
        ForumThread.objects.create(
            title="Another thread",
            content="Irrelevant content",
            author=user,
            category=forum_category,
        )
        response = client.get("/api/forum/threads?search=UniqueTitle123")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert len(data["items"]) == 1
        assert data["items"][0]["title"] == matching_thread.title

    def test_list_threads_search_by_content(
        self, client: Client, forum_thread: ForumThread, user: User, forum_category: ForumCategory
    ) -> None:
        """Test searching threads by content."""
        matching_thread = ForumThread.objects.create(
            title="Some title",
            content="Body with SpecialKeywordXYZ",
            author=user,
            category=forum_category,
        )
        ForumThread.objects.create(
            title="Different title",
            content="No matching keyword here",
            author=user,
            category=forum_category,
        )
        response = client.get("/api/forum/threads?search=SpecialKeywordXYZ")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert len(data["items"]) == 1
        assert data["items"][0]["title"] == matching_thread.title

    def test_list_threads_search_no_results(
        self, client: Client, forum_thread: ForumThread
    ) -> None:
        """Test searching threads with no matching results."""
        response = client.get("/api/forum/threads?search=NoMatchStringXYZ")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 0
        assert data["items"] == []

    def test_get_thread_public(
        self, client: Client, forum_thread: ForumThread, forum_reply: ForumReply, user: User
    ) -> None:
        """Test getting thread detail (public)."""
        response = client.get(f"/api/forum/threads/{forum_thread.id}")
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == forum_thread.title
        assert data["content"] == forum_thread.content
        assert data["reply_count"] == 1
        assert len(data["replies"]) == 1
        assert data["replies"][0]["content"] == forum_reply.content

    def test_get_thread_not_found(self, client: Client) -> None:
        """Test getting non-existent thread returns 404."""
        response = client.get("/api/forum/threads/00000000-0000-0000-0000-000000000000")
        assert response.status_code == 404

    def test_create_thread_success(
        self, auth_client: Client, user: User, forum_category: ForumCategory
    ) -> None:
        """Test creating a thread."""
        payload = {
            "title": "New Discussion",
            "content": "This is the content of my new thread.",
            "category_id": str(forum_category.id),
        }
        response = auth_client.post(
            "/api/forum/threads",
            data=json.dumps(payload),
            content_type="application/json",
        )
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == payload["title"]
        assert data["content"] == payload["content"]
        assert data["author"]["id"] == str(user.id)
        assert data["category_id"] == str(forum_category.id)
        assert data["reply_count"] == 0

    def test_create_thread_not_authenticated(
        self, client: Client, forum_category: ForumCategory
    ) -> None:
        """Test creating thread without auth fails."""
        payload = {"title": "Test", "content": "Content", "category_id": str(forum_category.id)}
        response = client.post(
            "/api/forum/threads",
            data=json.dumps(payload),
            content_type="application/json",
        )
        assert response.status_code == 403

    def test_update_thread_author(
        self, auth_client: Client, forum_thread: ForumThread
    ) -> None:
        """Test author can update thread."""
        payload = {"title": "Updated Title", "content": "Updated content"}
        response = auth_client.patch(
            f"/api/forum/threads/{forum_thread.id}",
            data=json.dumps(payload),
            content_type="application/json",
        )
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == payload["title"]
        assert data["content"] == payload["content"]

    def test_update_thread_not_author(
        self, client: Client, forum_thread: ForumThread
    ) -> None:
        """Test non-author cannot update thread."""
        other_user = User.objects.create_user(
            email="other@example.com",
            password="testpassword123",
            username="otheruser",
            user_type=User.UserTypeChoices.HELPER,
        )
        client.force_login(other_user)
        payload = {"title": "Hacked"}
        response = client.patch(
            f"/api/forum/threads/{forum_thread.id}",
            data=json.dumps(payload),
            content_type="application/json",
        )
        assert response.status_code == 403

    def test_delete_thread_author(self, auth_client: Client, forum_thread: ForumThread) -> None:
        """Test author can delete thread."""
        response = auth_client.delete(f"/api/forum/threads/{forum_thread.id}")
        assert response.status_code == 200
        assert not ForumThread.objects.filter(id=forum_thread.id).exists()

    def test_delete_thread_not_author(
        self, client: Client, forum_thread: ForumThread
    ) -> None:
        """Test non-author cannot delete thread."""
        other_user = User.objects.create_user(
            email="other@example.com",
            password="testpassword123",
            username="otheruser",
            user_type=User.UserTypeChoices.HELPER,
        )
        client.force_login(other_user)
        response = client.delete(f"/api/forum/threads/{forum_thread.id}")
        assert response.status_code == 403

    def test_create_reply_success(
        self, auth_client: Client, forum_thread: ForumThread, user: User
    ) -> None:
        """Test creating a reply."""
        payload = {"content": "My reply to the thread"}
        response = auth_client.post(
            f"/api/forum/threads/{forum_thread.id}/replies",
            data=json.dumps(payload),
            content_type="application/json",
        )
        assert response.status_code == 201
        data = response.json()
        assert data["content"] == payload["content"]
        assert data["thread_id"] == str(forum_thread.id)
        assert data["author"]["id"] == str(user.id)

    def test_create_reply_not_authenticated(
        self, client: Client, forum_thread: ForumThread
    ) -> None:
        """Test creating reply without auth fails."""
        payload = {"content": "Reply"}
        response = client.post(
            f"/api/forum/threads/{forum_thread.id}/replies",
            data=json.dumps(payload),
            content_type="application/json",
        )
        assert response.status_code == 403

    def test_update_reply_author(
        self, auth_client: Client, forum_reply: ForumReply
    ) -> None:
        """Test author can update reply."""
        payload = {"content": "Updated reply content"}
        response = auth_client.patch(
            f"/api/forum/replies/{forum_reply.id}",
            data=json.dumps(payload),
            content_type="application/json",
        )
        assert response.status_code == 200
        data = response.json()
        assert data["content"] == payload["content"]

    def test_update_reply_not_author(
        self, client: Client, forum_reply: ForumReply
    ) -> None:
        """Test non-author cannot update reply."""
        other_user = User.objects.create_user(
            email="other@example.com",
            password="testpassword123",
            username="otheruser",
            user_type=User.UserTypeChoices.HELPER,
        )
        client.force_login(other_user)
        payload = {"content": "Hacked"}
        response = client.patch(
            f"/api/forum/replies/{forum_reply.id}",
            data=json.dumps(payload),
            content_type="application/json",
        )
        assert response.status_code == 403

    def test_delete_reply_author(self, auth_client: Client, forum_reply: ForumReply) -> None:
        """Test author can delete reply."""
        response = auth_client.delete(f"/api/forum/replies/{forum_reply.id}")
        assert response.status_code == 200
        assert not ForumReply.objects.filter(id=forum_reply.id).exists()

    def test_delete_reply_not_author(
        self, client: Client, forum_reply: ForumReply
    ) -> None:
        """Test non-author cannot delete reply."""
        other_user = User.objects.create_user(
            email="other@example.com",
            password="testpassword123",
            username="otheruser",
            user_type=User.UserTypeChoices.HELPER,
        )
        client.force_login(other_user)
        response = client.delete(f"/api/forum/replies/{forum_reply.id}")
        assert response.status_code == 403


@pytest.mark.django_db
class TestForumAPIIntegration:
    """Integration tests for Forum API."""

    def test_full_forum_workflow(
        self, auth_client: Client, user: User, forum_category: ForumCategory
    ) -> None:
        """Test complete forum workflow: create thread, add reply, update, delete."""
        # Create thread
        create_resp = auth_client.post(
            "/api/forum/threads",
            data=json.dumps({
                "title": "Integration Test Thread",
                "content": "Testing the full flow.",
                "category_id": str(forum_category.id),
            }),
            content_type="application/json",
        )
        assert create_resp.status_code == 201
        thread_id = create_resp.json()["id"]

        # Get thread
        get_resp = auth_client.get(f"/api/forum/threads/{thread_id}")
        assert get_resp.status_code == 200
        assert get_resp.json()["reply_count"] == 0

        # Add reply
        reply_resp = auth_client.post(
            f"/api/forum/threads/{thread_id}/replies",
            data=json.dumps({"content": "First reply!"}),
            content_type="application/json",
        )
        assert reply_resp.status_code == 201

        # Verify reply appears
        get_resp2 = auth_client.get(f"/api/forum/threads/{thread_id}")
        assert get_resp2.status_code == 200
        assert get_resp2.json()["reply_count"] == 1
        assert len(get_resp2.json()["replies"]) == 1
        assert get_resp2.json()["replies"][0]["content"] == "First reply!"

        # Delete thread
        del_resp = auth_client.delete(f"/api/forum/threads/{thread_id}")
        assert del_resp.status_code == 200


def _make_image_file(name: str = "test.png", content_type: str = "image/png") -> SimpleUploadedFile:
    """Create a minimal valid PNG file for testing."""
    # Minimal 1x1 PNG
    png_data = (
        b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01"
        b"\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\x0cIDATx\x9cc\xf8\x0f\x00"
        b"\x00\x01\x01\x00\x05\x18\xd8N\x00\x00\x00\x00IEND\xaeB`\x82"
    )
    return SimpleUploadedFile(name, png_data, content_type=content_type)


@pytest.mark.django_db
class TestForumImageUpload:
    """Test cases for forum image uploads."""

    def test_list_threads_includes_image_urls(
        self, client: Client, forum_thread: ForumThread, user: User
    ) -> None:
        """Test that thread list includes image_urls (empty when no images)."""
        response = client.get("/api/forum/threads")
        assert response.status_code == 200
        data = response.json()
        assert "image_urls" in data["items"][0]
        assert data["items"][0]["image_urls"] == []

    def test_get_thread_includes_image_urls(
        self, client: Client, forum_thread: ForumThread, forum_reply: ForumReply
    ) -> None:
        """Test that thread detail includes image_urls for thread and replies."""
        response = client.get(f"/api/forum/threads/{forum_thread.id}")
        assert response.status_code == 200
        data = response.json()
        assert "image_urls" in data
        assert data["image_urls"] == []
        assert "image_urls" in data["replies"][0]
        assert data["replies"][0]["image_urls"] == []

    def test_add_thread_images_success(
        self, auth_client: Client, forum_thread: ForumThread
    ) -> None:
        """Test adding images to a thread."""
        image = _make_image_file()
        response = auth_client.post(
            f"/api/forum/threads/{forum_thread.id}/images",
            data={"images": image},
            format="multipart",
        )
        assert response.status_code == 201
        data = response.json()
        assert "image_urls" in data
        assert len(data["image_urls"]) == 1
        assert "/api/media/" in data["image_urls"][0]
        assert ForumThreadImage.objects.filter(thread=forum_thread).count() == 1

    def test_add_thread_images_not_author(
        self, client: Client, forum_thread: ForumThread
    ) -> None:
        """Test that non-author cannot add images to thread."""
        other_user = User.objects.create_user(
            email="other@example.com",
            password="testpassword123",
            username="otheruser",
            user_type=User.UserTypeChoices.HELPER,
        )
        client.force_login(other_user)
        image = _make_image_file()
        response = client.post(
            f"/api/forum/threads/{forum_thread.id}/images",
            data={"images": image},
            format="multipart",
        )
        assert response.status_code == 403

    def test_add_reply_images_success(
        self, auth_client: Client, forum_reply: ForumReply
    ) -> None:
        """Test adding images to a reply."""
        image = _make_image_file()
        response = auth_client.post(
            f"/api/forum/replies/{forum_reply.id}/images",
            data={"images": image},
            format="multipart",
        )
        assert response.status_code == 201
        data = response.json()
        assert len(data["image_urls"]) == 1
        assert ForumReplyImage.objects.filter(reply=forum_reply).count() == 1

    def test_delete_thread_image_author(
        self, auth_client: Client, forum_thread: ForumThread
    ) -> None:
        """Test author can delete thread image."""
        image = _make_image_file()
        auth_client.post(
            f"/api/forum/threads/{forum_thread.id}/images",
            data={"images": image},
            format="multipart",
        )
        thread_image = ForumThreadImage.objects.get(thread=forum_thread)
        response = auth_client.delete(
            f"/api/forum/threads/{forum_thread.id}/images/{thread_image.id}"
        )
        assert response.status_code == 200
        assert not ForumThreadImage.objects.filter(thread=forum_thread).exists()

    def test_delete_reply_image_author(
        self, auth_client: Client, forum_reply: ForumReply
    ) -> None:
        """Test author can delete reply image."""
        image = _make_image_file()
        auth_client.post(
            f"/api/forum/replies/{forum_reply.id}/images",
            data={"images": image},
            format="multipart",
        )
        reply_image = ForumReplyImage.objects.get(reply=forum_reply)
        response = auth_client.delete(
            f"/api/forum/replies/{forum_reply.id}/images/{reply_image.id}"
        )
        assert response.status_code == 200
        assert not ForumReplyImage.objects.filter(reply=forum_reply).exists()

    def test_thread_with_images_in_get_response(
        self, auth_client: Client, forum_thread: ForumThread
    ) -> None:
        """Test that get_thread returns image URLs after upload."""
        image = _make_image_file()
        auth_client.post(
            f"/api/forum/threads/{forum_thread.id}/images",
            data={"images": image},
            format="multipart",
        )
        response = auth_client.get(f"/api/forum/threads/{forum_thread.id}")
        assert response.status_code == 200
        assert len(response.json()["image_urls"]) == 1

    def test_add_thread_images_invalid_content_type(
        self, auth_client: Client, forum_thread: ForumThread
    ) -> None:
        """Test that non-image files are rejected for thread upload."""
        pdf_file = SimpleUploadedFile(
            "document.pdf",
            b"%PDF-1.4 fake pdf content",
            content_type="application/pdf",
        )
        response = auth_client.post(
            f"/api/forum/threads/{forum_thread.id}/images",
            data={"images": pdf_file},
            format="multipart",
        )
        assert response.status_code == 400

    def test_add_thread_images_invalid_image_type(
        self, auth_client: Client, forum_thread: ForumThread
    ) -> None:
        """Test that unsupported image types (e.g. BMP) are rejected."""
        bmp_file = SimpleUploadedFile(
            "image.bmp",
            b"fake bmp content",
            content_type="image/bmp",
        )
        response = auth_client.post(
            f"/api/forum/threads/{forum_thread.id}/images",
            data={"images": bmp_file},
            format="multipart",
        )
        assert response.status_code == 400

    def test_add_reply_images_invalid_content_type(
        self, auth_client: Client, forum_reply: ForumReply
    ) -> None:
        """Test that non-image files are rejected for reply upload."""
        text_file = SimpleUploadedFile(
            "readme.txt",
            b"plain text content",
            content_type="text/plain",
        )
        response = auth_client.post(
            f"/api/forum/replies/{forum_reply.id}/images",
            data={"images": text_file},
            format="multipart",
        )
        assert response.status_code == 400
