from django.contrib import admin

from features.host.models import Host, Vacancy


@admin.register(Host)
class HostAdmin(admin.ModelAdmin):
    """Admin interface for Host."""

    list_display = ("id", "type", "address", "created_at", "created_by_user")
    search_fields = ("type", "address")
    list_filter = ("type", "created_at")


@admin.register(Vacancy)
class VacancyAdmin(admin.ModelAdmin):
    """Admin interface for Vacancy."""

    list_display = ("id", "host", "created_at", "created_by_user")
    search_fields = ("host__name", "host__address")
    list_filter = ("created_at",)
