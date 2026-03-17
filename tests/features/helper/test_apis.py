import pytest

from features.helper.models import HelperModel


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
