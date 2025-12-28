from allauth.account.signals import user_signed_up
from django.db import transaction
from django.dispatch import receiver
from django.utils import timezone

from features.core.models import User
from features.helper.models import HelperModel
from features.host.models import Host


@receiver(user_signed_up, sender=User)
def create_user_profiles(sender: User, instance: User, created: bool, **kwargs: object) -> None:  # noqa: ARG001
    """Create helper and/or host profiles when a new user is created.

    This signal is triggered when a user is created (including during registration).
    It creates the appropriate profile(s) based on the user's type.
    """
    if created:
        with transaction.atomic():
            if instance.user_type in [User.UserTypeChoices.HELPER, User.UserTypeChoices.BOTH]:
                HelperModel._default_manager.create(
                    user=instance,
                    description="New helper profile",
                    birthday=timezone.now().date(),
                    gender="",
                    residence="",
                    expected_place=[],
                    expected_time_periods=[],
                    expected_treatments=[],
                    personality="",
                    motivation="",
                    hobbits="",
                    licenses=HelperModel.LicenseChoices.NONE,
                    languages=[],
                    avg_rating=0.0,
                )

            if instance.user_type in [User.UserTypeChoices.HOST, User.UserTypeChoices.BOTH]:
                Host._default_manager.create(
                    user=instance,
                    description="New host profile",
                    address="",
                    type="General",
                    contact_information="",
                    pocket_money=0,
                    meals_offered="",
                    dayoffs="",
                    allowance="",
                    facilities="",
                    other="",
                    expected_duration="",
                    expected_licenses="",
                    expected_age="",
                    expected_gender="",
                    expected_personality="",
                    expected_other_requirements="",
                    recruitment_slogan="",
                    avg_rating=0.0,
                )
