from allauth.account.signals import user_signed_up
from django.db import transaction
from django.dispatch import receiver
from django.utils import timezone

from features.core.models import User
from features.helper.models import HelperModel
from features.host.models import Host


@receiver(user_signed_up, sender=User)
def create_user_profiles(sender: User, request, user: User, **kwargs: object) -> None:  # noqa: ARG001, ANN001
    """Create helper and/or host profiles when a user signs up via allauth."""
    with transaction.atomic():
        if user.user_type in [User.UserTypeChoices.HELPER, User.UserTypeChoices.BOTH]:
            HelperModel._default_manager.create(
                user=user,  # audit fields
                user_id=user.id,
                description="New helper profile",
                birthday=timezone.now().date(),
                residence="",
                expected_place=[],
                expected_time_periods=[],
                expected_treatments=[],
                personality="",
                motivation="",
                hobbies="",
                licenses=HelperModel.LicenseChoices.NONE,
                languages=[],
                avg_rating=0.0,
            )

        if user.user_type in [User.UserTypeChoices.HOST, User.UserTypeChoices.BOTH]:
            Host._default_manager.create(
                user=user,  # audit fields
                user_id=user.id,
                name=user.name or user.email,
                description="New host profile",
                address="",
                type="General",
                phone_number="",
                contact_information="",
                pocket_money=0,
                meals_offered="",
                dayoffs="",
                facilities="",
                other="",
                expected_duration="",
                vehicle=Host.VehicleChoices.NONE,
                recruitment_slogan="",
                avg_rating=0.0,
            )
