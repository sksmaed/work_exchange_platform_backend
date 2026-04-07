from typing import ClassVar

from django.contrib.postgres.fields import ArrayField
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from common.models import BaseModel
from utils.storage import get_model_file_path


class Host(BaseModel):
    """Represents a host in the work exchange platform.

    Attributes:
    ----------
    user : ForeignKey
        Reference to the associated user.
    name : CharField
        Name of the host.
    description : TextField
        Description of the host.
    address : CharField
        Address of the host.
    type : CharField
        Type of host.
    phone_number : CharField
        Phone number of the host.
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
    name = models.CharField(
        max_length=100,
    )
    address = models.CharField(
        max_length=100,
        default="",
    )
    type = models.CharField(
        max_length=50,
    )
    phone_number = models.CharField(
        max_length=15,
    )
    contact_information = models.TextField(
        blank=True,
        default="",
    )
    description = models.TextField()
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

    vehicle = models.CharField(
        max_length=20,
        default="",
        blank=True,
    )
    recruitment_slogan = models.TextField(
        blank=True,
        default="",
    )
    host_image = models.ImageField(
        upload_to="host_images",
        blank=True,
        null=True,
    )
    avg_rating = models.FloatField(
        default=0.0,
        blank=True,
    )


class HostReview(BaseModel):
    """A star-rating + text review left by a helper (or any user) for a host.

    Attributes:
    ----------
    host : ForeignKey
        The host being reviewed.
    reviewer : ForeignKey
        The user who wrote the review.
    rating : IntegerField
        Integer rating 1-5.
    comment : TextField
        Optional text comment.
    """

    host = models.ForeignKey(
        "host.Host",
        on_delete=models.CASCADE,
        related_name="reviews",
    )
    reviewer = models.ForeignKey(
        "core.User",
        on_delete=models.CASCADE,
        related_name="host_reviews",
    )
    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
    )
    comment = models.TextField(blank=True, default="")

    class Meta:
        unique_together: ClassVar[list[tuple[str, str]]] = [("host", "reviewer")]

    def __str__(self) -> str:
        """Return string representation."""
        return f"{self.reviewer} → {self.host} ({self.rating}★)"


class HostReviewImage(BaseModel):
    """Image attachment for a host review."""

    review = models.ForeignKey(
        "host.HostReview",
        on_delete=models.CASCADE,
        related_name="images",
    )
    image = models.ImageField(upload_to=get_model_file_path)

    class Meta:
        ordering: ClassVar[list[str]] = ["created_at"]

    def __str__(self) -> str:
        """Return string representation."""
        return f"Image for review {self.review_id}"


class Vacancy(BaseModel):
    """Represents a vacancy in the work exchange platform.

    Attributes:
    ----------
    host : ForeignKey
        Reference to the associated host.
    name : CharField
        Name of the vacancy.
    work_time : CharField
        Work time of the vacancy.
    description : TextField
        Description of the vacancy.
    expected_duration : CharField
        Expected duration of the vacancy.
    expected_age : CharField
        Expected age of the vacancy.
    expected_gender : CharField
        Expected gender of the vacancy.
    expected_licenses : CharField
        Expected licenses of the vacancy.
    expected_personality : TextField
        Expected personality of the vacancy.
    expected_other_requirements : TextField
        Expected other requirements of the vacancy.
    other_questions : ArrayField
        Other questions of the vacancy.
    vacancy_image : ImageField
        Image of the vacancy.
    status : CharField
        Status of the vacancy.
    """

    host = models.ForeignKey(
        "host.Host",
        on_delete=models.CASCADE,
    )
    name = models.CharField(
        max_length=100,
    )
    work_time = models.CharField(
        max_length=100,
    )
    description = models.TextField()

    expected_duration = models.CharField(
        max_length=100,
    )
    expected_age = models.CharField(
        max_length=100,
    )
    expected_gender = models.CharField(
        max_length=100,
    )
    expected_licenses = models.CharField(
        max_length=100,
    )
    expected_personality = models.TextField()
    expected_other_requirements = models.TextField()
    other_questions = ArrayField(
        models.CharField(max_length=100),
        blank=True,
        default=list,
    )
    vacancy_image = models.ImageField(
        upload_to="vacancy_images",
        blank=True,
        null=True,
    )

    class StatusChoices(models.TextChoices):
        RECRUITING = "Recruiting", "Recruiting"
        FULL = "Full", "Full"
        UNAVAILABLE = "Unavailable", "Unavailable"

    status = models.CharField(
        max_length=20,
        choices=StatusChoices.choices,
        default=StatusChoices.RECRUITING,
    )


class VacancyAvailability(BaseModel):
    """Represents a continuous availability period for a vacancy.

    Attributes:
    ----------
    vacancy : ForeignKey
        Reference to the associated vacancy.
    start_date : DateField
        Start date of the availability period.
    end_date : DateField
        End date of the availability period.
    capacity : IntegerField
        Total number of slots available for this period.
    current_helpers : IntegerField
        Number of currently accepted helpers for this period.
    """

    vacancy = models.ForeignKey(
        "host.Vacancy",
        on_delete=models.CASCADE,
        related_name="availabilities",
    )
    start_date = models.DateField()
    end_date = models.DateField()
    capacity = models.IntegerField(default=1)
    current_helpers = models.IntegerField(default=0)
