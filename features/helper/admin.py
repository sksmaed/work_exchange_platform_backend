from django.contrib import admin

from features.helper.models import HelperModel


@admin.register(HelperModel)
class HelperModelAdmin(admin.ModelAdmin):
    """Admin interface for HelperModel."""

    list_display = ("user", "description")
    search_fields = ("user__username", "description")
    list_filter = ("user__user_type", "gender", "avg_rating")
    ordering = ("user__username",)
