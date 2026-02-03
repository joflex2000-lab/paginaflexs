"""
Product Importer - Importador de productos desde Excel/CSV.
"""
from decimal import Decimal, InvalidOperation
from apps.catalog.models import Producto, Categoria
from .base import BaseImporter


class ProductImporter(BaseImporter):
    """Importador de productos."""
    
    TIPO = 'productos'
    COLUMNAS_REQUERIDAS = ['SKU', 'Nombre', 'Precio']
    COLUMNAS_OPCIONALES = ['Stock', 'filtro_1', 'filtro_2', 'filtro_3', 'filtro_4', 'filtro_5']
    
    def procesar_fila(self, fila, dry_run=False):
        """Procesa una fila de producto."""
        # Obtener valores
        sku = self.get_valor(fila, 'SKU', '').strip()
        if not sku:
            raise ValueError("SKU es requerido")
        
        nombre = self.get_valor(fila, 'Nombre', '').strip()
        if not nombre:
            raise ValueError("Nombre es requerido")
        
        # Convertir precio a Decimal correctamente
        precio_raw = self.get_valor(fila, 'Precio', '0')
        try:
            # Manejar formatos: 1234.56, 1234,56, "$ 1.234,56"
            precio_str = str(precio_raw).replace('$', '').replace(' ', '').strip()
            
            # Si tiene coma y punto, determinar cuál es el separador decimal
            if ',' in precio_str and '.' in precio_str:
                # Formato argentino: 1.234,56 -> la coma es decimal
                precio_str = precio_str.replace('.', '').replace(',', '.')
            elif ',' in precio_str:
                # Solo coma: 1234,56 -> la coma es decimal
                precio_str = precio_str.replace(',', '.')
            
            precio = Decimal(precio_str).quantize(Decimal('0.01'))
        except (InvalidOperation, ValueError):
            raise ValueError(f"Precio inválido: {precio_raw}")
        
        if precio < 0:
            raise ValueError("Precio debe ser mayor o igual a 0")
        
        stock = self.get_int(fila, 'Stock', 0)
        if stock < 0:
            stock = 0
        
        # Filtros dinámicos
        filtro_1 = self.get_valor(fila, 'filtro_1', '')
        filtro_2 = self.get_valor(fila, 'filtro_2', '')
        filtro_3 = self.get_valor(fila, 'filtro_3', '')
        filtro_4 = self.get_valor(fila, 'filtro_4', '')
        filtro_5 = self.get_valor(fila, 'filtro_5', '')
        
        # Verificar si existe
        try:
            producto = Producto.objects.get(sku=sku)
            accion = 'actualizar'
        except Producto.DoesNotExist:
            producto = None
            accion = 'crear'
        
        if dry_run:
            return (accion, None)
        
        # Ejecutar
        if producto:
            # Update
            producto.nombre = nombre
            producto.precio = precio
            producto.stock = stock
            producto.filtro_1 = filtro_1
            producto.filtro_2 = filtro_2
            producto.filtro_3 = filtro_3
            producto.filtro_4 = filtro_4
            producto.filtro_5 = filtro_5
            producto.save()
        else:
            # Create
            producto = Producto.objects.create(
                sku=sku,
                nombre=nombre,
                precio=precio,
                stock=stock,
                filtro_1=filtro_1,
                filtro_2=filtro_2,
                filtro_3=filtro_3,
                filtro_4=filtro_4,
                filtro_5=filtro_5
            )
        
        return (accion, producto)
