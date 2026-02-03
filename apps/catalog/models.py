from django.db import models


class Categoria(models.Model):
    """
    Categoría de productos con soporte para subcategorías.
    """
    nombre = models.CharField(max_length=200, verbose_name='Nombre')
    padre = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='subcategorias',
        verbose_name='Categoría padre'
    )
    orden = models.PositiveIntegerField(default=0, verbose_name='Orden')
    activa = models.BooleanField(default=True, verbose_name='Activa')
    
    class Meta:
        verbose_name = 'Categoría'
        verbose_name_plural = 'Categorías'
        ordering = ['orden', 'nombre']
    
    def __str__(self):
        if self.padre:
            return f"{self.padre.nombre} > {self.nombre}"
        return self.nombre
    
    @property
    def es_subcategoria(self):
        return self.padre is not None


class ConfiguracionFiltro(models.Model):
    """
    Define qué filtros están disponibles para cada categoría.
    """
    categoria = models.ForeignKey(
        Categoria,
        on_delete=models.CASCADE,
        related_name='configuracion_filtros',
        verbose_name='Categoría'
    )
    nombre_campo = models.CharField(
        max_length=50,
        choices=[
            ('filtro_1', 'Filtro 1'),
            ('filtro_2', 'Filtro 2'),
            ('filtro_3', 'Filtro 3'),
            ('filtro_4', 'Filtro 4'),
            ('filtro_5', 'Filtro 5'),
        ],
        verbose_name='Campo'
    )
    etiqueta = models.CharField(
        max_length=100,
        verbose_name='Etiqueta',
        help_text='Nombre visible del filtro (ej: "Diámetro", "Material")'
    )
    activo = models.BooleanField(default=True, verbose_name='Activo')
    orden = models.PositiveIntegerField(default=0, verbose_name='Orden')
    
    class Meta:
        verbose_name = 'Configuración de Filtro'
        verbose_name_plural = 'Configuraciones de Filtros'
        ordering = ['orden']
        unique_together = ['categoria', 'nombre_campo']
    
    def __str__(self):
        return f"{self.categoria.nombre} - {self.etiqueta}"


class Producto(models.Model):
    """
    Producto del catálogo.
    """
    sku = models.CharField(
        max_length=50,
        unique=True,
        verbose_name='SKU',
        help_text='Código único del producto'
    )
    nombre = models.CharField(max_length=300, verbose_name='Nombre')
    descripcion = models.TextField(blank=True, verbose_name='Descripción')
    precio = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        verbose_name='Precio'
    )
    stock = models.IntegerField(default=0, verbose_name='Stock')
    
    # Categorías (puede pertenecer a varias)
    categorias = models.ManyToManyField(
        Categoria,
        blank=True,
        related_name='productos',
        verbose_name='Categorías'
    )
    
    # Filtros dinámicos (5 campos genéricos)
    filtro_1 = models.CharField(max_length=200, blank=True, verbose_name='Filtro 1')
    filtro_2 = models.CharField(max_length=200, blank=True, verbose_name='Filtro 2')
    filtro_3 = models.CharField(max_length=200, blank=True, verbose_name='Filtro 3')
    filtro_4 = models.CharField(max_length=200, blank=True, verbose_name='Filtro 4')
    filtro_5 = models.CharField(max_length=200, blank=True, verbose_name='Filtro 5')
    
    # Imagen del producto
    imagen = models.ImageField(
        upload_to='productos/',
        blank=True,
        null=True,
        verbose_name='Imagen'
    )
    
    activo = models.BooleanField(default=True, verbose_name='Activo')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Creado')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Actualizado')
    
    class Meta:
        verbose_name = 'Producto'
        verbose_name_plural = 'Productos'
        ordering = ['nombre']
    
    def __str__(self):
        return f"{self.sku} - {self.nombre}"
    
    def precio_con_descuento(self, descuento_porcentaje):
        """Calcula el precio con descuento del cliente."""
        if descuento_porcentaje > 0:
            descuento = self.precio * (descuento_porcentaje / 100)
            return self.precio - descuento
        return self.precio


class DefinicionAtributo(models.Model):
    """
    Define un atributo dinámico para una categoría específica.
    Permite configurar filtros personalizados por tipo de producto.
    """
    TIPO_CHOICES = [
        ('texto', 'Texto libre'),
        ('lista', 'Lista de opciones'),
        ('numero', 'Número'),
    ]
    
    categoria = models.ForeignKey(
        Categoria,
        on_delete=models.CASCADE,
        related_name='definiciones_atributos',
        verbose_name='Categoría'
    )
    nombre = models.CharField(
        max_length=50,
        verbose_name='Nombre interno',
        help_text='Identificador único (ej: tipo_fabricacion)'
    )
    etiqueta = models.CharField(
        max_length=100,
        verbose_name='Etiqueta',
        help_text='Nombre visible (ej: Tipo de Fabricación)'
    )
    tipo = models.CharField(
        max_length=20,
        choices=TIPO_CHOICES,
        default='texto',
        verbose_name='Tipo de dato'
    )
    opciones = models.JSONField(
        default=list,
        blank=True,
        verbose_name='Opciones',
        help_text='Para tipo "lista": ["opcion1", "opcion2", ...]'
    )
    orden = models.PositiveIntegerField(default=0, verbose_name='Orden')
    mostrar_en_filtros = models.BooleanField(
        default=True,
        verbose_name='Mostrar en filtros'
    )
    activo = models.BooleanField(default=True, verbose_name='Activo')
    
    class Meta:
        verbose_name = 'Definición de Atributo'
        verbose_name_plural = 'Definiciones de Atributos'
        ordering = ['categoria', 'orden']
        unique_together = ['categoria', 'nombre']
    
    def __str__(self):
        return f"{self.categoria.nombre} - {self.etiqueta}"


class ProductoAtributo(models.Model):
    """
    Valor de un atributo para un producto específico.
    """
    producto = models.ForeignKey(
        Producto,
        on_delete=models.CASCADE,
        related_name='atributos'
    )
    definicion = models.ForeignKey(
        DefinicionAtributo,
        on_delete=models.CASCADE,
        related_name='valores'
    )
    valor = models.CharField(max_length=500, verbose_name='Valor')
    
    class Meta:
        verbose_name = 'Atributo de Producto'
        verbose_name_plural = 'Atributos de Productos'
        unique_together = ['producto', 'definicion']
        indexes = [
            models.Index(fields=['definicion', 'valor']),
        ]
    
    def __str__(self):
        return f"{self.producto.sku} - {self.definicion.etiqueta}: {self.valor}"

