from django.contrib.auth.models import AbstractUser
from django.db import models

from common.models import BaseModel
from utils.storage import get_model_file_path


class User(AbstractUser, BaseModel):
    """Custom user model extending Django's AbstractUser and BaseModel.

    Attributes:
    ----------
    name : str
        Optional full name of the user.
    username : str
        Unique username for authentication.
    email : str
        Unique email address of the user.
    avatar : ImageField
        Optional user avatar image.
    last_login_ip : str
        Last login IP address (IPv4).
    user_type : str
        Type of user: 'helper', 'host', or 'both'.
    """

    class UserTypeChoices(models.TextChoices):
        HELPER = "helper", "Helper"
        HOST = "host", "Host"
        BOTH = "both", "Both Helper and Host"

    name = models.CharField(
        blank=True,
        max_length=255,
    )
    first_name = models.CharField(
        max_length=150,
        blank=True,
    )
    last_name = models.CharField(
        max_length=150,
        blank=True,
    )
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(
        unique=True,
    )
    avatar = models.ImageField(
        upload_to=get_model_file_path,
        blank=True,
        null=True,
    )
    last_login_ip = models.GenericIPAddressField(
        protocol="IPv4",
        blank=True,
        null=True,
    )
    user_type = models.CharField(
        max_length=10,
        choices=UserTypeChoices.choices,
        default=UserTypeChoices.HELPER,
        help_text="Type of user: helper, host, or both",
    )

    def get_full_name(self):
        """Return the full name of the user."""
        return self.name or self.email

    def get_short_name(self):
        """Return the short name of the user."""
        return self.name or self.email

    def __str__(self) -> str:
        """Return a string representation of the user."""
        return self.name
