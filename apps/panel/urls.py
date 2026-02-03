from django.urls import path
from . import views

app_name = 'panel'

urlpatterns = [
    # Dashboard
    path('', views.DashboardView.as_view(), name='dashboard'),
    
    # Productos
    path('productos/', views.ProductosListView.as_view(), name='productos'),
    path('productos/nuevo/', views.ProductoCreateView.as_view(), name='producto_crear'),
    path('productos/<int:pk>/', views.ProductoUpdateView.as_view(), name='producto_editar'),
    path('productos/<int:pk>/eliminar/', views.ProductoDeleteView.as_view(), name='producto_eliminar'),
    path('productos/eliminar-todos/', views.delete_all_products, name='eliminar_todos_productos'),
    
    # Clientes
    path('clientes/', views.ClientesListView.as_view(), name='clientes'),
    path('clientes/nuevo/', views.ClienteCreateView.as_view(), name='cliente_crear'),
    path('clientes/<int:pk>/', views.ClienteUpdateView.as_view(), name='cliente_editar'),
    path('clientes/<int:pk>/eliminar/', views.ClienteDeleteView.as_view(), name='cliente_eliminar'),
    path('clientes/<int:pk>/password/', views.change_client_password, name='cliente_cambiar_password'),
    path('clientes/eliminar-todos/', views.delete_all_clients, name='eliminar_todos_clientes'),
    
    # Pedidos
    path('pedidos/', views.PedidosListView.as_view(), name='pedidos'),
    path('pedidos/<int:pk>/', views.PedidoDetailView.as_view(), name='pedido_detalle'),
    path('pedidos/<int:pk>/estado/', views.cambiar_estado_pedido, name='pedido_cambiar_estado'),
    
    # Categorías
    path('categorias/', views.CategoriasListView.as_view(), name='categorias'),
    path('categorias/nueva/', views.CategoriaCreateView.as_view(), name='categoria_crear'),
    path('categorias/<int:pk>/', views.CategoriaUpdateView.as_view(), name='categoria_editar'),
    path('categorias/<int:pk>/productos/', views.CategoriaProductosView.as_view(), name='categoria_productos'),
]
