"""
Abrazaderas Importer - Importador especializado con anti-duplicado.
Extrae atributos automáticamente de la descripción.
"""
from decimal import Decimal, InvalidOperation
from apps.catalog.models import Producto, Categoria, DefinicionAtributo, ProductoAtributo
from .base import BaseImporter
from ..parsers.abrazaderas import AbrazaderaParser


class AbrazaderaImporter(BaseImporter):
    """
    Importador especializado para abrazaderas.
    - Usa columnas: codigo, descripcion, precio
    - Extrae atributos automáticamente de la descripción
    - Anti-duplicado por SKU (codigo)
    - Asignación automática a categoría Abrazaderas
    """
    
    TIPO = 'abrazaderas'
    COLUMNAS_REQUERIDAS = ['codigo', 'descripcion']
    COLUMNAS_OPCIONALES = ['precio', 'stock']
    
    def __init__(self, archivo, usuario=None, opciones=None):
        super().__init__(archivo, usuario, opciones)
        self.categoria_abrazaderas = None
        self.definiciones = {}
    
    def _inicializar_categoria(self):
        """Obtiene o crea la categoría Abrazaderas."""
        if self.categoria_abrazaderas:
            return
        
        self.categoria_abrazaderas, created = Categoria.objects.get_or_create(
            nombre__iexact='Abrazaderas',
            defaults={'nombre': 'Abrazaderas', 'activa': True}
        )
        
        # Cargar definiciones de atributos existentes
        for defn in DefinicionAtributo.objects.filter(
            categoria=self.categoria_abrazaderas,
            activo=True
        ):
            self.definiciones[defn.nombre] = defn
    
    def _asegurar_definiciones_base(self):
        """Crea las definiciones de atributos base si no existen."""
        if not self.categoria_abrazaderas:
            self._inicializar_categoria()
        
        definiciones_base = [
            {
                'nombre': 'tipo_fabricacion',
                'etiqueta': 'Tipo de Fabricación',
                'tipo': 'lista',
                'opciones': ['TREFILADA', 'LAMINADA'],
                'orden': 1
            },
            {
                'nombre': 'medida_pulgadas',
                'etiqueta': 'Medida (pulgadas)',
                'tipo': 'lista',
                'opciones': [],  # Se llenarán automáticamente
                'orden': 2
            },
            {
                'nombre': 'material',
                'etiqueta': 'Material',
                'tipo': 'lista',
                'opciones': ['ACERO', 'INOX', 'GALVANIZADO'],
                'orden': 3
            },
            {
                'nombre': 'ancho',
                'etiqueta': 'Ancho (mm)',
                'tipo': 'numero',
                'opciones': [],
                'orden': 4
            },
            {
                'nombre': 'largo',
                'etiqueta': 'Largo (mm)',
                'tipo': 'numero',
                'opciones': [],
                'orden': 5
            },
            {
                'nombre': 'forma',
                'etiqueta': 'Forma',
                'tipo': 'lista',
                'opciones': ['CURVA', 'PLANA', 'SEMICURVA', '/S/CURVA'],
                'orden': 6
            },
        ]
        
        for defn_data in definiciones_base:
            defn, created = DefinicionAtributo.objects.get_or_create(
                categoria=self.categoria_abrazaderas,
                nombre=defn_data['nombre'],
                defaults={
                    'etiqueta': defn_data['etiqueta'],
                    'tipo': defn_data['tipo'],
                    'opciones': defn_data['opciones'],
                    'orden': defn_data['orden'],
                    'mostrar_en_filtros': True,
                    'activo': True
                }
            )
            self.definiciones[defn.nombre] = defn
    
    def preview(self):
        """Override para inicializar categoría antes del preview."""
        self._inicializar_categoria()
        self._asegurar_definiciones_base()
        return super().preview()
    
    def procesar_fila(self, fila, dry_run=False):
        """Procesa una fila de abrazadera extrayendo atributos de la descripción."""
        # Obtener valores - aceptar variaciones de nombres de columna
        sku = self.get_valor(fila, 'codigo', '') or self.get_valor(fila, 'SKU', '') or self.get_valor(fila, 'Codigo', '')
        sku = str(sku).strip()
        if not sku:
            raise ValueError("Codigo/SKU es requerido")
        
        descripcion = self.get_valor(fila, 'descripcion', '') or self.get_valor(fila, 'Descripcion', '') or self.get_valor(fila, 'nombre', '') or self.get_valor(fila, 'Nombre', '')
        descripcion = str(descripcion).strip()
        if not descripcion:
            raise ValueError("Descripcion es requerida")
        
        # Precio (opcional)
        precio_raw = self.get_valor(fila, 'precio', '') or self.get_valor(fila, 'Precio', '')
        precio = None
        if precio_raw:
            try:
                precio_str = str(precio_raw).replace('$', '').replace(' ', '').strip()
                if ',' in precio_str and '.' in precio_str:
                    precio_str = precio_str.replace('.', '').replace(',', '.')
                elif ',' in precio_str:
                    precio_str = precio_str.replace(',', '.')
                precio = Decimal(precio_str).quantize(Decimal('0.01'))
            except (InvalidOperation, ValueError):
                pass
        
        # Stock (opcional)
        stock_raw = self.get_valor(fila, 'stock', '') or self.get_valor(fila, 'Stock', '')
        stock = None
        if stock_raw:
            try:
                stock = int(float(str(stock_raw)))
            except (ValueError, TypeError):
                pass
        
        # PARSEAR ATRIBUTOS DE LA DESCRIPCIÓN
        resultado_parser = AbrazaderaParser.parsear(descripcion)
        atributos_detectados = resultado_parser['atributos']
        
        # Verificar si el producto existe (anti-duplicado)
        try:
            producto = Producto.objects.get(sku=sku)
            accion = 'actualizar'
        except Producto.DoesNotExist:
            producto = None
            accion = 'crear'
        
        if dry_run:
            return (accion, None)
        
        # Ejecutar
        if not self.categoria_abrazaderas:
            self._inicializar_categoria()
            self._asegurar_definiciones_base()
        
        if producto:
            # UPDATE
            producto.nombre = descripcion
            if precio is not None:
                producto.precio = precio
            if stock is not None:
                producto.stock = stock
            producto.save()
        else:
            # CREATE
            producto = Producto.objects.create(
                sku=sku,
                nombre=descripcion,
                precio=precio or Decimal('0'),
                stock=stock or 0
            )
        
        # Asignar categoría Abrazaderas si no la tiene
        if self.categoria_abrazaderas not in producto.categorias.all():
            producto.categorias.add(self.categoria_abrazaderas)
        
        # Crear/actualizar atributos detectados
        for nombre_attr, valor in atributos_detectados.items():
            if valor and nombre_attr in self.definiciones:
                ProductoAtributo.objects.update_or_create(
                    producto=producto,
                    definicion=self.definiciones[nombre_attr],
                    defaults={'valor': str(valor).strip()}
                )
                
                # Agregar valor a las opciones si no existe (para filtros tipo lista)
                defn = self.definiciones[nombre_attr]
                if defn.tipo == 'lista' and valor not in defn.opciones:
                    defn.opciones.append(valor)
                    defn.save(update_fields=['opciones'])
        
        return (accion, producto)
