from django.urls import path
from . import views

app_name = 'cart'

urlpatterns = [
    path('', views.CarritoView.as_view(), name='ver'),
    path('agregar/<int:producto_id>/', views.agregar_al_carrito, name='agregar'),
    path('quitar/<int:producto_id>/', views.quitar_del_carrito, name='quitar'),
    path('actualizar/<int:producto_id>/', views.actualizar_cantidad, name='actualizar'),
    path('limpiar/', views.limpiar_carrito, name='limpiar'),
]
