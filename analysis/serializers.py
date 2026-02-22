from rest_framework import serializers

from .models import Analysis


class AnalysisSerializer(serializers.ModelSerializer):
    suggestions_list = serializers.SerializerMethodField()

    def get_suggestions_list(self, obj):
        if not obj.suggestions:
            return []
        return [line.strip() for line in obj.suggestions.splitlines() if line.strip()]

    class Meta:
        model = Analysis
        fields = (
            "id",
            "resume",
            "job_description",
            "match_score",
            "keyword_similarity",
            "skill_match_score",
            "experience_relevance",
            "ats_compliance",
            "skills_found",
            "skills_missing",
            "suggestions",
            "suggestions_list",
            "predicted_role",
            "created_at",
        )
