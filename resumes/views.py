from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from analysis.serializers import AnalysisSerializer
from analysis.services import run_analysis

from .models import Resume
from .parsers import extract_text_from_resume
from .serializers import ResumeUploadSerializer, ResumeAnalyzeSerializer
from .validators import validate_resume_file


class ResumeViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def upload(self, request):
        serializer = ResumeUploadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        resume_file = serializer.validated_data["file"]
        validate_resume_file(resume_file)

        resume = Resume.objects.create(user=request.user, file=resume_file)
        try:
            resume.extracted_text = extract_text_from_resume(resume.file.path)
        except Exception as exc:
            resume.delete()
            return Response({"detail": f"Could not parse file: {exc}"}, status=status.HTTP_400_BAD_REQUEST)

        resume.save(update_fields=["extracted_text"])

        return Response(
            {
                "id": resume.id,
                "file": resume.file.url,
                "uploaded_at": resume.uploaded_at,
                "message": "Resume uploaded and parsed successfully",
            },
            status=status.HTTP_201_CREATED,
        )

    def analyze(self, request):
        serializer = ResumeAnalyzeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        resume_id = serializer.validated_data["resume_id"]
        job_description = serializer.validated_data["job_description"]

        try:
            resume = Resume.objects.get(id=resume_id, user=request.user)
        except Resume.DoesNotExist:
            return Response({"detail": "Resume not found"}, status=status.HTTP_404_NOT_FOUND)

        analysis = run_analysis(resume=resume, job_description=job_description)
        return Response(AnalysisSerializer(analysis).data)

    def history(self, request):
        queryset = Resume.objects.filter(user=request.user).prefetch_related("analyses")
        items = [analysis for resume in queryset for analysis in resume.analyses.all()]
        return Response(AnalysisSerializer(items, many=True).data)
