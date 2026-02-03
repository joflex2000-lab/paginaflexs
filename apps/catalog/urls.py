from django.urls import path
from . import views

app_name = 'catalog'

urlpatterns = [
    path('', views.CatalogoView.as_view(), name='lista'),
    path('producto/<int:pk>/', views.ProductoDetalleView.as_view(), name='detalle'),
]
