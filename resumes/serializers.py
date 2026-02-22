from rest_framework import serializers

from .models import Resume


class ResumeUploadSerializer(serializers.Serializer):
    file = serializers.FileField()


class ResumeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Resume
        fields = ("id", "file", "uploaded_at", "extracted_text")
        read_only_fields = ("id", "uploaded_at", "extracted_text")


class ResumeAnalyzeSerializer(serializers.Serializer):
    resume_id = serializers.IntegerField()
    job_description = serializers.CharField(min_length=30)
