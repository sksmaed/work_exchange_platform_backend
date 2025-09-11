import pytest
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser
from django.core.cache import cache
from django.test import Client

from features.helper.models import HelperModel
from features.helper.resume.models import HelperResume

User = get_user_model()


@pytest.fixture(autouse=True)
def clear_cache_after_test():
    """Automatically clear cache after each test."""
    yield
    cache.clear()


@pytest.fixture(scope="session")
def client() -> Client:
    """Django test client."""
    return Client()


@pytest.fixture(scope="session")
def superuser_client() -> Client:
    """Django test client."""
    return Client()


# Test data constants
TEST_USER_NAME = "test"
TEST_USER_EMAIL = "testuser@example.com"
TEST_SUPERUSER_EMAIL = "testsuperuser@example.com"
TEST_PASSWORD = "testpassword123"  # noqa: S105
HTTP_OK = 200


@pytest.fixture
@pytest.mark.django_db
def user(db: None) -> AbstractUser:
    """Create a user."""
    return User.objects.create_user(
        email=TEST_USER_EMAIL, password=TEST_PASSWORD, username=TEST_USER_NAME, user_type=User.UserTypeChoices.HELPER
    )


@pytest.fixture
@pytest.mark.django_db
def superuser(db: None) -> AbstractUser:
    """Create a superuser."""
    return User.objects.create_superuser(email=TEST_SUPERUSER_EMAIL, password=TEST_PASSWORD)


@pytest.fixture
def authenticated_client(client: Client, user: AbstractUser) -> Client:
    """Authenticate a client."""
    response = client.post(
        "/api/auth/login/",
        {"email": TEST_USER_EMAIL, "password": TEST_PASSWORD},
        content_type="application/json",
    )
    assert response.status_code == HTTP_OK, f"Login failed: {response.content}"
    client.cookies.update(response.cookies)
    return client


@pytest.fixture
def authenticated_superuser_client(superuser_client: Client, superuser: AbstractUser) -> Client:
    """Authenticate a superuser client."""
    response = superuser_client.post(
        "/api/auth/login/",
        {"email": TEST_SUPERUSER_EMAIL, "password": TEST_PASSWORD},
        content_type="application/json",
    )
    assert response.status_code == HTTP_OK, f"Login failed: {response.content}"
    superuser_client.cookies.update(response.cookies)
    return superuser_client


@pytest.fixture
@pytest.mark.django_db
def helper_model(user: AbstractUser) -> HelperModel:
    """Create a helper model."""
    return HelperModel.objects.create(
        user=user,
        description="Test helper description",
        birthday="1990-01-01",
        gender=HelperModel.GenderChoices.MALE,
        residence="Test City",
        expected_place=["City A", "City B"],
        expected_time_periods=["morning", "afternoon"],
        expected_treatments=["cleaning", "cooking"],
        personality="Friendly and reliable",
        motivation="Want to help others",
        hobbies="Reading, cooking",
        licenses=HelperModel.LicenseChoices.DRIVING,
        languages=["Chinese", "English"],
        avg_rating=4.5,
    )


@pytest.fixture
@pytest.mark.django_db
def authenticated_helper_client(client: Client, user: AbstractUser) -> Client:
    """Authenticate a helper client."""
    response = client.post(
        "/api/auth/login/",
        {"email": user.email, "password": TEST_PASSWORD},
        content_type="application/json",
    )
    assert response.status_code == HTTP_OK, f"Login failed: {response.content}"
    client.cookies.update(response.cookies)
    return client


@pytest.fixture
@pytest.mark.django_db
def helper_resume(helper_model: HelperModel) -> HelperResume:
    """Create a helper resume."""
    return HelperResume.objects.create(
        helper=helper_model,
        title="Professional Helper",
        summary="Experienced helper with excellent skills",
        experiences=[
            {"title": "Home Assistant", "company": "ABC Family", "duration": "2 years"},
            {"title": "Cleaner", "company": "XYZ Company", "duration": "1 year"},
        ],
        skills=["Cleaning", "Cooking", "Elderly Care"],
        certifications=["First Aid Certificate", "CPR Certification"],
        availability=[{"day": "Monday", "time": "9:00-17:00"}, {"day": "Tuesday", "time": "9:00-17:00"}],
        preferred_locations=["Taipei", "New Taipei"],
        contact_email="helper@example.com",
        contact_phone="+886912345678",
    )
