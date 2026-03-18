from django.apps import AppConfig


class PostConfig(AppConfig):
    """Configuration for the post feature."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "features.post"
