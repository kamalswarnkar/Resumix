from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

from .views import (
    AnalysisTemplateView,
    DashboardTemplateView,
    LandingTemplateView,
    LoginTemplateView,
    RegisterTemplateView,
    UploadTemplateView,
)

urlpatterns = [
    path("", LandingTemplateView.as_view(), name="landing"),
    path("register/", RegisterTemplateView.as_view(), name="register-page"),
    path("login/", LoginTemplateView.as_view(), name="login-page"),
    path("dashboard/", DashboardTemplateView.as_view(), name="dashboard-page"),
    path("upload/", UploadTemplateView.as_view(), name="upload-page"),
    path("analysis/", AnalysisTemplateView.as_view(), name="analysis-page"),
    path("admin/", admin.site.urls),
    path("api/auth/", include("users.urls")),
    path("api/resume/", include("resumes.urls")),
    path("api/admin/", include("analysis.admin_urls")),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
