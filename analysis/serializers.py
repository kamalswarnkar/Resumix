from rest_framework import serializers

from .models import Analysis


class AnalysisSerializer(serializers.ModelSerializer):
    class Meta:
        model = Analysis
        fields = (
            "id",
            "resume",
            "match_score",
            "keyword_similarity",
            "skill_match_score",
            "experience_relevance",
            "ats_compliance",
            "skills_found",
            "skills_missing",
            "suggestions",
            "predicted_role",
            "created_at",
        )
