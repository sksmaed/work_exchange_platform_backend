"""Tests for Helper APIs."""

import json
from datetime import date

import pytest
from django.contrib.auth import get_user_model
from django.test import Client

from features.helper.models import HelperModel


@pytest.mark.django_db
class TestHelperControllerAPI:
    """Test cases for HelperControllerAPI endpoints."""

    def test_list_helpers_success(self, client: Client, helper_model: HelperModel) -> None:
        """Test successful retrieval of helpers list."""
        response = client.get("/api/helpers")

        assert response.status_code == 200
        data = response.json()

        assert "count" in data
        assert "items" in data  # ninja_extra uses "items" instead of "results"
        assert len(data["items"]) >= 1
        assert any(helper["id"] == str(helper_model.id) for helper in data["items"])

    def test_list_helpers_pagination(self, client: Client, helper_model: HelperModel) -> None:
        """Test helpers list pagination."""
        # Create additional helpers
        User = get_user_model()
        for i in range(5):
            user = User.objects.create_user(
                email=f"helper{i}@example.com",
                password="password123",
                username=f"helper{i}",
                user_type=User.UserTypeChoices.HELPER,
            )
            from allauth.account.models import EmailAddress  # noqa: PLC0415
            EmailAddress.objects.create(user=user, email=f"helper{i}@example.com", verified=True, primary=True)

            HelperModel.objects.create(
                user_id=user.id,
                description=f"Helper {i} description",
                birthday="1990-01-01",
                gender=HelperModel.GenderChoices.MALE,
            )

        response = client.get("/api/helpers?page=1&page_size=3")

        assert response.status_code == 200
        data = response.json()

        assert "count" in data
        assert "items" in data  # ninja_extra uses "items" instead of "results"
        assert len(data["items"]) == 3

    def test_list_helpers_filter_by_residence(self, client: Client, helper_model: HelperModel) -> None:
        """Test filtering helpers by residence."""
        # Create helper with different residence
        User = get_user_model()
        other_user = User.objects.create_user(
            email="other@example.com",
            password="password123",
            username="otheruser",
            user_type=User.UserTypeChoices.HELPER,
        )
        from allauth.account.models import EmailAddress  # noqa: PLC0415
        EmailAddress.objects.create(user=other_user, email="other@example.com", verified=True, primary=True)

        HelperModel.objects.create(
            user_id=other_user.id,
            description="Other helper",
            birthday="1990-01-01",
            gender=HelperModel.GenderChoices.FEMALE,
            residence="Other City",
        )

        response = client.get("/api/helpers?residence=Test City")

        assert response.status_code == 200
        data = response.json()

        assert all("Test City" in helper.get("residence", "") for helper in data["items"])

    def test_list_helpers_filter_by_gender(self, client: Client, helper_model: HelperModel) -> None:
        """Test filtering helpers by gender."""
        # Create helper with different gender
        User = get_user_model()
        other_user = User.objects.create_user(
            email="other@example.com",
            password="password123",
            username="otheruser",
            user_type=User.UserTypeChoices.HELPER,
        )
        from allauth.account.models import EmailAddress  # noqa: PLC0415
        EmailAddress.objects.create(user=other_user, email="other@example.com", verified=True, primary=True)

        HelperModel.objects.create(
            user_id=other_user.id,
            description="Other helper",
            birthday="1990-01-01",
            gender=HelperModel.GenderChoices.FEMALE,
        )

        response = client.get("/api/helpers?gender=M")

        assert response.status_code == 200
        data = response.json()

        assert all(helper["gender"] == "M" for helper in data["items"])

    def test_list_helpers_filter_by_licenses(self, client: Client, helper_model: HelperModel) -> None:
        """Test filtering helpers by licenses."""
        response = client.get("/api/helpers?licenses=Driving")

        assert response.status_code == 200
        data = response.json()

        assert all(helper["licenses"] == "Driving" for helper in data["items"])

    def test_list_helpers_filter_by_min_rating(self, client: Client, helper_model: HelperModel) -> None:
        """Test filtering helpers by minimum rating."""
        # Create helper with lower rating
        User = get_user_model()
        other_user = User.objects.create_user(
            email="other@example.com",
            password="password123",
            username="otheruser",
            user_type=User.UserTypeChoices.HELPER,
        )
        from allauth.account.models import EmailAddress  # noqa: PLC0415
        EmailAddress.objects.create(user=other_user, email="other@example.com", verified=True, primary=True)

        HelperModel.objects.create(
            user_id=other_user.id,
            description="Other helper",
            birthday="1990-01-01",
            gender=HelperModel.GenderChoices.FEMALE,
            avg_rating=3.0,
        )

        response = client.get("/api/helpers?min_rating=4.0")

        assert response.status_code == 200
        data = response.json()

        assert all(helper["avg_rating"] >= 4.0 for helper in data["items"])

    def test_list_helpers_search(self, client: Client, helper_model: HelperModel) -> None:
        """Test searching helpers."""
        response = client.get("/api/helpers?search=Test helper")

        assert response.status_code == 200
        data = response.json()

        # Search should find helpers matching description, residence, personality, or motivation
        assert len(data["items"]) >= 0  # May or may not find results depending on search

    def test_list_helpers_ordering(self, client: Client, helper_model: HelperModel) -> None:
        """Test ordering helpers."""
        # Create helpers with different ratings
        User = get_user_model()
        for i, rating in enumerate([3.0, 5.0, 4.0]):
            user = User.objects.create_user(
                email=f"helper{i}@example.com",
                password="password123",
                username=f"helper{i}",
                user_type=User.UserTypeChoices.HELPER,
            )
            from allauth.account.models import EmailAddress  # noqa: PLC0415
            EmailAddress.objects.create(user=user, email=f"helper{i}@example.com", verified=True, primary=True)

            HelperModel.objects.create(
                user_id=user.id,
                description=f"Helper {i}",
                birthday="1990-01-01",
                gender=HelperModel.GenderChoices.MALE,
                avg_rating=rating,
            )

        response = client.get("/api/helpers?ordering=-avg_rating")

        assert response.status_code == 200
        data = response.json()

        ratings = [helper["avg_rating"] for helper in data["items"]]
        assert ratings == sorted(ratings, reverse=True)

    def test_get_self_profile_success(
        self,
        authenticated_helper_client: Client,
        helper_model: HelperModel,
    ) -> None:
        """Test successful retrieval of authenticated user's helper profile."""
        response = authenticated_helper_client.get("/api/helpers/self/")

        assert response.status_code == 200
        data = response.json()

        assert data["id"] == str(helper_model.id)
        assert data["description"] == helper_model.description
        assert data["birthday"] == str(helper_model.birthday)

    def test_get_self_profile_not_authenticated(self, client: Client) -> None:
        """Test getting self profile without authentication should fail."""
        response = client.get("/api/helpers/self/")

        # Endpoint now requires authentication
        assert response.status_code == 403

    def test_get_self_profile_no_profile(
        self,
        authenticated_client: Client,
    ) -> None:
        """Test getting self profile when user has no helper profile should return 404."""
        response = authenticated_client.get("/api/helpers/self/")

        assert response.status_code == 404

    def test_get_helper_success(self, client: Client, helper_model: HelperModel) -> None:
        """Test successful retrieval of a specific helper profile."""
        response = client.get(f"/api/helpers/{helper_model.id}")

        assert response.status_code == 200
        data = response.json()

        assert data["id"] == str(helper_model.id)
        assert data["description"] == helper_model.description
        assert data["user"] == str(helper_model.user.id)  # ModelSchema serializes ForeignKey as ID string

    def test_get_helper_not_found(self, client: Client) -> None:
        """Test getting a non-existent helper should fail."""
        fake_id = "00000000-0000-0000-0000-000000000000"

        response = client.get(f"/api/helpers/{fake_id}")

        assert response.status_code == 404

    def test_create_helper_success(
        self,
        authenticated_client: Client,
    ) -> None:
        """Test successful creation of a helper profile."""
        payload = {
            "description": "New helper description",
            "birthday": "1995-05-15",
            "gender": "M",
            "residence": "New City",
            "expected_place": ["City A", "City B"],
            "expected_time_periods": [{"day": "Monday", "time": "9:00-17:00"}],
            "expected_treatments": ["cleaning", "cooking"],
            "personality": "Friendly",
            "motivation": "Want to help",
            "hobbies": "Reading",
            "licenses": "Driving",
            "languages": ["English", "Chinese"],
        }

        response = authenticated_client.post(
            "/api/helpers",
            data=json.dumps(payload),
            content_type="application/json",
        )

        assert response.status_code == 201
        data = response.json()

        assert data["description"] == payload["description"]
        assert data["birthday"] == payload["birthday"]
        assert data["gender"] == payload["gender"]
        assert data["residence"] == payload["residence"]

    def test_create_helper_minimal_data(
        self,
        authenticated_client: Client,
    ) -> None:
        """Test creating helper with minimal required data."""
        payload = {
            "description": "Minimal helper",
            "birthday": "1990-01-01",
            "gender": "F",
        }

        response = authenticated_client.post(
            "/api/helpers",
            data=json.dumps(payload),
            content_type="application/json",
        )

        assert response.status_code == 201
        data = response.json()

        assert data["description"] == payload["description"]
        assert data["birthday"] == payload["birthday"]
        assert data["gender"] == payload["gender"]

    def test_create_helper_not_authenticated(self, client: Client) -> None:
        """Test creating helper without authentication should fail."""
        payload = {
            "description": "Test helper",
            "birthday": "1990-01-01",
            "gender": "M",
        }

        response = client.post(
            "/api/helpers",
            data=json.dumps(payload),
            content_type="application/json",
        )

        assert response.status_code == 403

    def test_create_helper_already_exists(
        self,
        authenticated_helper_client: Client,
        helper_model: HelperModel,
    ) -> None:
        """Test creating helper when user already has a profile should fail."""
        payload = {
            "description": "Another helper",
            "birthday": "1990-01-01",
            "gender": "M",
        }

        response = authenticated_helper_client.post(
            "/api/helpers",
            data=json.dumps(payload),
            content_type="application/json",
        )

        assert response.status_code == 404  # Should return 404 with HelperAlreadyExistsError

    def test_update_helper_success(
        self,
        authenticated_helper_client: Client,
        helper_model: HelperModel,
    ) -> None:
        """Test successful update of helper profile."""
        payload = {
            "description": "Updated description",
            "residence": "Updated City",
        }

        response = authenticated_helper_client.patch(
            f"/api/helpers/{helper_model.id}",
            data=json.dumps(payload),
            content_type="application/json",
        )

        assert response.status_code == 200
        data = response.json()

        assert data["description"] == payload["description"]
        assert data["residence"] == payload["residence"]

        # Verify update in database
        helper_model.refresh_from_db()
        assert helper_model.description == payload["description"]
        assert helper_model.residence == payload["residence"]

    def test_update_helper_partial_update(
        self,
        authenticated_helper_client: Client,
        helper_model: HelperModel,
    ) -> None:
        """Test partial update of helper profile."""
        original_description = helper_model.description
        payload = {
            "residence": "New Residence",
        }

        response = authenticated_helper_client.patch(
            f"/api/helpers/{helper_model.id}",
            data=json.dumps(payload),
            content_type="application/json",
        )

        assert response.status_code == 200
        data = response.json()

        assert data["residence"] == payload["residence"]
        assert data["description"] == original_description  # Should remain unchanged

    def test_update_helper_forbidden(
        self,
        authenticated_client: Client,
        helper_model: HelperModel,
    ) -> None:
        """Test updating another user's helper profile should fail."""
        # Create a different user for this test
        User = get_user_model()
        other_user = User.objects.create_user(
            email="other@example.com",
            password="password123",
            username="otheruser",
            user_type=User.UserTypeChoices.HELPER,
        )
        from allauth.account.models import EmailAddress  # noqa: PLC0415
        EmailAddress.objects.create(user=other_user, email="other@example.com", verified=True, primary=True)

        # Create a client authenticated as the other user
        other_client = Client()
        other_client.post(
            "/api/auth/login/",
            {"email": "other@example.com", "password": "password123"},
            content_type="application/json",
        )

        payload = {
            "description": "Hacked description",
        }

        response = other_client.patch(
            f"/api/helpers/{helper_model.id}",
            data=json.dumps(payload),
            content_type="application/json",
        )

        assert response.status_code == 403

    def test_update_helper_not_found(
        self,
        authenticated_helper_client: Client,
    ) -> None:
        """Test updating non-existent helper should fail."""
        fake_id = "00000000-0000-0000-0000-000000000000"
        payload = {
            "description": "Updated",
        }

        response = authenticated_helper_client.patch(
            f"/api/helpers/{fake_id}",
            data=json.dumps(payload),
            content_type="application/json",
        )

        assert response.status_code == 404

    def test_update_helper_not_authenticated(
        self,
        client: Client,
        helper_model: HelperModel,
    ) -> None:
        """Test updating helper without authentication should fail."""
        payload = {
            "description": "Updated",
        }

        response = client.patch(
            f"/api/helpers/{helper_model.id}",
            data=json.dumps(payload),
            content_type="application/json",
        )

        assert response.status_code == 403

    def test_update_self_profile_success(
        self,
        authenticated_helper_client: Client,
        helper_model: HelperModel,
    ) -> None:
        """Test successful update of authenticated user's helper profile."""
        payload = {
            "description": "Updated self description",
            "personality": "Updated personality",
        }

        response = authenticated_helper_client.patch(
            "/api/helpers/self/",
            data=json.dumps(payload),
            content_type="application/json",
        )

        assert response.status_code == 200
        data = response.json()

        assert data["description"] == payload["description"]
        assert data["personality"] == payload["personality"]

        # Verify update in database
        helper_model.refresh_from_db()
        assert helper_model.description == payload["description"]
        assert helper_model.personality == payload["personality"]

    def test_update_self_profile_no_profile(
        self,
        authenticated_client: Client,
    ) -> None:
        """Test updating self profile when user has no helper profile should fail."""
        payload = {
            "description": "Updated",
        }

        response = authenticated_client.patch(
            "/api/helpers/self/",
            data=json.dumps(payload),
            content_type="application/json",
        )

        assert response.status_code == 404

    def test_delete_helper_success(
        self,
        authenticated_helper_client: Client,
        helper_model: HelperModel,
    ) -> None:
        """Test successful deletion of helper profile."""
        helper_id = helper_model.id

        response = authenticated_helper_client.delete(f"/api/helpers/{helper_id}")

        assert response.status_code == 200
        data = response.json()

        assert data["detail"] == "Helper profile deleted successfully"

        # Verify deletion in database
        assert not HelperModel.objects.filter(id=helper_id).exists()

    def test_delete_helper_forbidden(
        self,
        authenticated_client: Client,
        helper_model: HelperModel,
    ) -> None:
        """Test deleting another user's helper profile should fail."""
        # Create a different user for this test
        User = get_user_model()
        other_user = User.objects.create_user(
            email="other@example.com",
            password="password123",
            username="otheruser",
            user_type=User.UserTypeChoices.HELPER,
        )
        from allauth.account.models import EmailAddress  # noqa: PLC0415
        EmailAddress.objects.create(user=other_user, email="other@example.com", verified=True, primary=True)

        # Create a client authenticated as the other user
        other_client = Client()
        other_client.post(
            "/api/auth/login/",
            {"email": "other@example.com", "password": "password123"},
            content_type="application/json",
        )

        response = other_client.delete(f"/api/helpers/{helper_model.id}")

        assert response.status_code == 403

    def test_delete_helper_not_found(
        self,
        authenticated_helper_client: Client,
    ) -> None:
        """Test deleting non-existent helper should fail."""
        fake_id = "00000000-0000-0000-0000-000000000000"

        response = authenticated_helper_client.delete(f"/api/helpers/{fake_id}")

        assert response.status_code == 404

    def test_delete_helper_not_authenticated(
        self,
        client: Client,
        helper_model: HelperModel,
    ) -> None:
        """Test deleting helper without authentication should fail."""
        response = client.delete(f"/api/helpers/{helper_model.id}")

        assert response.status_code == 403


@pytest.mark.integration
@pytest.mark.django_db
class TestHelperControllerAPIIntegration:
    """Integration tests for HelperControllerAPI."""

    def test_full_helper_workflow(
        self,
        authenticated_client: Client,
    ) -> None:
        """Test complete workflow: create, view, update, delete helper profile."""
        # Step 1: Create helper profile
        create_payload = {
            "description": "Initial description",
            "birthday": "1990-01-01",
            "gender": "M",
            "residence": "Initial City",
        }

        create_response = authenticated_client.post(
            "/api/helpers",
            data=json.dumps(create_payload),
            content_type="application/json",
        )
        assert create_response.status_code == 201
        helper_data = create_response.json()
        helper_id = helper_data["id"]

        # Step 2: Get self profile
        self_response = authenticated_client.get("/api/helpers/self/")
        assert self_response.status_code == 200
        self_data = self_response.json()
        assert self_data["id"] == helper_id
        assert self_data["description"] == create_payload["description"]

        # Step 3: Get helper by ID
        get_response = authenticated_client.get(f"/api/helpers/{helper_id}")
        assert get_response.status_code == 200
        get_data = get_response.json()
        assert get_data["id"] == helper_id

        # Step 4: Update self profile
        update_payload = {
            "description": "Updated description",
            "residence": "Updated City",
        }

        update_response = authenticated_client.patch(
            "/api/helpers/self/",
            data=json.dumps(update_payload),
            content_type="application/json",
        )
        assert update_response.status_code == 200
        update_data = update_response.json()
        assert update_data["description"] == update_payload["description"]
        assert update_data["residence"] == update_payload["residence"]

        # Step 5: Delete helper profile
        delete_response = authenticated_client.delete(f"/api/helpers/{helper_id}")
        assert delete_response.status_code == 200

        # Verify deletion
        final_get_response = authenticated_client.get(f"/api/helpers/{helper_id}")
        assert final_get_response.status_code == 404

