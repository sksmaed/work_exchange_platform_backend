from django.contrib import admin

from features.helper.resume.models import HelperResume


@admin.register(HelperResume)
class HelperResumeAdmin(admin.ModelAdmin):
    """Admin interface for HelperResume model.

    Displays resume details and allows searching/filtering by helper email, title, and creation date.
    """

    list_display = ("id", "helper", "title", "created_at")
    search_fields = ("helper__user__email", "title")
    list_filter = ("created_at",)
