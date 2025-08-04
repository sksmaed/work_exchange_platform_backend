from django.db import models

from common.models import BaseModel


class HostModel(BaseModel):
    """Represents a host in the work exchange platform.

    Attributes:
    ----------
    user : ForeignKey
        Reference to the associated user.
    description : TextField
        Description of the host.
    address : CharField
        Address of the host.
    type : CharField
        Type of host.
    contact_information : TextField
        Contact information for the host.
    pocket_money : IntegerField
        Pocket money offered by the host.
    meals_offered : CharField
        Meals offered by the host.
    dayoffs : CharField
        Days off provided by the host.
    allowance : CharField
        Allowance details.
    facilities : TextField
        Facilities provided by the host.
    other : TextField
        Other information.
    expected_duration : CharField
        Expected duration of stay.
    expected_licenses : CharField
        Expected licenses from applicants.
    expected_age : CharField
        Expected age of applicants.
    expected_gender : CharField
        Expected gender of applicants.
    expected_personality : TextField
        Expected personality traits.
    expected_other_requirements : TextField
        Other requirements.
    recruitment_slogan : TextField
        Recruitment slogan for the host.
    avg_rating : FloatField
        Average rating of the host.
    """

    user = models.ForeignKey(
        "core.User",
        on_delete=models.CASCADE,
    )
    description = models.TextField()
    address = models.CharField(
        max_length=100,
        default="",
    )
    type = models.CharField(
        max_length=50,
    )
    contact_information = models.TextField(
        blank=True,
        default="",
    )
    pocket_money = models.IntegerField(
        default=0,
    )
    meals_offered = models.CharField(
        max_length=100,
        blank=True,
        default="",
    )
    dayoffs = models.CharField(
        max_length=100,
        blank=True,
        default="",
    )
    allowance = models.CharField(
        max_length=100,
        blank=True,
        default="",
    )
    facilities = models.TextField(
        blank=True,
        default="",
    )
    other = models.TextField(
        blank=True,
        default="",
    )
    expected_duration = models.CharField(
        max_length=100,
        blank=True,
        default="",
    )

    class LicenseChoices(models.TextChoices):
        NONE = "None", "None"
        DRIVING = "Driving", "Driving License"
        MOTORCYCLE = "Motorcycle", "Motorcycle License"
        BOTH = "Both", "Both Licenses"

    expected_licenses = models.CharField(
        max_length=20,
        choices=LicenseChoices.choices,
        default=LicenseChoices.NONE,
    )
    expected_age = models.CharField(
        max_length=50,
        blank=True,
        default="",
    )
    expected_gender = models.CharField(
        max_length=10,
        blank=True,
        default="",
    )
    expected_personality = models.TextField(
        blank=True,
        default="",
    )
    expected_other_requirements = models.TextField(
        blank=True,
        default="",
    )
    recruitment_slogan = models.TextField(
        blank=True,
        default="",
    )
    avg_rating = models.FloatField(
        default=0.0,
        blank=True,
    )
