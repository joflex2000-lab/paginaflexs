from decimal import Decimal
from apps.catalog.models import Producto


class Carrito:
    """
    Carrito de compras almacenado en la sesión.
    """
    
    def __init__(self, request):
        self.session = request.session
        carrito = self.session.get('carrito')
        
        if not carrito:
            carrito = self.session['carrito'] = {}
        
        self.carrito = carrito
        
        # Obtener descuento del cliente
        self.descuento = Decimal('0')
        if request.user.is_authenticated:
            try:
                self.descuento = request.user.cliente.descuento
            except:
                pass
    
    def agregar(self, producto, cantidad=1):
        """Agregar producto al carrito."""
        producto_id = str(producto.id)
        
        if producto_id not in self.carrito:
            self.carrito[producto_id] = {
                'cantidad': 0,
                'precio': str(producto.precio)
            }
        
        self.carrito[producto_id]['cantidad'] += cantidad
        self.guardar()
    
    def quitar(self, producto):
        """Quitar producto del carrito."""
        producto_id = str(producto.id)
        
        if producto_id in self.carrito:
            del self.carrito[producto_id]
            self.guardar()
    
    def actualizar_cantidad(self, producto, cantidad):
        """Actualizar cantidad de un producto."""
        producto_id = str(producto.id)
        
        if producto_id in self.carrito:
            if cantidad > 0:
                self.carrito[producto_id]['cantidad'] = cantidad
            else:
                del self.carrito[producto_id]
            self.guardar()
    
    def guardar(self):
        """Guardar cambios en la sesión."""
        self.session.modified = True
    
    def limpiar(self):
        """Vaciar el carrito."""
        del self.session['carrito']
        self.guardar()
    
    def __iter__(self):
        """Iterar sobre los items del carrito."""
        producto_ids = self.carrito.keys()
        productos = Producto.objects.filter(id__in=producto_ids)
        
        carrito = self.carrito.copy()
        
        for producto in productos:
            carrito[str(producto.id)]['producto'] = producto
        
        for item in carrito.values():
            if 'producto' in item:
                item['precio'] = Decimal(item['precio'])
                item['precio_con_descuento'] = item['producto'].precio_con_descuento(self.descuento)
                item['subtotal'] = item['precio_con_descuento'] * item['cantidad']
                yield item
    
    def __len__(self):
        """Cantidad total de items."""
        return sum(item['cantidad'] for item in self.carrito.values())
    
    def get_total(self):
        """Total del carrito con descuento aplicado."""
        total = Decimal('0')
        
        for item in self:
            total += item['subtotal']
        
        return total
    
    def get_total_sin_descuento(self):
        """Total del carrito sin descuento."""
        return sum(
            Decimal(item['precio']) * item['cantidad']
            for item in self.carrito.values()
        )
