from django.shortcuts import redirect, get_object_or_404
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse

from apps.catalog.models import Producto
from .cart import Carrito


class CarritoView(LoginRequiredMixin, TemplateView):
    """Vista del carrito de compras."""
    template_name = 'cart/carrito.html'


@login_required
def agregar_al_carrito(request, producto_id):
    """Agregar producto al carrito."""
    producto = get_object_or_404(Producto, id=producto_id, activo=True)
    carrito = Carrito(request)
    
    cantidad = int(request.POST.get('cantidad', 1))
    carrito.agregar(producto, cantidad)
    
    messages.success(request, f'"{producto.nombre}" agregado al carrito.')
    
    # Si es AJAX, devolver JSON
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'total_items': len(carrito),
            'message': f'"{producto.nombre}" agregado al carrito.'
        })
    
    # Redirigir a donde venía o al catálogo
    return redirect(request.META.get('HTTP_REFERER', 'catalog:lista'))


@login_required
def quitar_del_carrito(request, producto_id):
    """Quitar producto del carrito."""
    producto = get_object_or_404(Producto, id=producto_id)
    carrito = Carrito(request)
    carrito.quitar(producto)
    
    messages.info(request, f'"{producto.nombre}" eliminado del carrito.')
    
    return redirect('cart:ver')


@login_required
def actualizar_cantidad(request, producto_id):
    """Actualizar cantidad de un producto."""
    producto = get_object_or_404(Producto, id=producto_id)
    carrito = Carrito(request)
    
    cantidad = int(request.POST.get('cantidad', 0))
    carrito.actualizar_cantidad(producto, cantidad)
    
    return redirect('cart:ver')


@login_required
def limpiar_carrito(request):
    """Vaciar el carrito."""
    carrito = Carrito(request)
    carrito.limpiar()
    
    messages.info(request, 'Carrito vaciado.')
    
    return redirect('cart:ver')
