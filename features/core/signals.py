from allauth.account.signals import user_signed_up
from django.contrib.auth.signals import user_logged_in
from django.db import transaction
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.http import HttpRequest
from django.utils import timezone

from features.core.models import User
from features.helper.models import HelperModel
from features.host.models import HostModel


@receiver(user_signed_up)
def create_user_profiles(request: HttpRequest, user: User, **_: object) -> None:
    """Create helper and host profiles after registration."""

    with transaction.atomic():
        if user.user_type in [User.UserTypeChoices.HELPER, User.UserTypeChoices.BOTH]:
            HelperModel(
                user=user,
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
            ).save(user=user)

        if user.user_type in [User.UserTypeChoices.HOST, User.UserTypeChoices.BOTH]:
            HostModel(
                user=user,
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
            ).save(user=user)


@receiver(pre_save, sender=User)
def store_previous_user_type(sender: type[User], instance: User, **_: object) -> None:
    """Cache current user type before saving."""

    if instance.pk and sender.objects.filter(pk=instance.pk).exists():
        instance._previous_user_type = sender.objects.get(pk=instance.pk).user_type  # noqa: SLF001
    else:
        instance._previous_user_type = None  # noqa: SLF001


@receiver(post_save, sender=User)
def update_user_profiles(sender: type[User], instance: User, created: bool, **_: object) -> None:
    """Create missing profiles when user type changes."""

    if created:
        return

    previous = getattr(instance, "_previous_user_type", None)
    if previous == instance.user_type:
        return

    with transaction.atomic():
        if instance.user_type in [User.UserTypeChoices.HELPER, User.UserTypeChoices.BOTH]:
            if not HelperModel.objects.filter(user=instance).exists():
                HelperModel(
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
                ).save(user=instance)

        if instance.user_type in [User.UserTypeChoices.HOST, User.UserTypeChoices.BOTH]:
            if not HostModel.objects.filter(user=instance).exists():
                HostModel(
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
                ).save(user=instance)


@receiver(user_logged_in)
def ensure_user_profiles_exist(request: HttpRequest, user: User, **_: object) -> None:
    """Create missing profiles on login."""

    with transaction.atomic():
        if user.user_type in [User.UserTypeChoices.HELPER, User.UserTypeChoices.BOTH]:
            if not HelperModel.objects.filter(user=user).exists():
                HelperModel(
                    user=user,
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
                ).save(user=user)

        if user.user_type in [User.UserTypeChoices.HOST, User.UserTypeChoices.BOTH]:
            if not HostModel.objects.filter(user=user).exists():
                HostModel(
                    user=user,
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
                ).save(user=user)
