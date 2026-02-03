from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('registro/', views.RegistroView.as_view(), name='registro'),
    path('redirigir/', views.post_login_redirect, name='post_login_redirect'),
    path('perfil/', views.PerfilView.as_view(), name='perfil'),
]
