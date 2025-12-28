import pytest

# Django setup happens in root conftest.py via pytest_configure
# Import Django components after Django is configured
pytest_plugins = []  # Ensure root conftest loads first


def _get_user_model():
    """Get user model after Django is configured."""
    from django.contrib.auth import get_user_model  # noqa: PLC0415

    return get_user_model()


def _get_models():
    """Import models after Django is configured."""
    from django.contrib.auth.models import AbstractUser  # noqa: PLC0415
    from django.core.cache import cache  # noqa: PLC0415
    from django.test import Client  # noqa: PLC0415

    from features.helper.models import HelperModel  # noqa: PLC0415
    from features.host.models import Host, Vacancy  # noqa: PLC0415

    return AbstractUser, Client, cache, HelperModel, Host, Vacancy


@pytest.fixture(autouse=True)
def clear_cache_after_test():
    """Automatically clear cache after each test."""
    _, _, cache, _, _, _ = _get_models()
    yield
    cache.clear()


@pytest.fixture(scope="session")
def client():
    """Django test client."""
    _, Client, _, _, _, _ = _get_models()
    return Client()


@pytest.fixture(scope="session")
def superuser_client():
    """Django test client."""
    _, Client, _, _, _, _ = _get_models()
    return Client()


# Test data constants
TEST_USER_NAME = "test"
TEST_USER_EMAIL = "testuser@example.com"
TEST_SUPERUSER_EMAIL = "testsuperuser@example.com"
TEST_PASSWORD = "testpassword123"  # noqa: S105
HTTP_OK = 200


@pytest.fixture
def user(db):
    """Create a user with verified email."""
    AbstractUser, _, _, _, _, _ = _get_models()
    User = _get_user_model()
    user = User.objects.create_user(
        email=TEST_USER_EMAIL, password=TEST_PASSWORD, username=TEST_USER_NAME, user_type=User.UserTypeChoices.HELPER
    )
    # Verify email for testing
    from allauth.account.models import EmailAddress  # noqa: PLC0415
    EmailAddress.objects.create(user=user, email=TEST_USER_EMAIL, verified=True, primary=True)
    return user


@pytest.fixture
def superuser(db):
    """Create a superuser."""
    User = _get_user_model()
    return User.objects.create_superuser(email=TEST_SUPERUSER_EMAIL, password=TEST_PASSWORD)


@pytest.fixture
def authenticated_client(client, user):
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
def authenticated_superuser_client(superuser_client, superuser):
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
def helper_model(user, db):
    """Create a helper model."""
    _, _, _, HelperModel, _, _ = _get_models()
    helper = HelperModel.objects.create(
        user_id=user.id,
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
    # Refresh to ensure user relationship is loaded
    helper.refresh_from_db()
    return helper


@pytest.fixture
def authenticated_helper_client(user, helper_model, db):
    """Authenticate a helper client."""
    # Create a fresh client to avoid cookie conflicts
    _, Client, _, _, _, _ = _get_models()
    client = Client()
    
    # Ensure helper_model.user matches the user fixture
    # Both helper_model and authenticated_helper_client depend on user,
    # so they should use the same user instance
    # Refresh helper_model to ensure user relationship is loaded
    helper_model.refresh_from_db()
    assert helper_model.user.id == user.id, f"helper_model.user ({helper_model.user.id}) must match user fixture ({user.id})"
    
    response = client.post(
        "/api/auth/login/",
        {"email": user.email, "password": TEST_PASSWORD},
        content_type="application/json",
    )
    assert response.status_code == HTTP_OK, f"Login failed: {response.content}"
    client.cookies.update(response.cookies)
    return client


@pytest.fixture
def host_user(db):
    """Create a host user with verified email."""
    User = _get_user_model()
    user = User.objects.create_user(
        email="host@example.com",
        password=TEST_PASSWORD,
        username="hostuser",
        user_type=User.UserTypeChoices.HOST,
    )
    # Verify email for testing
    from allauth.account.models import EmailAddress  # noqa: PLC0415
    EmailAddress.objects.create(user=user, email="host@example.com", verified=True, primary=True)
    return user


@pytest.fixture
def host(host_user, db):
    """Create a host model."""
    _, _, _, _, Host, _ = _get_models()
    return Host.objects.create(
        user_id=host_user.id,
        address="123 Test Street",
        type="Family",
        phone_number="+886912345678",
        description="A friendly host family",
        pocket_money=5000,
        meals_offered="Breakfast, Lunch, Dinner",
        dayoffs="Weekends",
        facilities="WiFi, Private Room",
        other="Pet friendly",
        expected_duration="3-6 months",
        vehicle=Host.VehicleChoices.DRIVING,
        recruitment_slogan="Join our welcoming family!",
        avg_rating=4.8,
    )


@pytest.fixture
def vacancy(host, db):
    """Create a vacancy."""
    _, _, _, _, _, Vacancy = _get_models()
    return Vacancy.objects.create(
        host=host,
        name="House Helper Needed",
        work_time="9:00 AM - 5:00 PM",
        description="Looking for a reliable helper to assist with household chores",
        expected_duration="3 months",
        expected_age="20-30",
        expected_gender="Any",
        expected_licenses="Driving License",
        expected_personality="Friendly, responsible, and hardworking",
        expected_other_requirements="Experience in housekeeping preferred",
        other_questions=["Do you have experience with elderly care?"],
        status=Vacancy.StatusChoices.RECRUITING,
    )


@pytest.fixture
def authenticated_host_client(host_user, db):
    """Authenticate a host client."""
    # Create a fresh client to avoid cookie conflicts
    _, Client, _, _, _, _ = _get_models()
    client = Client()
    
    response = client.post(
        "/api/auth/login/",
        {"email": host_user.email, "password": TEST_PASSWORD},
        content_type="application/json",
    )
    assert response.status_code == HTTP_OK, f"Login failed: {response.content}"
    client.cookies.update(response.cookies)
    return client
