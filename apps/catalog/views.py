from django.views.generic import ListView, DetailView
from django.db.models import Q
from django.contrib.auth.mixins import LoginRequiredMixin

from .models import Producto, Categoria, DefinicionAtributo, ProductoAtributo
from apps.accounts.models import Cliente


class CatalogoView(LoginRequiredMixin, ListView):
    """Vista del catálogo de productos con filtros dinámicos por categoría."""
    model = Producto
    template_name = 'catalog/lista_fixed.html'
    context_object_name = 'productos'
    paginate_by = 24
    
    def _aplicar_filtros(self, queryset, params, excluir_atributo=None):
        """
        Aplica filtros al queryset basado en los parámetros GET.
        Permite excluir un atributo específico (útil para calcular opciones disponibles).
        """
        # Búsqueda por texto (siempre aplica)
        busqueda = params.get('q', '')
        if busqueda:
            queryset = queryset.filter(
                Q(nombre__icontains=busqueda) |
                Q(sku__icontains=busqueda) |
                Q(descripcion__icontains=busqueda)
            )
        
        # Filtro por categoría (siempre aplica)
        categoria_id = params.get('categoria')
        if categoria_id:
            try:
                categoria = Categoria.objects.get(id=categoria_id)
                cat_ids = [categoria.id]
                for sub in categoria.subcategorias.filter(activa=True):
                    cat_ids.append(sub.id)
                queryset = queryset.filter(categorias__id__in=cat_ids)
            except Categoria.DoesNotExist:
                pass
        
        # Filtros dinámicos legacy
        for i in range(1, 6):
            valor = params.get(f'filtro_{i}')
            if valor:
                queryset = queryset.filter(**{f'filtro_{i}': valor})
                
        # Filtros por atributos dinámicos
        for key, values in params.lists():
            if key.startswith('attr_'):
                nombre_atributo = key[5:]
                # Si estamos excluyendo este atributo, lo saltamos
                if excluir_atributo and nombre_atributo == excluir_atributo:
                    continue
                    
                valores = [v for v in values if v]
                if valores:
                    queryset = queryset.filter(
                        atributos__definicion__nombre=nombre_atributo,
                        atributos__valor__in=valores
                    )
        
        return queryset

    def get_queryset(self):
        queryset = Producto.objects.filter(activo=True).prefetch_related(
            'categorias', 'atributos', 'atributos__definicion'
        )
        # Usar el método helper para aplicar todos los filtros
        return self._aplicar_filtros(queryset, self.request.GET).distinct()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Categorías para el sidebar
        context['categorias'] = Categoria.objects.filter(activa=True, padre=None).prefetch_related('subcategorias')
        
        # Descuento del cliente...
        context['descuento_cliente'] = 0
        if self.request.user.is_authenticated:
            try:
                context['descuento_cliente'] = self.request.user.cliente.descuento
            except Cliente.DoesNotExist:
                pass
        
        # Params actuales
        context['busqueda'] = self.request.GET.get('q', '')
        context['categoria_actual'] = self.request.GET.get('categoria', '')
        
        # Filtros dinámicos dependientes
        context['filtros_dinamicos'] = []
        categoria_id = self.request.GET.get('categoria')
        
        if categoria_id:
            try:
                categoria = Categoria.objects.get(id=categoria_id)
                definiciones = DefinicionAtributo.objects.filter(
                    categoria=categoria,
                    activo=True,
                    mostrar_en_filtros=True
                ).order_by('orden')
                
                # Base queryset para calcular disponibilidad
                base_queryset = Producto.objects.filter(activo=True)
                
                # Control de desbloqueo por niveles (orden)
                # Empezamos mostrando solo el nivel 1
                max_orden_visible = 1
                
                # Pre-calcular el nivel máximo visible basado en selecciones
                # Si se selecciona algo de nivel N, desbloqueamos nivel N+1
                sorted_definiciones = list(definiciones)
                
                # Mapa de orden -> tiene_seleccion?
                orden_tiene_seleccion = {}
                for defn in sorted_definiciones:
                   sel = self.request.GET.getlist(f'attr_{defn.nombre}')
                   if sel:
                       orden_tiene_seleccion[defn.orden] = True
                
                # Determinar hasta qué orden mostrar
                # Iteramos por orden. Si el orden actual tiene selección, dejamos ver el siguiente orden.
                # (Asumimos que sorted_definiciones está ordenado por 'orden')
                
                current_checked_order = 0
                for defn in sorted_definiciones:
                    if defn.orden > current_checked_order:
                        current_checked_order = defn.orden
                        # Si hay selección en este nivel (o niveles anteriores), 
                        # permitimos ver el siguiente nivel (current + 1)
                        if orden_tiene_seleccion.get(current_checked_order):
                            if current_checked_order + 1 > max_orden_visible:
                                max_orden_visible = current_checked_order + 1
                        # Si NO hay selección en este nivel, max_visible se queda aquí, 
                        # pero permitimos ver items HERMANOS (del mismo nivel).
                
                for defn in sorted_definiciones:
                    # Si el orden de esta def es mayor al permitido, ocultar (break)
                    if defn.orden > max_orden_visible:
                        break

                    # Calcular qué valores son válidos para ESTE atributo...
                    qs_para_opciones = self._aplicar_filtros(
                        base_queryset, 
                        self.request.GET, 
                        excluir_atributo=defn.nombre
                    )
                    
                    valores_disponibles = ProductoAtributo.objects.filter(
                        definicion=defn,
                        producto__in=qs_para_opciones
                    ).values_list('valor', flat=True).distinct()
                    
                    valores_validos = set(v for v in valores_disponibles if v)
                    
                    opciones_finales = []
                    if defn.tipo == 'lista' and defn.opciones:
                        opciones_finales = [op for op in defn.opciones if op in valores_validos]
                    else:
                        opciones_finales = list(valores_validos)
                    
                    seleccionados = self.request.GET.getlist(f'attr_{defn.nombre}')
                    
                    if opciones_finales:
                        context['filtros_dinamicos'].append({
                            'nombre': defn.nombre,
                            'etiqueta': defn.etiqueta,
                            'tipo': defn.tipo,
                            'opciones': sorted(opciones_finales),
                            'seleccionados': seleccionados,
                            'orden': defn.orden
                        })
                        
            except Categoria.DoesNotExist:
                pass
        
        return context


class ProductoDetalleView(LoginRequiredMixin, DetailView):
    """Vista de detalle de un producto."""
    model = Producto
    template_name = 'catalog/detalle.html'
    context_object_name = 'producto'
    
    def get_queryset(self):
        return Producto.objects.prefetch_related(
            'atributos', 'atributos__definicion', 'categorias'
        )
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Descuento del cliente
        context['descuento_cliente'] = 0
        if self.request.user.is_authenticated:
            try:
                context['descuento_cliente'] = self.request.user.cliente.descuento
            except Cliente.DoesNotExist:
                pass
        
        # Atributos del producto organizados
        context['atributos_producto'] = self.object.atributos.select_related('definicion').order_by('definicion__orden')
        
        return context
