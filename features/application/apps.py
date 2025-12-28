from django.apps import AppConfig


class ApplicationConfig(AppConfig):
    """Configuration for the application app."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "features.application"
    label = "application"

