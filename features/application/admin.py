from django.contrib import admin

from features.application.models import Application


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    """Admin interface for Application model."""

    list_display = ("id", "helper", "vacancy", "status", "start_date", "end_date")
    list_filter = ("status", "start_date", "end_date")
    search_fields = ("helper__user__username", "vacancy__title")
