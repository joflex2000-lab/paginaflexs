from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    path('', views.MisPedidosView.as_view(), name='lista'),
    path('crear/', views.crear_pedido, name='crear'),
    path('<int:pk>/', views.DetallePedidoView.as_view(), name='detalle'),
]
