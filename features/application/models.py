from datetime import date
from typing import ClassVar

from django.db import models

from common.models import BaseModel
from features.helper.models import HelperModel


class Application(BaseModel):
    """Model representing a helper's application to a vacancy.

    Attributes:
    ----------
    vacancy : ForeignKey
        Reference to the Vacancy being applied to.
    helper : ForeignKey
        Reference to the HelperModel applying.
    start_date : DateField
        Proposed start date for the helper.
    end_date : DateField
        Proposed end date for the helper.
    status : CharField
        Status of the application.
    """

    class StatusChoices(models.TextChoices):
        PENDING = "pending", "Pending"
        ACCEPTED = "accepted", "Accepted"
        REJECTED = "rejected", "Rejected"
        WITHDRAWN = "withdrawn", "Withdrawn"

    vacancy = models.ForeignKey(
        "host.Vacancy",
        on_delete=models.CASCADE,
        related_name="applications",
    )
    helper = models.ForeignKey(
        HelperModel,
        on_delete=models.CASCADE,
        related_name="applications",
    )
    start_date = models.DateField()
    end_date = models.DateField()
    status = models.CharField(
        max_length=20,
        choices=StatusChoices.choices,
        default=StatusChoices.PENDING,
    )

    class Meta:
        # One helper can only apply once to a specific vacancy
        unique_together = [["helper", "vacancy"]]
        ordering: ClassVar[list[str]] = ["-created_at"]

    def __str__(self) -> str:
        """String representation of the Application."""
        return f"Application({self.helper.user.email} -> Vacancy#{self.vacancy.id})"

