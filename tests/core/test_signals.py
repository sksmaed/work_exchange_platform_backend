from allauth.account.signals import user_signed_up

from features.core.models import User
from features.helper.models import HelperModel
from features.host.models import HostModel


def test_user_signed_up_creates_profiles(user):
    user_signed_up.send(sender=User, request=None, user=user)
    assert HelperModel.objects.filter(user=user).exists()
    assert not HostModel.objects.filter(user=user).exists()


def test_update_user_profiles_creates_host_on_type_change(user):
    user_signed_up.send(sender=User, request=None, user=user)
    user.user_type = User.UserTypeChoices.HOST
    user.save()
    assert HostModel.objects.filter(user=user).count() == 1
    user.save()
    assert HostModel.objects.filter(user=user).count() == 1


def test_save_without_user_type_change_does_not_create_profiles(user):
    user_signed_up.send(sender=User, request=None, user=user)
    user.name = "New"
    user.save()
    assert not HostModel.objects.filter(user=user).exists()

