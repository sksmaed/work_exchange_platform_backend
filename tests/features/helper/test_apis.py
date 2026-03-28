import pytest
from django.core.files.uploadedfile import SimpleUploadedFile

from features.helper.models import HelperModel, HelperPhoto


def _make_image_file(name: str = "test.png", content_type: str = "image/png") -> SimpleUploadedFile:
    """Create a minimal valid PNG file for testing."""
    png_data = (
        b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01"
        b"\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\x0cIDATx\x9cc\xf8\x0f\x00"
        b"\x00\x01\x01\x00\x05\x18\xd8N\x00\x00\x00\x00IEND\xaeB`\x82"
    )
    return SimpleUploadedFile(name, png_data, content_type=content_type)


@pytest.fixture
def test_user(django_user_model):
    return django_user_model.objects.create_user(
        username="testhelper",
        email="testhelper@example.com",
        password="password123",
        user_type=django_user_model.UserTypeChoices.HELPER,
    )


@pytest.mark.django_db
class TestHelperProfileAPI:
    def test_create_helper_profile_success(self, client, test_user):
        client.force_login(test_user)
        url = "/api/helpers/"
        payload = {
            "description": "I am a helpful person",
            "birthday": "2000-01-01",
            "gender": "F",
            "expected_time_periods": [{"start_date": "2025-05-01", "end_date": "2025-05-15"}],
            "residence": "Taipei",
        }

        response = client.post(url, data=payload, content_type="application/json")
        assert response.status_code == 201

        helper = HelperModel.objects.get(user=test_user)
        assert helper.description == "I am a helpful person"
        assert len(helper.expected_time_periods) == 1
        assert helper.expected_time_periods[0]["start_date"] == "2025-05-01"

    def test_create_helper_profile_invalid_periods(self, client, test_user):
        client.force_login(test_user)
        url = "/api/helpers/"
        payload = {
            "description": "I am a helpful person",
            "birthday": "2000-01-01",
            "gender": "F",
            "expected_time_periods": [
                {"start_date": "2025-05-01", "end_date": "2025-05-15"},
                {"start_date": "2025-06-01", "end_date": "2025-06-15"},
            ],
            "residence": "Taipei",
        }

        response = client.post(url, data=payload, content_type="application/json")
        # Should fail due to custom schema validator checking for continuous date range (length <= 1)
        assert response.status_code == 422
        assert "Helpers can only select a single continuous time period" in str(response.content)

    def test_create_helper_profile_invalid_date_order(self, client, test_user):
        client.force_login(test_user)
        url = "/api/helpers/"
        payload = {
            "description": "I am a helpful person",
            "birthday": "2000-01-01",
            "gender": "F",
            "expected_time_periods": [{"start_date": "2025-05-15", "end_date": "2025-05-01"}],
            "residence": "Taipei",
        }

        response = client.post(url, data=payload, content_type="application/json")
        assert response.status_code == 422
        assert "start_date cannot be after end_date" in str(response.content)

    def test_upload_avatar_success(self, client, test_user):
        client.force_login(test_user)
        helper = HelperModel(
            user=test_user,
            description="Profile",
            birthday="2000-01-01",
            gender="F",
        )
        helper.save(user=test_user)
        image = _make_image_file("avatar.png")

        response = client.post(
            "/api/helpers/self/avatar",
            data={"image": image},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["avatar_url"]
        assert data["photos"] == []

    def test_upload_helper_photos_success(self, client, test_user):
        client.force_login(test_user)
        helper = HelperModel(
            user=test_user,
            description="Profile",
            birthday="2000-01-01",
            gender="F",
        )
        helper.save(user=test_user)
        image = _make_image_file("helper-photo.png")

        response = client.post(
            "/api/helpers/self/photos",
            data={"images": image},
            format="multipart",
        )

        assert response.status_code == 201
        data = response.json()
        assert len(data["image_urls"]) == 1
        assert HelperPhoto.objects.filter(helper=helper).count() == 1

    def test_delete_helper_photo_success(self, client, test_user):
        client.force_login(test_user)
        helper = HelperModel(
            user=test_user,
            description="Profile",
            birthday="2000-01-01",
            gender="F",
        )
        helper.save(user=test_user)
        photo = HelperPhoto(helper=helper)
        image = _make_image_file("to-delete.png")
        photo.image.save(image.name, image, save=False)
        photo.save(user=test_user)

        response = client.delete(f"/api/helpers/self/photos/{photo.id}")

        assert response.status_code == 200
        assert not HelperPhoto.objects.filter(id=photo.id).exists()
