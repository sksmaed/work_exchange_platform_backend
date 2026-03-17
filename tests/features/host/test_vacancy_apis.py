import pytest

from features.host.models import Host, Vacancy


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
class TestVacancyAPI:
    def test_create_vacancy_success(self, client, host_user, test_host):
        client.force_login(host_user)
        url = f"/api/hosts/{test_host.id}/vacancies"
        payload = {
            "host_id": str(test_host.id),
            "name": "Receptionist",
            "work_time": "Afternoon 1PM-5PM",
            "description": "Welcome guests.",
            "expected_duration": "2 Months",
            "expected_age": "20+",
            "expected_gender": "Any",
            "expected_licenses": "None",
            "expected_personality": "Friendly",
            "expected_other_requirements": "English speaking",
            "status": "Recruiting",
        }

        response = client.post(url, data=payload, content_type="application/json")
        assert response.status_code == 201

        vacancy = Vacancy.objects.get(name="Receptionist")
        assert vacancy.description == "Welcome guests."
        assert vacancy.host == test_host

    def test_create_vacancy_unauthorized(self, client, other_user, test_host):
        client.force_login(other_user)
        url = f"/api/hosts/{test_host.id}/vacancies"
        payload = {
            "host_id": str(test_host.id),
            "name": "Receptionist",
            "work_time": "Afternoon 1PM-5PM",
            "description": "Welcome guests.",
            "expected_duration": "2 Months",
            "expected_age": "20+",
            "expected_gender": "Any",
            "expected_licenses": "None",
            "expected_personality": "Friendly",
            "expected_other_requirements": "English speaking",
        }

        response = client.post(url, data=payload, content_type="application/json")
        assert response.status_code == 403

    def test_list_vacancies(self, client, host_user, test_host, test_vacancy):
        client.force_login(host_user)
        url = f"/api/hosts/{test_host.id}/vacancies"

        response = client.get(url)
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["name"] == "Housekeeping Assistant"

    def test_update_vacancy_success(self, client, host_user, test_vacancy):
        client.force_login(host_user)
        url = f"/api/hosts/vacancies/{test_vacancy.id}"
        payload = {"work_time": "Morning 9AM-1PM", "status": "Full"}

        response = client.patch(url, data=payload, content_type="application/json")
        assert response.status_code == 200

        test_vacancy.refresh_from_db()
        assert test_vacancy.work_time == "Morning 9AM-1PM"
        assert test_vacancy.status == "Full"

    def test_delete_vacancy_success(self, client, host_user, test_vacancy):
        client.force_login(host_user)
        url = f"/api/hosts/vacancies/{test_vacancy.id}"

        response = client.delete(url)
        assert response.status_code == 200
        assert Vacancy.objects.count() == 0
