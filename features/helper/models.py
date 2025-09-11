from typing import ClassVar

from django.db import models

from common.models import BaseModel


class HelperModel(BaseModel):
    """Model representing a helper user in the platform.

    Attributes:
    ----------
    user : ForeignKey
        Reference to the user associated with this helper.
    description : TextField
        Description of the helper.
    birthday : DateField
        Birthday of the helper.
    gender : CharField
        Gender of the helper.
    residence : CharField
        Current residence of the helper.
    expected_place : JSONField
        Expected places for the helper.
    expected_time_periods : JSONField
        Expected time periods for availability.
    expected_treatments : JSONField
        Expected treatments the helper can provide.
    personality : TextField
        Personality description.
    motivation : TextField
        Motivation for helping.
    hobbits : TextField
        Hobbies of the helper.
    license : CharField
        Type of license the helper holds.
    languages : JSONField
        Languages spoken by the helper.
    avg_rating : FloatField
        Average rating of the helper.
    """

    user = models.ForeignKey(
        "core.User",
        on_delete=models.CASCADE,
    )
    description = models.TextField()
    birthday = models.DateField()

    class GenderChoices(models.TextChoices):
        MALE = "M", "Male"
        FEMALE = "F", "Female"

    gender = models.CharField(
        max_length=10,
        choices=GenderChoices.choices,
        default=None,
    )
    residence = models.CharField(
        max_length=100,
        blank=True,
        default="",
    )
    expected_place = models.JSONField(
        default=list,
        blank=True,
    )
    expected_time_periods = models.JSONField(
        default=list,
        blank=True,
    )
    expected_treatments = models.JSONField(
        default=list,
        blank=True,
    )
    personality = models.TextField(
        blank=True,
        default="",
    )
    motivation = models.TextField(
        blank=True,
        default="",
    )
    hobbies = models.TextField(
        blank=True,
        default="",
    )

    class LicenseChoices(models.TextChoices):
        NONE = "None", "None"
        DRIVING = "Driving", "Driving License"
        MOTORCYCLE = "Motorcycle", "Motorcycle License"
        BOTH = "Both", "Both Licenses"

    licenses = models.CharField(
        max_length=20,
        choices=LicenseChoices.choices,
        default=LicenseChoices.NONE,
    )
    languages = models.JSONField(
        default=list,
        blank=True,
    )
    avg_rating = models.FloatField(
        default=0.0,
        blank=True,
    )


class HelperPhoto(BaseModel):
    """Model representing a photo associated with a helper.

    Attributes:
    ----------
    helper : ForeignKey
        Reference to the HelperModel this photo belongs to.
    image : ImageField
        The image file for the photo.
    alt_text : CharField
        Alternative text for accessibility.
    order : PositiveIntegerField
        Display order of the photo.
    """

    helper = models.ForeignKey(HelperModel, on_delete=models.CASCADE, related_name="photos")
    image = models.ImageField(upload_to="helper_photos/")
    alt_text = models.CharField(max_length=200, blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering: ClassVar[list[str]] = ["order", "created_at"]
