from django.contrib import admin

from .models import Analysis


@admin.register(Analysis)
class AnalysisAdmin(admin.ModelAdmin):
    list_display = ("id", "resume", "match_score", "predicted_role", "created_at")
    list_filter = ("predicted_role", "created_at")
    search_fields = ("resume__user__email",)
