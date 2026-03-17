import json
from datetime import date

import pytest
from django.test import Client

from features.application.models import Application
from features.host.models import Host, Vacancy, VacancyAvailability


@pytest.fixture
@pytest.mark.django_db
def test_host(superuser) -> Host:
    host = Host(
        user=superuser,
        name="Test Host",
        description="A nice place",
        address="123 Road",
        type="Hostel",
    )
    host.save(user=superuser)
    return host


@pytest.fixture
@pytest.mark.django_db
def test_vacancy(test_host) -> Vacancy:
    return Vacancy.objects.create(
        host=test_host,
        name="Test Vacancy",
        status=Vacancy.StatusChoices.RECRUITING,
    )


@pytest.fixture
@pytest.mark.django_db
def test_vacancy_availability(test_vacancy) -> VacancyAvailability:
    return VacancyAvailability.objects.create(
        vacancy=test_vacancy,
        start_date=date(2025, 5, 1),
        end_date=date(2025, 5, 31),
        capacity=2,
        current_helpers=0,
    )


class TestApplicationAPI:
    @pytest.mark.django_db
    def test_create_application_success(
        self,
        authenticated_helper_client: Client,
        test_vacancy: Vacancy,
        test_vacancy_availability: VacancyAvailability,
        helper_model,
    ):
        """Helper applies within the valid availability period."""
        payload = {"vacancy_id": str(test_vacancy.id), "start_date": "2025-05-10", "end_date": "2025-05-20"}
        response = authenticated_helper_client.post(
            "/api/applications/",
            data=json.dumps(payload),
            content_type="application/json",
        )
        assert response.status_code == 201
        assert Application.objects.filter(vacancy=test_vacancy, helper=helper_model).exists()

    @pytest.mark.django_db
    def test_create_application_invalid_dates(
        self,
        authenticated_helper_client: Client,
        test_vacancy: Vacancy,
        test_vacancy_availability: VacancyAvailability,
    ):
        """Helper applies outside of the valid availability period."""
        payload = {
            "vacancy_id": str(test_vacancy.id),
            "start_date": "2025-04-20",  # Starts before availability
            "end_date": "2025-05-10",
        }
        response = authenticated_helper_client.post(
            "/api/applications/",
            data=json.dumps(payload),
            content_type="application/json",
        )
        assert response.status_code == 400
        response_json = response.json()
        assert "not available" in response_json["message"]

    @pytest.mark.django_db
    def test_create_application_full_capacity(
        self,
        authenticated_helper_client: Client,
        test_vacancy: Vacancy,
        test_vacancy_availability: VacancyAvailability,
    ):
        """Helper applies when capacity is full."""
        # Fill capacity
        test_vacancy_availability.current_helpers = 2
        test_vacancy_availability.save()

        payload = {"vacancy_id": str(test_vacancy.id), "start_date": "2025-05-10", "end_date": "2025-05-20"}
        response = authenticated_helper_client.post(
            "/api/applications/",
            data=json.dumps(payload),
            content_type="application/json",
        )
        assert response.status_code == 400
        response_json = response.json()
        assert "not available" in response_json["message"]
