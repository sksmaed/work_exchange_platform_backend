import json
from datetime import date

import pytest
from django.contrib.auth import get_user_model
from django.test import Client

from features.application.models import Application
from features.calendar.models import CalendarEvent
from features.helper.models import HelperModel
from features.host.models import Host, Vacancy, VacancyAvailability

User = get_user_model()

TEST_HOST_EMAIL = "calendar_host@example.com"
TEST_HOST_PASSWORD = "hostpassword123"  # noqa: S105
TEST_HELPER_EMAIL = "calendar_helper@example.com"
TEST_HELPER_PASSWORD = "helperpassword123"  # noqa: S105


@pytest.fixture
@pytest.mark.django_db
def host_user(db):
    """Create a host user."""
    return User.objects.create_user(
        username="calendar_host_user",
        email=TEST_HOST_EMAIL,
        password=TEST_HOST_PASSWORD,
        user_type="Host",
    )


@pytest.fixture
@pytest.mark.django_db
def helper_user(db):
    """Create a helper user."""
    return User.objects.create_user(
        username="calendar_helper_user",
        email=TEST_HELPER_EMAIL,
        password=TEST_HELPER_PASSWORD,
        user_type="Helper",
    )


@pytest.fixture
@pytest.mark.django_db
def test_host(host_user):
    """Create a test host."""
    host = Host(
        user=host_user,
        name="Calendar Test Host",
        description="A host for calendar tests",
        address="42 Test Lane",
        type="Farmhouse",
    )
    host.save(user=host_user)
    return host


@pytest.fixture
@pytest.mark.django_db
def test_vacancy(test_host, host_user):
    """Create a test vacancy."""
    vacancy = Vacancy(
        host=test_host,
        name="Calendar Test Vacancy",
        work_time="9AM-5PM",
        description="Calendar testing vacancy",
        expected_duration="1 Month",
        expected_age="Any",
        expected_gender="Any",
        expected_licenses="None",
        expected_personality="Flexible",
        expected_other_requirements="None",
        status=Vacancy.StatusChoices.RECRUITING,
    )
    vacancy.save(user=host_user)
    return vacancy


@pytest.fixture
@pytest.mark.django_db
def test_vacancy_availability(test_vacancy):
    """Create a VacancyAvailability for the test vacancy."""
    return VacancyAvailability.objects.create(
        vacancy=test_vacancy,
        start_date=date(2025, 6, 1),
        end_date=date(2025, 6, 30),
        capacity=3,
        current_helpers=0,
    )


@pytest.fixture
@pytest.mark.django_db
def test_helper(helper_user):
    """Create a helper profile for the helper user."""
    helper = HelperModel(
        user=helper_user,
        description="Test calendar helper",
        birthday="1995-03-10",
        gender=HelperModel.GenderChoices.FEMALE,
        residence="Test City",
        expected_place=["City X"],
        expected_time_periods=[{"start_date": "2025-06-01", "end_date": "2025-06-30"}],
        expected_treatments=["gardening"],
        personality="Calm",
        motivation="Love nature",
        hobbies="Hiking",
        licenses=HelperModel.LicenseChoices.NONE,
        languages=["English"],
        avg_rating=4.0,
    )
    helper.save(user=helper_user)
    return helper


@pytest.fixture
@pytest.mark.django_db
def test_accepted_application(test_helper, test_vacancy, test_vacancy_availability, host_user):
    """Create an accepted Application, with a CalendarEvent created."""
    application = Application.objects.create(
        helper=test_helper,
        vacancy=test_vacancy,
        start_date=date(2025, 6, 5),
        end_date=date(2025, 6, 20),
        status=Application.StatusChoices.ACCEPTED,
    )
    # Manually create the calendar event to represent the accepted state
    CalendarEvent.objects.create(
        host=test_vacancy.host,
        helper=test_helper,
        application=application,
        start_date=application.start_date,
        end_date=application.end_date,
        remarks=f"Application accepted for {test_vacancy.name}.",
    )
    test_vacancy_availability.current_helpers = 1
    test_vacancy_availability.save()
    return application


@pytest.fixture
def host_client(host_user):
    """Return a client authenticated as the host user."""
    client = Client()
    response = client.post(
        "/api/auth/login/",
        {"email": TEST_HOST_EMAIL, "password": TEST_HOST_PASSWORD},
        content_type="application/json",
    )
    assert response.status_code == 200, f"Host login failed: {response.content}"
    client.cookies.update(response.cookies)
    return client


@pytest.fixture
def helper_client(helper_user):
    """Return a client authenticated as the helper user."""
    client = Client()
    response = client.post(
        "/api/auth/login/",
        {"email": TEST_HELPER_EMAIL, "password": TEST_HELPER_PASSWORD},
        content_type="application/json",
    )
    assert response.status_code == 200, f"Helper login failed: {response.content}"
    client.cookies.update(response.cookies)
    return client


@pytest.mark.django_db
class TestCalendarAPI:
    def test_list_calendar_events_by_host(
        self,
        host_client: Client,
        test_host: Host,
        test_accepted_application: Application,
    ):
        """Host can list their own calendar events."""
        url = f"/api/calendar/hosts/{test_host.id}/events"
        response = host_client.get(url)

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 1
        assert data[0]["start_date"] == "2025-06-05"
        assert data[0]["end_date"] == "2025-06-20"

    def test_list_calendar_events_forbidden_for_other_user(
        self,
        helper_client: Client,
        test_host: Host,
        test_accepted_application: Application,
    ):
        """Non-owner cannot view a host's calendar events."""
        url = f"/api/calendar/hosts/{test_host.id}/events"
        response = helper_client.get(url)

        assert response.status_code == 403

    def test_update_calendar_event(
        self,
        host_client: Client,
        test_host: Host,
        test_accepted_application: Application,
    ):
        """Host can update a calendar event's dates and remarks."""
        event = CalendarEvent.objects.get(application=test_accepted_application)

        url = f"/api/calendar/events/{event.id}"
        payload = {
            "start_date": "2025-06-10",
            "end_date": "2025-06-25",
            "remarks": "Adjusted dates by host.",
        }
        response = host_client.patch(url, data=json.dumps(payload), content_type="application/json")

        assert response.status_code == 200
        data = response.json()
        assert data["start_date"] == "2025-06-10"
        assert data["end_date"] == "2025-06-25"
        assert data["remarks"] == "Adjusted dates by host."

        # Confirm DB was updated
        event.refresh_from_db()
        assert event.start_date == date(2025, 6, 10)
        assert event.remarks == "Adjusted dates by host."

    def test_update_calendar_event_forbidden_for_non_owner(
        self,
        helper_client: Client,
        test_host: Host,
        test_accepted_application: Application,
    ):
        """Non-host-owner cannot edit the calendar event."""
        event = CalendarEvent.objects.get(application=test_accepted_application)

        url = f"/api/calendar/events/{event.id}"
        payload = {"remarks": "Trying to change remarks"}
        response = helper_client.patch(url, data=json.dumps(payload), content_type="application/json")

        assert response.status_code == 403

    def test_delete_calendar_event(
        self,
        host_client: Client,
        test_accepted_application: Application,
    ):
        """Host can delete a calendar event manually."""
        event = CalendarEvent.objects.get(application=test_accepted_application)
        event_id = event.id

        url = f"/api/calendar/events/{event_id}"
        response = host_client.delete(url)

        assert response.status_code == 200
        assert not CalendarEvent.objects.filter(id=event_id).exists()

    def test_delete_calendar_event_forbidden_for_non_owner(
        self,
        helper_client: Client,
        test_accepted_application: Application,
    ):
        """Non-host-owner cannot delete the calendar event."""
        event = CalendarEvent.objects.get(application=test_accepted_application)
        url = f"/api/calendar/events/{event.id}"
        response = helper_client.delete(url)

        assert response.status_code == 403
        assert CalendarEvent.objects.filter(id=event.id).exists()

    def test_accept_application_creates_calendar_event(
        self,
        host_client: Client,
        test_helper: HelperModel,
        test_vacancy: Vacancy,
        test_vacancy_availability: VacancyAvailability,
    ):
        """Accepting an application should automatically create a CalendarEvent."""
        application = Application.objects.create(
            helper=test_helper,
            vacancy=test_vacancy,
            start_date=date(2025, 6, 5),
            end_date=date(2025, 6, 20),
            status=Application.StatusChoices.PENDING,
        )

        assert not CalendarEvent.objects.filter(application=application).exists()

        url = f"/api/applications/{application.id}/status"
        response = host_client.patch(
            url, data=json.dumps({"status": Application.StatusChoices.ACCEPTED}), content_type="application/json"
        )
        assert response.status_code == 200

        assert CalendarEvent.objects.filter(application=application).exists()
        event = CalendarEvent.objects.get(application=application)
        assert event.host == test_vacancy.host
        assert event.helper == test_helper
        assert event.start_date == date(2025, 6, 5)
        assert event.end_date == date(2025, 6, 20)

    def test_reject_accepted_application_deletes_calendar_event(
        self,
        host_client: Client,
        test_accepted_application: Application,
    ):
        """Rejecting a previously accepted application should delete the CalendarEvent."""
        assert CalendarEvent.objects.filter(application=test_accepted_application).exists()

        url = f"/api/applications/{test_accepted_application.id}/status"
        response = host_client.patch(
            url,
            data=json.dumps({"status": Application.StatusChoices.REJECTED}),
            content_type="application/json",
        )
        assert response.status_code == 200

        assert not CalendarEvent.objects.filter(application=test_accepted_application).exists()

    def test_withdraw_accepted_application_deletes_calendar_event(
        self,
        helper_client: Client,
        test_accepted_application: Application,
    ):
        """Helper withdrawing an accepted application should delete the CalendarEvent."""
        assert CalendarEvent.objects.filter(application=test_accepted_application).exists()

        url = f"/api/applications/{test_accepted_application.id}"
        response = helper_client.delete(url)
        assert response.status_code == 200

        assert not CalendarEvent.objects.filter(application=test_accepted_application).exists()
