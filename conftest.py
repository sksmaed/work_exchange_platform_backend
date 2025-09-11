"""Root conftest.py for Django configuration."""

import os

import django
from django.conf import settings


def pytest_configure():
    """Configure Django settings for tests."""
    if not settings.configured:
        os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.local")
        django.setup()
