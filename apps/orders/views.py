from django.shortcuts import redirect, get_object_or_404
from django.views.generic import ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .models import Pedido, ItemPedido
from apps.cart.cart import Carrito
from apps.accounts.models import Cliente


class MisPedidosView(LoginRequiredMixin, ListView):
    """Lista de pedidos del cliente."""
    model = Pedido
    template_name = 'orders/lista.html'
    context_object_name = 'pedidos'
    paginate_by = 10
    
    def get_queryset(self):
        # Si es admin, ver todos los pedidos
        if self.request.user.es_admin:
            return Pedido.objects.all()
        
        # Si es cliente, solo sus pedidos
        try:
            cliente = self.request.user.cliente
            return Pedido.objects.filter(cliente=cliente)
        except Cliente.DoesNotExist:
            return Pedido.objects.none()


class DetallePedidoView(LoginRequiredMixin, DetailView):
    """Detalle de un pedido."""
    model = Pedido
    template_name = 'orders/detalle.html'
    context_object_name = 'pedido'
    
    def get_queryset(self):
        # Admin puede ver cualquier pedido
        if self.request.user.es_admin:
            return Pedido.objects.all()
        
        # Cliente solo ve sus pedidos
        try:
            cliente = self.request.user.cliente
            return Pedido.objects.filter(cliente=cliente)
        except Cliente.DoesNotExist:
            return Pedido.objects.none()


@login_required
def crear_pedido(request):
    """Crear pedido desde el carrito."""
    if request.method != 'POST':
        return redirect('cart:ver')
    
    carrito = Carrito(request)
    
    # Verificar que hay items en el carrito
    if len(carrito) == 0:
        messages.error(request, 'El carrito está vacío.')
        return redirect('cart:ver')
    
    # Obtener cliente
    try:
        cliente = request.user.cliente
    except Cliente.DoesNotExist:
        messages.error(request, 'No tienes un perfil de cliente asociado.')
        return redirect('cart:ver')
    
    # Crear el pedido
    pedido = Pedido.objects.create(
        cliente=cliente,
        nota=request.POST.get('nota', ''),
        descuento_aplicado=cliente.descuento
    )
    
    # Crear items del pedido
    subtotal = 0
    for item in carrito:
        precio_con_descuento = item['precio_con_descuento']
        ItemPedido.objects.create(
            pedido=pedido,
            producto=item['producto'],
            cantidad=item['cantidad'],
            precio_unitario=precio_con_descuento
        )
        subtotal += item['subtotal']
    
    # Actualizar totales del pedido
    pedido.subtotal = carrito.get_total_sin_descuento()
    pedido.total = subtotal
    pedido.save()
    
    # Limpiar carrito
    carrito.limpiar()
    
    messages.success(request, f'Pedido #{pedido.id} creado exitosamente.')
    return redirect('orders:detalle', pk=pedido.id)
