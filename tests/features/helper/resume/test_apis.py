"""Tests for HelperResumeAPI."""

import json
from typing import Any

import pytest
from django.test import Client

from features.helper.models import HelperModel
from features.helper.resume.models import HelperResume


@pytest.mark.django_db
class TestHelperResumeAPI:
    """Test cases for HelperResumeAPI."""

    def test_get_self_resume_success(
        self,
        authenticated_helper_client: Client,
        helper_resume: HelperResume,
    ) -> None:
        """Test successful retrieval of user's own resume."""
        response = authenticated_helper_client.get("/api/helper/resume/self/")

        assert response.status_code == 200
        data = response.json()

        assert data["id"] == str(helper_resume.id)
        assert data["title"] == helper_resume.title
        assert data["summary"] == helper_resume.summary
        assert data["experiences"] == helper_resume.experiences
        assert data["skills"] == helper_resume.skills
        assert data["certifications"] == helper_resume.certifications
        assert data["availability"] == helper_resume.availability
        assert data["preferred_locations"] == helper_resume.preferred_locations
        assert data["contact_email"] == helper_resume.contact_email
        assert data["contact_phone"] == helper_resume.contact_phone

    def test_get_self_resume_not_authenticated(self, client: Client) -> None:
        """Test get resume without authentication should fail."""
        response = client.get("/api/helper/resume/self/")
        assert response.status_code == 403

    def test_get_self_resume_no_helper_profile(
        self,
        authenticated_client: Client,
    ) -> None:
        """Test get resume when user has no helper profile should return 404."""
        response = authenticated_client.get("/api/helper/resume/self/")
        assert response.status_code == 404

    def test_get_self_resume_no_resume(
        self,
        authenticated_helper_client: Client,
        helper_model: HelperModel,
    ) -> None:
        """Test get resume when helper has no resume should return 404."""
        # Ensure no resume exists for this helper
        HelperResume.objects.filter(helper=helper_model).delete()

        response = authenticated_helper_client.get("/api/helper/resume/self/")
        assert response.status_code == 404

    def test_create_resume_success(
        self,
        authenticated_helper_client: Client,
        helper_model: HelperModel,
    ) -> None:
        """Test successful creation of a new resume."""
        # Ensure no existing resume
        HelperResume.objects.filter(helper=helper_model).delete()

        payload = {
            "title": "Professional Helper",
            "summary": "Experienced in various helper tasks",
            "experiences": [{"title": "Home Assistant", "company": "ABC Family", "duration": "2 years"}],
            "skills": ["Cleaning", "Cooking"],
            "certifications": ["First Aid"],
            "availability": [{"day": "Monday", "time": "9:00-17:00"}],
            "preferred_locations": ["Taipei"],
            "contact_email": "test@example.com",
            "contact_phone": "+886912345678",
        }

        response = authenticated_helper_client.post(
            "/api/helper/resume/",
            data=json.dumps(payload),
            content_type="application/json",
        )

        assert response.status_code == 201
        data = response.json()

        assert data["title"] == payload["title"]
        assert data["summary"] == payload["summary"]
        assert data["experiences"] == payload["experiences"]
        assert data["skills"] == payload["skills"]
        assert data["certifications"] == payload["certifications"]
        assert data["availability"] == payload["availability"]
        assert data["preferred_locations"] == payload["preferred_locations"]
        assert data["contact_email"] == payload["contact_email"]
        assert data["contact_phone"] == payload["contact_phone"]

    def test_create_resume_minimal_data(
        self,
        authenticated_helper_client: Client,
        helper_model: HelperModel,
    ) -> None:
        """Test creating resume with minimal data (all optional fields)."""
        # Ensure no existing resume
        HelperResume.objects.filter(helper=helper_model).delete()

        payload: dict[str, Any] = {}

        response = authenticated_helper_client.post(
            "/api/helper/resume/",
            data=json.dumps(payload),
            content_type="application/json",
        )

        assert response.status_code == 201
        data = response.json()

        # Check default values are applied
        assert data["title"] == ""
        assert data["summary"] == ""
        assert data["experiences"] == []
        assert data["skills"] == []
        assert data["certifications"] == []
        assert data["availability"] == []
        assert data["preferred_locations"] == []
        assert data["contact_email"] in (None, "")
        assert data["contact_phone"] == ""

    def test_create_resume_not_authenticated(self, client: Client) -> None:
        """Test creating resume without authentication should fail."""
        payload = {"title": "Test Resume"}

        response = client.post(
            "/api/helper/resume/",
            data=json.dumps(payload),
            content_type="application/json",
        )
        assert response.status_code == 403

    def test_create_resume_no_helper_profile(
        self,
        authenticated_client: Client,
    ) -> None:
        """Test creating resume when user has no helper profile should return 404."""
        payload = {"title": "Test Resume"}

        response = authenticated_client.post(
            "/api/helper/resume/",
            data=json.dumps(payload),
            content_type="application/json",
        )
        assert response.status_code == 404

    def test_update_resume_success(
        self,
        authenticated_helper_client: Client,
        helper_resume: HelperResume,
    ) -> None:
        """Test successful update of existing resume."""
        updated_data = {
            "title": "Updated Professional Helper",
            "summary": "Updated summary with more details",
            "skills": ["Advanced Cleaning", "Gourmet Cooking", "Elder Care"],
        }

        response = authenticated_helper_client.put(
            "/api/helper/resume/",
            data=json.dumps(updated_data),
            content_type="application/json",
        )

        assert response.status_code == 200
        data = response.json()

        assert data["title"] == updated_data["title"]
        assert data["summary"] == updated_data["summary"]
        assert data["skills"] == updated_data["skills"]
        # Other fields should remain unchanged
        assert data["experiences"] == helper_resume.experiences
        assert data["certifications"] == helper_resume.certifications

    def test_update_resume_partial_update(
        self,
        authenticated_helper_client: Client,
        helper_resume: HelperResume,
    ) -> None:
        """Test partial update of resume (only some fields)."""
        original_title = helper_resume.title
        original_summary = helper_resume.summary

        updated_data = {
            "contact_phone": "+886987654321",
            "preferred_locations": ["Taichung", "Kaohsiung"],
        }

        response = authenticated_helper_client.put(
            "/api/helper/resume/",
            data=json.dumps(updated_data),
            content_type="application/json",
        )

        assert response.status_code == 200
        data = response.json()

        # Updated fields
        assert data["contact_phone"] == updated_data["contact_phone"]
        assert data["preferred_locations"] == updated_data["preferred_locations"]

        # Unchanged fields
        assert data["title"] == original_title
        assert data["summary"] == original_summary

    def test_update_resume_with_null_values(
        self,
        authenticated_helper_client: Client,
        helper_resume: HelperResume,
    ) -> None:
        """Test update resume with null values (should be ignored)."""
        original_title = helper_resume.title

        updated_data = {
            "title": None,  # Should be ignored
            "summary": "Updated summary",  # Should be applied
        }

        response = authenticated_helper_client.put(
            "/api/helper/resume/",
            data=json.dumps(updated_data),
            content_type="application/json",
        )

        assert response.status_code == 200
        data = response.json()

        # Null field should remain unchanged
        assert data["title"] == original_title
        # Non-null field should be updated
        assert data["summary"] == updated_data["summary"]

    def test_update_resume_not_authenticated(self, client: Client) -> None:
        """Test updating resume without authentication should fail."""
        updated_data = {"title": "Updated Title"}

        response = client.put(
            "/api/helper/resume/",
            data=json.dumps(updated_data),
            content_type="application/json",
        )
        assert response.status_code == 403

    def test_update_resume_no_helper_profile(
        self,
        authenticated_client: Client,
    ) -> None:
        """Test updating resume when user has no helper profile should return 404."""
        updated_data = {"title": "Updated Title"}

        response = authenticated_client.put(
            "/api/helper/resume/",
            data=json.dumps(updated_data),
            content_type="application/json",
        )
        assert response.status_code == 404

    def test_update_resume_no_existing_resume(
        self,
        authenticated_helper_client: Client,
        helper_model: HelperModel,
    ) -> None:
        """Test updating resume when no resume exists should return 404."""
        # Delete existing resume
        HelperResume.objects.filter(helper=helper_model).delete()

        updated_data = {"title": "Updated Title"}

        response = authenticated_helper_client.put(
            "/api/helper/resume/",
            data=json.dumps(updated_data),
            content_type="application/json",
        )
        assert response.status_code == 404


@pytest.mark.integration
@pytest.mark.django_db
class TestHelperResumeAPIIntegration:
    """Integration tests for HelperResumeAPI."""

    def test_full_resume_workflow(
        self,
        authenticated_helper_client: Client,
        helper_model: HelperModel,
    ) -> None:
        """Test complete workflow: create, read, update resume."""
        # Ensure no existing resume
        HelperResume.objects.filter(helper=helper_model).delete()

        # Step 1: Create resume
        create_payload = {
            "title": "Initial Resume",
            "summary": "Initial summary",
            "skills": ["Skill1", "Skill2"],
        }

        create_response = authenticated_helper_client.post(
            "/api/helper/resume/",
            data=json.dumps(create_payload),
            content_type="application/json",
        )
        assert create_response.status_code == 201

        # Step 2: Read resume
        read_response = authenticated_helper_client.get("/api/helper/resume/self/")
        assert read_response.status_code == 200

        created_data = read_response.json()
        assert created_data["title"] == create_payload["title"]

        # Step 3: Update resume
        update_payload = {
            "title": "Updated Resume",
            "skills": ["Updated Skill1", "Updated Skill2", "New Skill"],
        }

        update_response = authenticated_helper_client.put(
            "/api/helper/resume/",
            data=json.dumps(update_payload),
            content_type="application/json",
        )
        assert update_response.status_code == 200

        # Step 4: Verify update
        final_response = authenticated_helper_client.get("/api/helper/resume/self/")
        assert final_response.status_code == 200

        final_data = final_response.json()
        assert final_data["title"] == update_payload["title"]
        assert final_data["skills"] == update_payload["skills"]
        # Summary should remain unchanged from original
        assert final_data["summary"] == create_payload["summary"]
