from django.shortcuts import redirect, get_object_or_404, render
from django.urls import reverse_lazy
from django.views.generic import TemplateView, ListView, CreateView, UpdateView, DeleteView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db.models import Count, Sum, Q

from apps.catalog.models import Producto, Categoria
from apps.accounts.models import Cliente
from apps.orders.models import Pedido


class AdminRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Mixin que requiere rol de admin."""
    
    def test_func(self):
        return self.request.user.es_admin


class DashboardView(AdminRequiredMixin, TemplateView):
    """Dashboard del panel de administración."""
    template_name = 'panel/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Estadísticas
        context['total_productos'] = Producto.objects.filter(activo=True).count()
        context['total_clientes'] = Cliente.objects.count()
        context['total_pedidos'] = Pedido.objects.count()
        context['pedidos_pendientes'] = Pedido.objects.filter(estado='pendiente').count()
        
        # Últimos pedidos
        context['ultimos_pedidos'] = Pedido.objects.select_related('cliente')[:5]
        
        return context


# ===================== PRODUCTOS =====================

class ProductosListView(AdminRequiredMixin, ListView):
    """Lista de productos."""
    model = Producto
    template_name = 'panel/productos/lista.html'
    context_object_name = 'productos'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = Producto.objects.all()
        
        # Búsqueda
        busqueda = self.request.GET.get('q', '')
        if busqueda:
            queryset = queryset.filter(
                Q(nombre__icontains=busqueda) |
                Q(sku__icontains=busqueda)
            )
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['busqueda'] = self.request.GET.get('q', '')
        return context


class ProductoCreateView(AdminRequiredMixin, CreateView):
    """Crear producto."""
    model = Producto
    template_name = 'panel/productos/form.html'
    fields = ['sku', 'nombre', 'descripcion', 'precio', 'stock', 'categorias', 
              'filtro_1', 'filtro_2', 'filtro_3', 'filtro_4', 'filtro_5', 'imagen', 'activo']
    success_url = reverse_lazy('panel:productos')
    
    def form_valid(self, form):
        messages.success(self.request, 'Producto creado exitosamente.')
        return super().form_valid(form)


class ProductoUpdateView(AdminRequiredMixin, UpdateView):
    """Editar producto."""
    model = Producto
    template_name = 'panel/productos/form.html'
    fields = ['sku', 'nombre', 'descripcion', 'precio', 'stock', 'categorias',
              'filtro_1', 'filtro_2', 'filtro_3', 'filtro_4', 'filtro_5', 'imagen', 'activo']
    success_url = reverse_lazy('panel:productos')
    
    def form_valid(self, form):
        messages.success(self.request, 'Producto actualizado exitosamente.')
        return super().form_valid(form)


class ProductoDeleteView(AdminRequiredMixin, DeleteView):
    """Eliminar producto."""
    model = Producto
    template_name = 'panel/productos/confirmar_eliminar.html'
    success_url = reverse_lazy('panel:productos')
    
    def form_valid(self, form):
        messages.success(self.request, 'Producto eliminado.')
        return super().form_valid(form)


# ===================== CLIENTES =====================

class ClientesListView(AdminRequiredMixin, ListView):
    """Lista de clientes."""
    model = Cliente
    template_name = 'panel/clientes/lista.html'
    context_object_name = 'clientes'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = Cliente.objects.select_related('usuario').all()
        
        # Búsqueda
        busqueda = self.request.GET.get('q', '')
        if busqueda:
            queryset = queryset.filter(
                Q(nombre__icontains=busqueda) |
                Q(cuit_dni__icontains=busqueda) |
                Q(usuario__username__icontains=busqueda)
            )
        
        return queryset


class ClienteCreateView(AdminRequiredMixin, CreateView):
    """Crear cliente manualmente."""
    model = Cliente
    template_name = 'panel/clientes/form.html'
    fields = ['nombre', 'contacto', 'tipo_cliente', 'provincia', 'domicilio',
              'telefonos', 'cuit_dni', 'descuento', 'condicion_iva']
    success_url = reverse_lazy('panel:clientes')
    
    def form_valid(self, form):
        # Obtener credenciales del formulario
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        username = self.request.POST.get('username', '').strip()
        password = self.request.POST.get('password', '').strip()
        
        if not username:
            form.add_error(None, 'El username es requerido')
            return self.form_invalid(form)
        
        if not password:
            form.add_error(None, 'La contraseña es requerida')
            return self.form_invalid(form)
        
        # Verificar si el username ya existe
        if User.objects.filter(username=username).exists():
            form.add_error(None, f'El usuario "{username}" ya existe. Elegí otro.')
            return self.form_invalid(form)
        
        # Crear usuario
        user = User.objects.create_user(
            username=username,
            password=password,
            email=f"{username}@temporal.com"
        )
        
        # Asignar usuario al cliente
        form.instance.usuario = user
        
        messages.success(
            self.request, 
            f'Cliente creado exitosamente. Usuario: {username} / Contraseña: {password}'
        )
        return super().form_valid(form)


class ClienteUpdateView(AdminRequiredMixin, UpdateView):
    """Editar cliente."""
    model = Cliente
    template_name = 'panel/clientes/form.html'
    fields = ['nombre', 'contacto', 'tipo_cliente', 'provincia', 'domicilio',
              'telefonos', 'cuit_dni', 'descuento', 'condicion_iva']
    success_url = reverse_lazy('panel:clientes')
    

    def form_valid(self, form):
        messages.success(self.request, 'Cliente actualizado exitosamente.')
        return super().form_valid(form)


class ClienteDeleteView(AdminRequiredMixin, DeleteView):
    """Eliminar cliente."""
    model = Cliente
    template_name = 'panel/clientes/confirmar_eliminar.html'
    success_url = reverse_lazy('panel:clientes')
    
    def delete(self, request, *args, **kwargs):
        cliente = self.get_object()
        # El usuario asociado se eliminará automáticamente por CASCADE
        messages.success(request, f'Cliente "{cliente.nombre}" y su usuario asociado fueron eliminados.')
        return super().delete(request, *args, **kwargs)


@login_required
@user_passes_test(lambda u: u.es_admin)
def change_client_password(request, pk):
    """Cambiar contraseña de un cliente."""
    cliente = get_object_or_404(Cliente, pk=pk)
    
    if request.method == 'POST':
        new_password = request.POST.get('new_password', '').strip()
        
        if not new_password:
            messages.error(request, 'La contraseña no puede estar vacía')
        else:
            # Cambiar contraseña
            cliente.usuario.set_password(new_password)
            cliente.usuario.save()
            messages.success(request, f'Contraseña actualizada para {cliente.nombre}. Nueva contraseña: {new_password}')
            return redirect('panel:cliente_editar', pk=pk)
    
    return render(request, 'panel/clientes/cambiar_password.html', {'cliente': cliente})


@login_required
@user_passes_test(lambda u: u.es_admin)
def delete_all_clients(request):
    """Elimina todos los clientes y sus usuarios asociados."""
    if request.method == 'POST':
        # Obtener IDs de usuarios asociados a clientes
        clientes = Cliente.objects.all()
        user_ids = clientes.values_list('usuario_id', flat=True)
        
        # Eliminar clientes
        count_clientes = clientes.count()
        clientes.delete()
        
        # Eliminar usuarios (excepto el propio admin si tuviera cliente, aunque raro)
        from django.contrib.auth import get_user_model
        User = get_user_model()
        users_deleted = User.objects.filter(id__in=user_ids).exclude(id=request.user.id).delete()
        
        messages.success(request, f'Se eliminaron {count_clientes} clientes y sus usuarios asociados.')
    
    return redirect('panel:clientes')


@login_required
@user_passes_test(lambda u: u.es_admin)
def delete_all_products(request):
    """Elimina todos los productos."""
    if request.method == 'POST':
        count = Producto.objects.count()
        Producto.objects.all().delete()
        messages.success(request, f'Se eliminaron {count} productos.')
    
    return redirect('panel:productos')


# ===================== PEDIDOS =====================

class PedidosListView(AdminRequiredMixin, ListView):
    """Lista de pedidos."""
    model = Pedido
    template_name = 'panel/pedidos/lista.html'
    context_object_name = 'pedidos'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = Pedido.objects.select_related('cliente').all()
        
        # Filtro por estado
        estado = self.request.GET.get('estado', '')
        if estado:
            queryset = queryset.filter(estado=estado)
        
        # Búsqueda
        busqueda = self.request.GET.get('q', '')
        if busqueda:
            queryset = queryset.filter(
                Q(cliente__nombre__icontains=busqueda) |
                Q(id__icontains=busqueda)
            )
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['estados'] = Pedido.Estado.choices
        context['estado_actual'] = self.request.GET.get('estado', '')
        return context


class PedidoDetailView(AdminRequiredMixin, DetailView):
    """Detalle de pedido."""
    model = Pedido
    template_name = 'panel/pedidos/detalle.html'
    context_object_name = 'pedido'
    
    def get_queryset(self):
        return Pedido.objects.select_related('cliente').prefetch_related('items__producto')


@login_required
@user_passes_test(lambda u: u.es_admin)
def cambiar_estado_pedido(request, pk):
    """Cambiar estado de un pedido."""
    pedido = get_object_or_404(Pedido, pk=pk)
    
    if request.method == 'POST':
        nuevo_estado = request.POST.get('estado')
        if nuevo_estado in dict(Pedido.Estado.choices):
            pedido.estado = nuevo_estado
            pedido.save()
            messages.success(request, f'Estado del pedido #{pedido.id} actualizado a {pedido.get_estado_display()}.')
    
    return redirect('panel:pedido_detalle', pk=pk)


# ===================== CATEGORÍAS =====================

class CategoriasListView(AdminRequiredMixin, ListView):
    """Lista de categorías."""
    model = Categoria
    template_name = 'panel/categorias/lista.html'
    context_object_name = 'categorias'
    
    def get_queryset(self):
        return Categoria.objects.filter(padre=None).prefetch_related('subcategorias')


class CategoriaCreateView(AdminRequiredMixin, CreateView):
    """Crear categoría."""
    model = Categoria
    template_name = 'panel/categorias/form.html'
    fields = ['nombre', 'padre', 'orden', 'activa']
    success_url = reverse_lazy('panel:categorias')
    
    def form_valid(self, form):
        messages.success(self.request, 'Categoría creada exitosamente.')
        return super().form_valid(form)


class CategoriaUpdateView(AdminRequiredMixin, UpdateView):
    """Editar categoría."""
    model = Categoria
    template_name = 'panel/categorias/form.html'
    fields = ['nombre', 'padre', 'orden', 'activa']
    success_url = reverse_lazy('panel:categorias')
    
    def form_valid(self, form):
        messages.success(self.request, 'Categoría actualizada exitosamente.')
        return super().form_valid(form)


class CategoriaProductosView(AdminRequiredMixin, ListView):
    """Vista para gestionar productos de una categoría masivamente."""
    model = Producto
    template_name = 'panel/categorias/productos.html'
    context_object_name = 'productos'
    paginate_by = 50
    
    def get_queryset(self):
        queryset = Producto.objects.all().order_by('nombre')
        
        # Búsqueda
        busqueda = self.request.GET.get('q', '')
        if busqueda:
            queryset = queryset.filter(
                Q(nombre__icontains=busqueda) |
                Q(sku__icontains=busqueda)
            )
            
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        self.categoria = get_object_or_404(Categoria, pk=self.kwargs['pk'])
        context['categoria'] = self.categoria
        # Set de IDs que ya están en la categoría para marcar checkboxes
        context['productos_en_categoria_ids'] = set(self.categoria.productos.values_list('id', flat=True))
        context['busqueda'] = self.request.GET.get('q', '')
        return context

    def post(self, request, pk):
        categoria = get_object_or_404(Categoria, pk=pk)
        action = request.POST.get('action')
        product_ids = request.POST.getlist('productos')
        
        if not product_ids:
            messages.warning(request, 'No se seleccionaron productos.')
            return redirect(request.path_info + f'?q={request.GET.get("q", "")}&page={request.GET.get("page", 1)}')

        products = Producto.objects.filter(id__in=product_ids)
        count = products.count()

        if action == 'add_selected':
            categoria.productos.add(*products)
            messages.success(request, f'{count} productos agregados a {categoria.nombre}.')
            
        elif action == 'remove_selected':
            categoria.productos.remove(*products)
            messages.success(request, f'{count} productos quitados de {categoria.nombre}.')
            
        return redirect(request.path_info + f'?q={request.GET.get("q", "")}&page={request.GET.get("page", 1)}')
