from django.views.generic import TemplateView


class FrontendTemplateView(TemplateView):
    template_name = "frontend_template.html"
