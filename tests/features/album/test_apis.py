"""Tests for Album API (Phase 1)."""

import pytest
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client

from features.album.models import AlbumPhoto
from features.host.models import Host

User = get_user_model()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_image_file(name: str = "test.png", content_type: str = "image/png") -> SimpleUploadedFile:
    """Create a minimal valid PNG file for testing."""
    png_data = (
        b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01"
        b"\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\x0cIDATx\x9cc\xf8\x0f\x00"
        b"\x00\x01\x01\x00\x05\x18\xd8N\x00\x00\x00\x00IEND\xaeB`\x82"
    )
    return SimpleUploadedFile(name, png_data, content_type=content_type)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
@pytest.mark.django_db
def host_user(db: None) -> User:
    """Create a user who is a host owner."""
    return User.objects.create_user(
        email="hostowner@example.com",
        password="testpassword123",
        username="hostowner",
        user_type=User.UserTypeChoices.HOST,
    )


@pytest.fixture
@pytest.mark.django_db
def host(host_user: User) -> Host:
    """Create a host belonging to host_user."""
    h = Host(
        user=host_user,
        name="Test Shop",
        address="123 Main St",
        type="Cafe",
        phone_number="0912345678",
        description="A cozy test shop.",
    )
    h.save(user=host_user)
    return h


@pytest.fixture
def host_client(client: Client, host_user: User) -> Client:
    """Authenticated client for the host owner (force_login)."""
    client.force_login(host_user)
    return client


@pytest.fixture
@pytest.mark.django_db
def album_photo(host: Host, host_user: User) -> AlbumPhoto:
    """Create an AlbumPhoto with a dummy image."""
    image_file = _make_image_file()
    photo = AlbumPhoto(host=host, order=0)
    photo.image.save(image_file.name, image_file, save=False)
    photo.save(user=host_user)
    return photo


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

@pytest.mark.django_db
class TestAlbumAPI:
    """Test cases for Album API."""

    def test_get_album_public_empty(self, client: Client, host: Host) -> None:
        """Anyone can GET a host's album even when it has no photos."""
        response = client.get(f"/api/hosts/{host.id}/album")
        assert response.status_code == 200
        data = response.json()
        assert data["host_id"] == str(host.id)
        assert data["photos"] == []
        assert data["total"] == 0
        assert data["has_next"] is False

    def test_get_album_with_photos(self, client: Client, host: Host, album_photo: AlbumPhoto) -> None:
        """GET album returns photos when they exist."""
        response = client.get(f"/api/hosts/{host.id}/album")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert len(data["photos"]) == 1
        assert data["photos"][0]["id"] == str(album_photo.id)
        assert "image_url" in data["photos"][0]

    def test_get_album_host_not_found(self, client: Client) -> None:
        """GET album with non-existent host_id returns 404."""
        response = client.get("/api/hosts/00000000-0000-0000-0000-000000000000/album")
        assert response.status_code == 404

    def test_get_album_pagination(self, client: Client, host: Host, host_user: User) -> None:
        """GET album supports pagination."""
        for i in range(5):
            image_file = _make_image_file(f"photo{i}.png")
            photo = AlbumPhoto(host=host, order=i)
            photo.image.save(image_file.name, image_file, save=False)
            photo.save(user=host_user)

        response = client.get(f"/api/hosts/{host.id}/album?page=1&page_size=2")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 5
        assert len(data["photos"]) == 2
        assert data["has_next"] is True

    def test_upload_photos_success(self, host_client: Client, host: Host) -> None:
        """Host owner can upload photos."""
        image = _make_image_file()
        response = host_client.post(
            f"/api/hosts/{host.id}/album/photos",
            data={"images": image},
            format="multipart",
        )
        assert response.status_code == 201
        data = response.json()
        assert "image_urls" in data
        assert len(data["image_urls"]) == 1
        assert AlbumPhoto.objects.filter(host=host).count() == 1

    def test_upload_photos_not_authenticated(self, client: Client, host: Host) -> None:
        """Unauthenticated users cannot upload photos."""
        image = _make_image_file()
        response = client.post(
            f"/api/hosts/{host.id}/album/photos",
            data={"images": image},
            format="multipart",
        )
        assert response.status_code == 403

    def test_upload_photos_not_owner(self, client: Client, host: Host) -> None:
        """Non-owner authenticated user cannot upload photos."""
        other_user = User.objects.create_user(
            email="other@example.com",
            password="testpassword123",
            username="otheruser",
            user_type=User.UserTypeChoices.HELPER,
        )
        client.force_login(other_user)
        image = _make_image_file()
        response = client.post(
            f"/api/hosts/{host.id}/album/photos",
            data={"images": image},
            format="multipart",
        )
        assert response.status_code == 403

    def test_upload_photos_invalid_type(self, host_client: Client, host: Host) -> None:
        """Uploading a non-image file returns 400."""
        pdf = SimpleUploadedFile("doc.pdf", b"%PDF-1.4 fake", content_type="application/pdf")
        response = host_client.post(
            f"/api/hosts/{host.id}/album/photos",
            data={"images": pdf},
            format="multipart",
        )
        assert response.status_code == 400

    def test_upload_photos_unsupported_image_type(self, host_client: Client, host: Host) -> None:
        """Uploading an unsupported image type (e.g. BMP) returns 400."""
        bmp = SimpleUploadedFile("img.bmp", b"fake bmp", content_type="image/bmp")
        response = host_client.post(
            f"/api/hosts/{host.id}/album/photos",
            data={"images": bmp},
            format="multipart",
        )
        assert response.status_code == 400

    def test_delete_photo_success(self, host_client: Client, host: Host, album_photo: AlbumPhoto) -> None:
        """Host owner can delete a photo."""
        response = host_client.delete(
            f"/api/hosts/{host.id}/album/photos/{album_photo.id}"
        )
        assert response.status_code == 200
        assert not AlbumPhoto.objects.filter(id=album_photo.id).exists()

    def test_delete_photo_not_owner(self, client: Client, host: Host, album_photo: AlbumPhoto) -> None:
        """Non-owner cannot delete a photo."""
        other_user = User.objects.create_user(
            email="other2@example.com",
            password="testpassword123",
            username="otheruser2",
            user_type=User.UserTypeChoices.HELPER,
        )
        client.force_login(other_user)
        response = client.delete(
            f"/api/hosts/{host.id}/album/photos/{album_photo.id}"
        )
        assert response.status_code == 403
        assert AlbumPhoto.objects.filter(id=album_photo.id).exists()

    def test_delete_photo_not_found(self, host_client: Client, host: Host) -> None:
        """Deleting a non-existent photo returns 404."""
        response = host_client.delete(
            f"/api/hosts/{host.id}/album/photos/00000000-0000-0000-0000-000000000000"
        )
        assert response.status_code == 404

    def test_deleted_photo_no_longer_in_album(
        self, host_client: Client, host: Host, album_photo: AlbumPhoto
    ) -> None:
        """After deletion the photo is not included in the album GET response."""
        host_client.delete(f"/api/hosts/{host.id}/album/photos/{album_photo.id}")
        response = host_client.get(f"/api/hosts/{host.id}/album")
        assert response.status_code == 200
        assert response.json()["total"] == 0
