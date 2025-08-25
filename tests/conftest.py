import os
import sys
from pathlib import Path

import django
import pytest
from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.test import Client
import uuid

BASE_DIR = Path(__file__).resolve().parents[1]
sys.path.append(str(BASE_DIR))
os.environ.setdefault("DJANGO_SECRET_KEY", "test")
os.environ.setdefault("DATABASE_HOST", "")
os.environ.setdefault("DATABASE_PORT", "0")
os.environ.setdefault("DATABASE_DB", "")
os.environ.setdefault("DATABASE_USER", "")
os.environ.setdefault("DATABASE_PASSWORD", "")
os.environ.setdefault(
    "CACHES_BACKEND", "django.core.cache.backends.locmem.LocMemCache"
)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.test")
django.setup()
call_command("migrate", run_syncdb=True, verbosity=0)

User = get_user_model()


@pytest.fixture
def user():
    uid = uuid.uuid4().hex
    return User.objects.create_user(
        username=uid,
        email=f"{uid}@example.com",
        password="password",
    )


@pytest.fixture
def superuser():
    uid = uuid.uuid4().hex
    return User.objects.create_superuser(
        username=uid,
        email=f"{uid}@example.com",
        password="password",
    )


@pytest.fixture
def organization():
    return {}


@pytest.fixture
def client():
    return Client()


@pytest.fixture
def superuser_client(superuser):
    client = Client()
    client.force_login(superuser)
    return client

