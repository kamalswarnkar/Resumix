from django.urls import path

from .views import ResumeViewSet

urlpatterns = [
    path("upload/", ResumeViewSet.as_view({"post": "upload"}), name="resume-upload"),
    path("analyze/", ResumeViewSet.as_view({"post": "analyze"}), name="resume-analyze"),
    path("history/", ResumeViewSet.as_view({"get": "history"}), name="resume-history"),
]
