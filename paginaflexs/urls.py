"""
URL configuration for paginaflexs project.
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Django admin (solo superusuario)
    path('django-admin/', admin.site.urls),
    
    # Apps propias
    path('', include('apps.core.urls')),
    path('cuenta/', include('apps.accounts.urls')),
    path('catalogo/', include('apps.catalog.urls')),
    path('carrito/', include('apps.cart.urls')),
    path('pedidos/', include('apps.orders.urls')),
    path('panel/', include('apps.panel.urls')),
    path('panel/importar/', include('apps.imports.urls')),
]

# Servir archivos media en desarrollo
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
