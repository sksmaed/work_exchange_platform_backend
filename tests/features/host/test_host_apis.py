import datetime

import pytest

from features.host.models import Host, Vacancy, VacancyAvailability


@pytest.fixture
def host_user(django_user_model):
    return django_user_model.objects.create_user(
        username="test_host",
        email="host@example.com",
        password="password123",
        user_type="Host",
    )


@pytest.fixture
def other_user(django_user_model):
    return django_user_model.objects.create_user(
        username="test_other",
        email="other@example.com",
        password="password123",
        user_type="Host",
    )


@pytest.fixture
def test_host(host_user):
    host = Host(
        user=host_user,
        description="A great place to stay.",
        address="123 Ocean Drive",
        type="Guesthouse",
    )
    host.save(user=host_user)
    return host


@pytest.fixture
def test_vacancy(test_host, host_user):
    vacancy = Vacancy(
        host=test_host,
        name="Housekeeping Assistant",
        work_time="Morning 8AM-12PM",
        description="Help with cleaning rooms.",
        expected_duration="1 Month",
        expected_age="18-30",
        expected_gender="Any",
        expected_licenses="None",
        expected_personality="Hardworking",
        expected_other_requirements="None",
    )
    vacancy.save(user=host_user)
    return vacancy


@pytest.mark.django_db
class TestHostAPI:
    def test_list_hosts_no_filters(self, client, host_user, test_host):
        client.force_login(host_user)
        url = "/api/hosts"

        response = client.get(url)
        assert response.status_code == 200
        data = response.json()
        assert data["count"] == 1
        assert data["items"][0]["address"] == test_host.address

    def test_list_hosts_month_filter(self, client, host_user, test_host, test_vacancy):
        # Create availability for August
        VacancyAvailability.objects.create(
            vacancy=test_vacancy,
            start_date=datetime.date(2023, 8, 1),
            end_date=datetime.date(2023, 8, 31),
            capacity=1,
            current_helpers=0,
            created_by_user=host_user,
            updated_by_user=host_user,
        )

        client.force_login(host_user)

        # Test for a month with availability
        url = "/api/hosts?month=8"
        response = client.get(url)
        assert response.status_code == 200
        data = response.json()
        assert data["count"] == 1
        assert data["items"][0]["id"] == str(test_host.id)

        # Test for a month without availability
        url = "/api/hosts?month=9"
        response = client.get(url)
        assert response.status_code == 200
        data = response.json()
        assert data["count"] == 0
