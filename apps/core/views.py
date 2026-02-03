from django.views.generic import TemplateView


class HomeView(TemplateView):
    """Página de inicio pública."""
    template_name = 'core/home.html'
