from django.contrib import admin
from django.contrib.auth import admin as auth_admin

from features.core.models import User


@admin.register(User)
class UserAdmin(auth_admin.UserAdmin):
    """Admin interface for User model."""

    list_display = ("email", "username", "is_staff", "is_superuser", "user_type")
    search_fields = ("email", "username")
    ordering = ("email",)
