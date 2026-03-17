from typing import ClassVar

from django.db import models

from common.models import BaseModel


class Application(BaseModel):
    """Model representing an application from a helper to a host vacancy."""

    class StatusChoices(models.TextChoices):
        PENDING = "pending", "Pending"
        ACCEPTED = "accepted", "Accepted"
        REJECTED = "rejected", "Rejected"
        WITHDRAWN = "withdrawn", "Withdrawn"

    helper = models.ForeignKey("helper.HelperModel", on_delete=models.CASCADE, related_name="applications")
    vacancy = models.ForeignKey("host.Vacancy", on_delete=models.CASCADE, related_name="applications")
    status = models.CharField(
        max_length=20,
        choices=StatusChoices.choices,
        default=StatusChoices.PENDING,
    )
    start_date = models.DateField()
    end_date = models.DateField()

    class Meta:
        unique_together: ClassVar[tuple[tuple[str, ...], ...]] = (("helper", "vacancy"),)

    def __str__(self) -> str:
        """String representation."""
        return f"Application({self.helper} -> {self.vacancy})"
