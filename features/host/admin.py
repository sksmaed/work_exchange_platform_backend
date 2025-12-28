from django.contrib import admin

from features.host.models import HostModel


@admin.register(HostModel)
class HostModelAdmin(admin.ModelAdmin):
    """Admin interface for HostModel."""

    list_display = ("id", "name", "type", "address", "created_at", "created_by_user")
    search_fields = ("name", "address", "type")
    list_filter = ("type", "created_at")
