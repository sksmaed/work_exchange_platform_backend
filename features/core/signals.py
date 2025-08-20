from django.contrib.auth.signals import user_logged_in
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.http import HttpRequest
from django.utils import timezone
from django.db import transaction

from features.core.models import User
from features.helper.models import HelperModel
from features.host.models import HostModel


@receiver(post_save, sender=User)
def create_user_profiles(sender, instance, created, **kwargs):
    """Create helper and/or host profiles when a new user is created.
    
    This signal is triggered when a user is created (including during registration).
    It creates the appropriate profile(s) based on the user's type.
    """
    if created:
        with transaction.atomic():
            # Create profiles based on user type
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
                print(f"Created helper profile for user: {instance.email}")
            
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
                print(f"Created host profile for user: {instance.email}")


@receiver(post_save, sender=User)
def update_user_profiles(sender, instance, created, **kwargs):
    """Update user profiles when user type changes.
    
    This signal handles cases where a user changes their type after creation.
    It creates or removes profiles as needed.
    """
    if not created:  # Only for updates, not creation
        with transaction.atomic():
            # Check if helper profile exists
            helper_exists = HelperModel.objects.filter(user=instance).exists()
            # Check if host profile exists
            host_exists = HostModel.objects.filter(user=instance).exists()
            
            # Create helper profile if needed
            if instance.user_type in [User.UserTypeChoices.HELPER, User.UserTypeChoices.BOTH] and not helper_exists:
                HelperModel.objects.create(
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
                print(f"Created helper profile for existing user: {instance.email}")
            
            # Create host profile if needed
            if instance.user_type in [User.UserTypeChoices.HOST, User.UserTypeChoices.BOTH] and not host_exists:
                HostModel.objects.create(
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
                print(f"Created host profile for existing user: {instance.email}")


@receiver(user_logged_in)
def ensure_user_profiles_exist(request: HttpRequest, user: User, **kwargs) -> None:
    """Ensure helper and host profiles exist when user logs in.
    
    This is a fallback mechanism to ensure profiles exist even if signals failed.
    """
    with transaction.atomic():
        # Ensure helper profile exists if user should have one
        if user.user_type in [User.UserTypeChoices.HELPER, User.UserTypeChoices.BOTH]:
            HelperModel.objects.get_or_create(
                user=user,
                defaults={
                    'description': 'New helper profile',
                    'birthday': timezone.now().date(),
                    'gender': '',
                    'residence': '',
                    'expected_place': [],
                    'expected_time_periods': [],
                    'expected_treatments': [],
                    'personality': '',
                    'motivation': '',
                    'hobbits': '',
                    'licenses': HelperModel.LicenseChoices.NONE,
                    'languages': [],
                    'avg_rating': 0.0,
                }
            )
        
        # Ensure host profile exists if user should have one
        if user.user_type in [User.UserTypeChoices.HOST, User.UserTypeChoices.BOTH]:
            HostModel.objects.get_or_create(
                user=user,
                defaults={
                    'description': 'New host profile',
                    'address': '',
                    'type': 'General',
                    'contact_information': '',
                    'pocket_money': 0,
                    'meals_offered': '',
                    'dayoffs': '',
                    'allowance': '',
                    'facilities': '',
                    'other': '',
                    'expected_duration': '',
                    'expected_licenses': '',
                    'expected_age': '',
                    'expected_gender': '',
                    'expected_personality': '',
                    'expected_other_requirements': '',
                    'recruitment_slogan': '',
                    'avg_rating': 0.0,
                }
            ) 