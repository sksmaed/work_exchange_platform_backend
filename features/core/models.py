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
    """

    name = models.CharField(
        blank=True,
        max_length=255,
    )
    first_name = None
    last_name = None
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(
        unique=True,
    )
    avatar = models.ImageField(
        upload_to=get_model_file_path,
        blank=True,
        null=True,
    )
    date_joined = None
    last_login_ip = models.GenericIPAddressField(
        protocol="IPv4",
        blank=True,
        null=True,
    )
