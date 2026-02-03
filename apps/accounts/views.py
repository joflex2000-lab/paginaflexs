from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, TemplateView
from django.contrib.auth import views as auth_views
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required

from .forms import LoginForm, RegistroForm
from .models import Cliente


class LoginView(auth_views.LoginView):
    """Vista de login personalizada."""
    template_name = 'accounts/login.html'
    authentication_form = LoginForm
    redirect_authenticated_user = True


class LogoutView(auth_views.LogoutView):
    """Vista de logout."""
    next_page = 'core:home'


class RegistroView(CreateView):
    """Vista de registro para nuevos clientes."""
    template_name = 'accounts/registro.html'
    form_class = RegistroForm
    success_url = reverse_lazy('accounts:login')
    
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('catalog:lista')
        return super().dispatch(request, *args, **kwargs)
    
    def form_valid(self, form):
        response = super().form_valid(form)
        # Aquí podrías agregar mensaje de éxito
        return response


@login_required
def post_login_redirect(request):
    """
    Redirige según el rol del usuario:
    - Admin: página de selección (panel o catálogo)
    - Cliente: directo al catálogo
    """
    if request.user.es_admin:
        return redirect('accounts:perfil')  # Temporalmente al perfil, luego a selección
    else:
        return redirect('catalog:lista')


class PerfilView(LoginRequiredMixin, TemplateView):
    """Vista del perfil del usuario."""
    template_name = 'accounts/perfil.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Obtener cliente si existe
        try:
            context['cliente'] = self.request.user.cliente
        except Cliente.DoesNotExist:
            context['cliente'] = None
        
        return context
