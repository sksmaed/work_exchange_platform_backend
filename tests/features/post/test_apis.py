import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client

from features.core.models import User
from features.host.models import Host
from features.post.models import Comment, Post


@pytest.fixture
def host_user(db: None) -> User:
    """Create a user who is a host owner."""
    return User.objects.create_user(
        email="hostowner_post@example.com",
        password="testpassword123",
        username="hostowner_post",
        user_type=User.UserTypeChoices.HOST,
    )


@pytest.fixture
def other_user(db: None) -> User:
    """Create another regular user."""
    return User.objects.create_user(
        email="otheruser_post@example.com",
        password="testpassword123",
        username="otheruser_post",
        user_type=User.UserTypeChoices.HELPER,
    )


@pytest.fixture
def host(host_user: User) -> Host:
    """Create a host belonging to host_user."""
    h = Host(
        user=host_user,
        name="Test Shop Post",
        address="123 Main St",
        type="Cafe",
        phone_number="0912345678",
        description="A cozy test shop.",
    )
    h.save(user=host_user)
    return h


@pytest.fixture
def host_client(client: Client, host_user: User) -> Client:
    response = client.post(
        "/api/auth/login/",
        {"email": host_user.email, "password": "testpassword123"},
        content_type="application/json",
    )
    client.cookies.update(response.cookies)
    return client


@pytest.fixture
def other_client(client: Client, other_user: User) -> Client:
    response = client.post(
        "/api/auth/login/",
        {"email": other_user.email, "password": "testpassword123"},
        content_type="application/json",
    )
    client.cookies.update(response.cookies)
    return client


@pytest.fixture
def test_post(host: Host, host_user: User) -> Post:
    post = Post(host=host, content="Original Post Content")
    post.save(user=host_user)
    return post


@pytest.mark.django_db
class TestPostAPI:
    def test_create_post_success(self, host_client: Client, host: Host):
        image = SimpleUploadedFile("test.jpg", b"file_content", content_type="image/jpeg")
        response = host_client.post(
            f"/api/hosts/{host.id}/posts",
            data={"content": "Hello World", "images": [image]},
        )
        assert response.status_code == 200
        data = response.json()["data"]
        assert data["content"] == "Hello World"
        assert len(data["photos"]) == 1
        assert Post.objects.filter(host=host).count() == 1

    def test_create_post_not_owner(self, other_client: Client, host: Host):
        response = other_client.post(
            f"/api/hosts/{host.id}/posts",
            data={"content": "Hello World"},
        )
        assert response.status_code == 403

    def test_list_posts(self, client: Client, host: Host, test_post: Post):
        response = client.get(f"/api/hosts/{host.id}/posts")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert data["posts"][0]["content"] == "Original Post Content"
        assert data["posts"][0]["type"] == "all"

    def test_list_all_posts(self, client: Client, host: Host, test_post: Post):
        response = client.get("/api/posts")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert data["posts"][0]["content"] == "Original Post Content"
        assert data["posts"][0]["host_id"] == str(host.id)

    def test_list_posts_invalid_host_id_returns_404(self, client: Client):
        response = client.get("/api/hosts/1/posts")
        assert response.status_code == 404

    def test_update_post(self, host_client: Client, test_post: Post):
        response = host_client.patch(
            f"/api/posts/{test_post.id}", data={"content": "Updated Content"}, content_type="application/json"
        )
        assert response.status_code == 200
        assert response.json()["data"]["content"] == "Updated Content"
        test_post.refresh_from_db()
        assert test_post.content == "Updated Content"

    def test_delete_post(self, host_client: Client, test_post: Post):
        response = host_client.delete(f"/api/posts/{test_post.id}")
        assert response.status_code == 200
        assert Post.objects.filter(id=test_post.id).count() == 0

    def test_create_comment(self, other_client: Client, test_post: Post):
        response = other_client.post(f"/api/posts/{test_post.id}/comments", data={"content": "Nice post!"})
        assert response.status_code == 200
        data = response.json()["data"]
        assert data["content"] == "Nice post!"

        test_post.refresh_from_db()
        assert test_post.comment_count == 1

    def test_list_comments(self, client: Client, test_post: Post, other_user: User):
        c = Comment(post=test_post, user=other_user, content="Comment 1")
        c.save(user=other_user)

        response = client.get(f"/api/posts/{test_post.id}/comments")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert data["comments"][0]["content"] == "Comment 1"

    def test_create_reply_comment(self, other_client: Client, test_post: Post, other_user: User):
        # Create a parent comment first
        parent_resp = other_client.post(f"/api/posts/{test_post.id}/comments", data={"content": "Parent"})
        assert parent_resp.status_code == 200
        parent_id = parent_resp.json()["data"]["id"]

        # Create a reply to the parent
        reply_resp = other_client.post(
            f"/api/posts/{test_post.id}/comments", data={"content": "Reply", "parent_id": parent_id}
        )
        assert reply_resp.status_code == 200
        reply_data = reply_resp.json()["data"]
        assert reply_data["content"] == "Reply"
        assert reply_data["parent_id"] == parent_id

    def test_delete_comment_by_owner(self, other_client: Client, test_post: Post, other_user: User):
        c = Comment(post=test_post, user=other_user, content="Comment 1")
        c.save(user=other_user)
        test_post.comment_count += 1
        test_post.save(user=other_user)

        response = other_client.delete(f"/api/posts/{test_post.id}/comments/{c.id}")
        assert response.status_code == 200
        test_post.refresh_from_db()
        assert test_post.comment_count == 0

    def test_delete_comment_by_host(self, host_client: Client, test_post: Post, other_user: User):
        c = Comment(post=test_post, user=other_user, content="Comment 1")
        c.save(user=other_user)
        test_post.comment_count += 1
        test_post.save(user=other_user)

        response = host_client.delete(f"/api/posts/{test_post.id}/comments/{c.id}")
        assert response.status_code == 200
        test_post.refresh_from_db()
        assert test_post.comment_count == 0

    def test_toggle_like(self, other_client: Client, test_post: Post):
        # Like
        response = other_client.post(f"/api/posts/{test_post.id}/likes")
        assert response.status_code == 200
        assert response.json()["data"]["liked"] is True
        test_post.refresh_from_db()
        assert test_post.like_count == 1

        # Unlike
        response = other_client.post(f"/api/posts/{test_post.id}/likes")
        assert response.status_code == 200
        assert response.json()["data"]["liked"] is False
        test_post.refresh_from_db()
        assert test_post.like_count == 0
