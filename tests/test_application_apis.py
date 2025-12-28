"""Tests for Application APIs."""

import json
from datetime import date, timedelta

import pytest
from django.test import Client

from features.application.models import Application
from features.helper.models import HelperModel
from features.host.models import Host, Vacancy


@pytest.mark.django_db
class TestApplicationAPI:
    """Test cases for Application API endpoints."""

    def test_create_application_success(
        self,
        authenticated_helper_client: Client,
        helper_model: HelperModel,
        vacancy: Vacancy,
    ) -> None:
        """Test successful creation of an application."""
        payload = {
            "vacancy_id": str(vacancy.id),
            "start_date": str(date.today() + timedelta(days=30)),
            "end_date": str(date.today() + timedelta(days=120)),
        }

        response = authenticated_helper_client.post(
            "/api/applications",
            data=json.dumps(payload),
            content_type="application/json",
        )

        assert response.status_code == 201
        data = response.json()

        assert data["status"] == Application.StatusChoices.PENDING
        assert data["vacancy_id"] == str(vacancy.id)
        assert data["helper_id"] == str(helper_model.id)
        assert data["start_date"] == payload["start_date"]
        assert data["end_date"] == payload["end_date"]

    def test_create_application_not_authenticated(
        self,
        client: Client,
        vacancy: Vacancy,
    ) -> None:
        """Test creating application without authentication should fail."""
        payload = {
            "vacancy_id": str(vacancy.id),
            "start_date": str(date.today() + timedelta(days=30)),
            "end_date": str(date.today() + timedelta(days=120)),
        }

        response = client.post(
            "/api/applications",
            data=json.dumps(payload),
            content_type="application/json",
        )

        assert response.status_code == 403

    def test_create_application_no_helper_profile(
        self,
        authenticated_client: Client,
        vacancy: Vacancy,
    ) -> None:
        """Test creating application when user has no helper profile should fail."""
        payload = {
            "vacancy_id": str(vacancy.id),
            "start_date": str(date.today() + timedelta(days=30)),
            "end_date": str(date.today() + timedelta(days=120)),
        }

        response = authenticated_client.post(
            "/api/applications",
            data=json.dumps(payload),
            content_type="application/json",
        )

        assert response.status_code == 404

    def test_create_application_duplicate(
        self,
        authenticated_helper_client: Client,
        helper_model: HelperModel,
        vacancy: Vacancy,
    ) -> None:
        """Test creating duplicate application should fail."""
        # Create first application
        payload = {
            "vacancy_id": str(vacancy.id),
            "start_date": str(date.today() + timedelta(days=30)),
            "end_date": str(date.today() + timedelta(days=120)),
        }

        response1 = authenticated_helper_client.post(
            "/api/applications",
            data=json.dumps(payload),
            content_type="application/json",
        )
        assert response1.status_code == 201

        # Try to create duplicate
        response2 = authenticated_helper_client.post(
            "/api/applications",
            data=json.dumps(payload),
            content_type="application/json",
        )
        assert response2.status_code == 400

    def test_create_application_invalid_vacancy(
        self,
        authenticated_helper_client: Client,
    ) -> None:
        """Test creating application with invalid vacancy ID should fail."""
        payload = {
            "vacancy_id": "00000000-0000-0000-0000-000000000000",
            "start_date": str(date.today() + timedelta(days=30)),
            "end_date": str(date.today() + timedelta(days=120)),
        }

        response = authenticated_helper_client.post(
            "/api/applications",
            data=json.dumps(payload),
            content_type="application/json",
        )

        assert response.status_code == 404

    def test_get_self_applications_as_helper(
        self,
        authenticated_helper_client: Client,
        helper_model: HelperModel,
        vacancy: Vacancy,
    ) -> None:
        """Test getting applications where user is the helper."""
        # Create an application
        application = Application.objects.create(
            helper=helper_model,
            vacancy=vacancy,
            start_date=date.today() + timedelta(days=30),
            end_date=date.today() + timedelta(days=120),
            status=Application.StatusChoices.PENDING,
        )

        response = authenticated_helper_client.get("/api/applications/self/")

        assert response.status_code == 200
        data = response.json()

        assert len(data) == 1
        assert data[0]["id"] == str(application.id)
        assert data[0]["helper_id"] == str(helper_model.id)
        assert data[0]["vacancy_id"] == str(vacancy.id)

    def test_get_self_applications_as_host(
        self,
        authenticated_host_client: Client,
        host: Host,
        vacancy: Vacancy,
        helper_model: HelperModel,
    ) -> None:
        """Test getting applications where user is the vacancy host."""
        # Create an application from another helper
        application = Application.objects.create(
            helper=helper_model,
            vacancy=vacancy,
            start_date=date.today() + timedelta(days=30),
            end_date=date.today() + timedelta(days=120),
            status=Application.StatusChoices.PENDING,
        )

        response = authenticated_host_client.get("/api/applications/self/")

        assert response.status_code == 200
        data = response.json()

        assert len(data) == 1
        assert data[0]["id"] == str(application.id)

    def test_get_self_applications_empty(
        self,
        authenticated_helper_client: Client,
    ) -> None:
        """Test getting applications when user has none."""
        response = authenticated_helper_client.get("/api/applications/self/")

        assert response.status_code == 200
        data = response.json()

        assert data == []

    def test_get_application_success_as_helper(
        self,
        authenticated_helper_client: Client,
        helper_model: HelperModel,
        vacancy: Vacancy,
    ) -> None:
        """Test getting a specific application as the helper."""
        application = Application.objects.create(
            helper=helper_model,
            vacancy=vacancy,
            start_date=date.today() + timedelta(days=30),
            end_date=date.today() + timedelta(days=120),
            status=Application.StatusChoices.PENDING,
        )

        response = authenticated_helper_client.get(f"/api/applications/{application.id}")

        assert response.status_code == 200
        data = response.json()

        assert data["id"] == str(application.id)
        assert data["helper_id"] == str(helper_model.id)
        assert data["vacancy_id"] == str(vacancy.id)

    def test_get_application_success_as_host(
        self,
        authenticated_host_client: Client,
        host: Host,
        vacancy: Vacancy,
        helper_model: HelperModel,
    ) -> None:
        """Test getting a specific application as the vacancy host."""
        application = Application.objects.create(
            helper=helper_model,
            vacancy=vacancy,
            start_date=date.today() + timedelta(days=30),
            end_date=date.today() + timedelta(days=120),
            status=Application.StatusChoices.PENDING,
        )

        response = authenticated_host_client.get(f"/api/applications/{application.id}")

        assert response.status_code == 200
        data = response.json()

        assert data["id"] == str(application.id)

    def test_get_application_forbidden(
        self,
        authenticated_helper_client: Client,
        helper_model: HelperModel,
        vacancy: Vacancy,
    ) -> None:
        """Test getting an application user doesn't have access to should fail."""
        # Create another helper and application
        from django.contrib.auth import get_user_model

        User = get_user_model()
        other_user = User.objects.create_user(
            email="other@example.com",
            password="password123",
            username="otheruser",
            user_type=User.UserTypeChoices.HELPER,
        )
        # Verify email for the other user
        from allauth.account.models import EmailAddress  # noqa: PLC0415
        EmailAddress.objects.create(user=other_user, email="other@example.com", verified=True, primary=True)
        
        other_helper = HelperModel.objects.create(
            user_id=other_user.id,
            description="Other helper",
            birthday="1990-01-01",
            gender=HelperModel.GenderChoices.FEMALE,
        )

        application = Application.objects.create(
            helper=other_helper,
            vacancy=vacancy,
            start_date=date.today() + timedelta(days=30),
            end_date=date.today() + timedelta(days=120),
            status=Application.StatusChoices.PENDING,
        )

        response = authenticated_helper_client.get(f"/api/applications/{application.id}")

        assert response.status_code == 403

    def test_get_application_not_found(
        self,
        authenticated_helper_client: Client,
    ) -> None:
        """Test getting a non-existent application should fail."""
        fake_id = "00000000-0000-0000-0000-000000000000"

        response = authenticated_helper_client.get(f"/api/applications/{fake_id}")

        assert response.status_code == 404

    def test_withdraw_application_success(
        self,
        authenticated_helper_client: Client,
        helper_model: HelperModel,
        vacancy: Vacancy,
    ) -> None:
        """Test successfully withdrawing an application."""
        application = Application.objects.create(
            helper=helper_model,
            vacancy=vacancy,
            start_date=date.today() + timedelta(days=30),
            end_date=date.today() + timedelta(days=120),
            status=Application.StatusChoices.PENDING,
        )

        response = authenticated_helper_client.delete(f"/api/applications/{application.id}")

        assert response.status_code == 200
        data = response.json()

        assert data["detail"] == "Application withdrawn successfully"

        # Verify status was updated
        application.refresh_from_db()
        assert application.status == Application.StatusChoices.WITHDRAWN

    def test_withdraw_application_forbidden(
        self,
        authenticated_host_client: Client,
        helper_model: HelperModel,
        vacancy: Vacancy,
    ) -> None:
        """Test withdrawing an application as host should fail."""
        application = Application.objects.create(
            helper=helper_model,
            vacancy=vacancy,
            start_date=date.today() + timedelta(days=30),
            end_date=date.today() + timedelta(days=120),
            status=Application.StatusChoices.PENDING,
        )

        response = authenticated_host_client.delete(f"/api/applications/{application.id}")

        assert response.status_code == 403

    def test_withdraw_application_not_found(
        self,
        authenticated_helper_client: Client,
    ) -> None:
        """Test withdrawing a non-existent application should fail."""
        fake_id = "00000000-0000-0000-0000-000000000000"

        response = authenticated_helper_client.delete(f"/api/applications/{fake_id}")

        assert response.status_code == 404

    def test_update_application_status_accept_success(
        self,
        authenticated_host_client: Client,
        host: Host,
        vacancy: Vacancy,
        helper_model: HelperModel,
    ) -> None:
        """Test successfully accepting an application."""
        application = Application.objects.create(
            helper=helper_model,
            vacancy=vacancy,
            start_date=date.today() + timedelta(days=30),
            end_date=date.today() + timedelta(days=120),
            status=Application.StatusChoices.PENDING,
        )

        payload = {"status": Application.StatusChoices.ACCEPTED}

        response = authenticated_host_client.patch(
            f"/api/applications/{application.id}/status",
            data=json.dumps(payload),
            content_type="application/json",
        )

        assert response.status_code == 200
        data = response.json()

        assert data["status"] == Application.StatusChoices.ACCEPTED

        # Verify status was updated
        application.refresh_from_db()
        assert application.status == Application.StatusChoices.ACCEPTED

    def test_update_application_status_reject_success(
        self,
        authenticated_host_client: Client,
        host: Host,
        vacancy: Vacancy,
        helper_model: HelperModel,
    ) -> None:
        """Test successfully rejecting an application."""
        application = Application.objects.create(
            helper=helper_model,
            vacancy=vacancy,
            start_date=date.today() + timedelta(days=30),
            end_date=date.today() + timedelta(days=120),
            status=Application.StatusChoices.PENDING,
        )

        payload = {"status": Application.StatusChoices.REJECTED}

        response = authenticated_host_client.patch(
            f"/api/applications/{application.id}/status",
            data=json.dumps(payload),
            content_type="application/json",
        )

        assert response.status_code == 200
        data = response.json()

        assert data["status"] == Application.StatusChoices.REJECTED

        # Verify status was updated
        application.refresh_from_db()
        assert application.status == Application.StatusChoices.REJECTED

    def test_update_application_status_forbidden_as_helper(
        self,
        authenticated_helper_client: Client,
        helper_model: HelperModel,
        vacancy: Vacancy,
    ) -> None:
        """Test updating application status as helper should fail."""
        application = Application.objects.create(
            helper=helper_model,
            vacancy=vacancy,
            start_date=date.today() + timedelta(days=30),
            end_date=date.today() + timedelta(days=120),
            status=Application.StatusChoices.PENDING,
        )

        payload = {"status": Application.StatusChoices.ACCEPTED}

        response = authenticated_helper_client.patch(
            f"/api/applications/{application.id}/status",
            data=json.dumps(payload),
            content_type="application/json",
        )

        assert response.status_code == 403

    def test_update_application_status_invalid_status(
        self,
        authenticated_host_client: Client,
        host: Host,
        vacancy: Vacancy,
        helper_model: HelperModel,
    ) -> None:
        """Test updating application status with invalid status should fail."""
        application = Application.objects.create(
            helper=helper_model,
            vacancy=vacancy,
            start_date=date.today() + timedelta(days=30),
            end_date=date.today() + timedelta(days=120),
            status=Application.StatusChoices.PENDING,
        )

        payload = {"status": Application.StatusChoices.PENDING}

        response = authenticated_host_client.patch(
            f"/api/applications/{application.id}/status",
            data=json.dumps(payload),
            content_type="application/json",
        )

        assert response.status_code == 403

    def test_update_application_status_not_found(
        self,
        authenticated_host_client: Client,
    ) -> None:
        """Test updating status of non-existent application should fail."""
        fake_id = "00000000-0000-0000-0000-000000000000"
        payload = {"status": Application.StatusChoices.ACCEPTED}

        response = authenticated_host_client.patch(
            f"/api/applications/{fake_id}/status",
            data=json.dumps(payload),
            content_type="application/json",
        )

        assert response.status_code == 404


@pytest.mark.integration
@pytest.mark.django_db
class TestApplicationAPIIntegration:
    """Integration tests for Application API."""

    def test_full_application_workflow(
        self,
        helper_model: HelperModel,
        authenticated_helper_client: Client,
        authenticated_host_client: Client,
        host: Host,
        vacancy: Vacancy,
    ) -> None:
        """Test complete workflow: create, view, update status, withdraw."""
        # Ensure helper_model exists and is accessible
        # Refresh to ensure it's in the database
        helper_model.refresh_from_db()
        user = helper_model.user
        
        # Verify HelperModel exists for this user
        assert HelperModel.objects.filter(user=user).exists(), f"HelperModel should exist for user {user.id} ({user.email})"
        
        # Verify we can query it the same way the API does (using user_id like the API now does)
        found_helper = HelperModel.objects.filter(user_id=user.id).first()
        assert found_helper is not None, f"Could not find HelperModel for user {user.id} using user_id"
        assert found_helper.id == helper_model.id, "Found helper should match fixture"
        
        # Step 1: Helper creates application
        # Note: The authenticated_helper_client should have authenticated with helper_model.user
        # The API now uses user_id=user.id to find the HelperModel
        create_payload = {
            "vacancy_id": str(vacancy.id),
            "start_date": str(date.today() + timedelta(days=30)),
            "end_date": str(date.today() + timedelta(days=120)),
        }

        create_response = authenticated_helper_client.post(
            "/api/applications",
            data=json.dumps(create_payload),
            content_type="application/json",
        )
        assert create_response.status_code == 201
        application_data = create_response.json()
        application_id = application_data["id"]

        # Step 2: Helper views their application
        helper_view_response = authenticated_helper_client.get(f"/api/applications/{application_id}")
        assert helper_view_response.status_code == 200

        # Step 3: Host views the application
        host_view_response = authenticated_host_client.get(f"/api/applications/{application_id}")
        assert host_view_response.status_code == 200

        # Step 4: Host accepts the application
        accept_payload = {"status": Application.StatusChoices.ACCEPTED}
        accept_response = authenticated_host_client.patch(
            f"/api/applications/{application_id}/status",
            data=json.dumps(accept_payload),
            content_type="application/json",
        )
        assert accept_response.status_code == 200
        assert accept_response.json()["status"] == Application.StatusChoices.ACCEPTED

        # Step 5: Helper withdraws the application
        withdraw_response = authenticated_helper_client.delete(f"/api/applications/{application_id}")
        assert withdraw_response.status_code == 200

        # Verify final state
        application = Application.objects.get(id=application_id)
        assert application.status == Application.StatusChoices.WITHDRAWN

