from django.views.generic import TemplateView


class LandingTemplateView(TemplateView):
    template_name = "frontend_template.html"


class RegisterTemplateView(TemplateView):
    template_name = "register.html"


class LoginTemplateView(TemplateView):
    template_name = "login.html"


class DashboardTemplateView(TemplateView):
    template_name = "dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["active_page"] = "dashboard"
        return context


class UploadTemplateView(TemplateView):
    template_name = "upload.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["active_page"] = "upload"
        return context


class AnalysisTemplateView(TemplateView):
    template_name = "analysis.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["active_page"] = "analysis"
        return context
