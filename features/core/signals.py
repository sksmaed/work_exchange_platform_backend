from allauth.account.signals import user_signed_up
from django.db import transaction
from django.dispatch import receiver
from django.utils import timezone

from features.core.models import User
from features.helper.models import HelperModel
from features.host.models import HostModel


@receiver(user_signed_up, sender=User)
def create_user_profiles(sender: User, instance: User, created: bool, **kwargs: object) -> None:  # noqa: ARG001
    """Create helper and/or host profiles when a new user is created.

    This signal is triggered when a user is created (including during registration).
    It creates the appropriate profile(s) based on the user's type.
    """
    if created:
        with transaction.atomic():
            if instance.user_type in [User.UserTypeChoices.HELPER, User.UserTypeChoices.BOTH]:
                HelperModel.objects.create(
                    user=instance,
                    description="New helper profile",
                    birthday=timezone.now().date(),
                    gender="",  # Will be filled by user later
                    residence="",  # Will be filled by user later
                    expected_place=[],  # Empty list for now
                    expected_time_periods=[],  # Empty list for now
                    expected_treatments=[],  # Empty list for now
                    personality="",  # Will be filled by user later
                    motivation="",  # Will be filled by user later
                    hobbits="",  # Will be filled by user later
                    licenses=HelperModel.LicenseChoices.NONE,
                    languages=[],  # Empty list for now
                    avg_rating=0.0,
                )

            if instance.user_type in [User.UserTypeChoices.HOST, User.UserTypeChoices.BOTH]:
                HostModel.objects.create(
                    user=instance,
                    description="New host profile",
                    address="",  # Will be filled by user later
                    type="General",  # Default type
                    contact_information="",  # Will be filled by user later
                    pocket_money=0,  # Default value
                    meals_offered="",  # Will be filled by user later
                    dayoffs="",  # Will be filled by user later
                    allowance="",  # Will be filled by user later
                    facilities="",  # Will be filled by user later
                    other="",  # Will be filled by user later
                    expected_duration="",  # Will be filled by user later
                    expected_licenses="",  # Will be filled by user later
                    expected_age="",  # Will be filled by user later
                    expected_gender="",  # Will be filled by user later
                    expected_personality="",  # Will be filled by user later
                    expected_other_requirements="",  # Will be filled by user later
                    recruitment_slogan="",  # Will be filled by user later
                    avg_rating=0.0,
                )
