from django.contrib import admin

from features.host.models import Host


@admin.register(Host)
class HostAdmin(admin.ModelAdmin):
    """Admin interface for Host."""

    list_display = ("id", "type", "address", "created_at", "created_by_user")
    search_fields = ("type", "address")
    list_filter = ("type", "created_at")
