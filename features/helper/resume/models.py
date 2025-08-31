from django.contrib.postgres.fields import ArrayField
from django.db import models

from common.models import BaseModel
from features.helper.models import HelperModel


class HelperResume(BaseModel):
    """Resume for a helper user."""

    helper = models.OneToOneField(HelperModel, on_delete=models.CASCADE, related_name="resume")

    title = models.CharField(max_length=100, blank=True, default="")
    summary = models.TextField(blank=True, default="")

    # Experience and skills
    experiences = models.JSONField(blank=True, default=list)
    skills = ArrayField(models.CharField(max_length=100), blank=True, default=list)
    certifications = models.JSONField(blank=True, default=list)

    # Availability and preferences
    availability = models.JSONField(blank=True, default=list)  # e.g., days/time slots
    preferred_locations = models.JSONField(blank=True, default=list)

    # Contact preference
    contact_email = models.EmailField(blank=True, default="")
    contact_phone = models.CharField(max_length=30, blank=True, default="")

    def __str__(self) -> str:
        """String representation of the HelperResume model."""
        return f"Resume({self.helper.user.email})"
