from django.db import models
from django.conf import settings


class ImportLog(models.Model):
    """Registro de cada importación realizada."""
    
    TIPO_CHOICES = [
        ('productos', 'Productos'),
        ('clientes', 'Clientes'),
        ('categorias', 'Categorías'),
        ('abrazaderas', 'Abrazaderas'),
    ]
    
    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('procesando', 'Procesando'),
        ('completado', 'Completado'),
        ('cancelado', 'Cancelado'),
        ('error', 'Error'),
    ]
    
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='pendiente')
    archivo_nombre = models.CharField(max_length=255)
    archivo = models.FileField(upload_to='imports/logs/', null=True, blank=True)
    
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='importaciones'
    )
    
    # Contadores
    total_filas = models.IntegerField(default=0)
    creados = models.IntegerField(default=0)
    actualizados = models.IntegerField(default=0)
    errores = models.IntegerField(default=0)
    procesados = models.IntegerField(default=0)  # Para barra de progreso
    
    # Fechas
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name = 'Log de Importación'
        verbose_name_plural = 'Logs de Importación'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.get_tipo_display()} - {self.created_at.strftime('%d/%m/%Y %H:%M')}"
    
    @property
    def progreso(self):
        """Retorna el porcentaje de progreso."""
        if self.total_filas == 0:
            return 0
        return int((self.procesados / self.total_filas) * 100)


class ImportError(models.Model):
    """Errores individuales durante una importación."""
    
    log = models.ForeignKey(
        ImportLog,
        on_delete=models.CASCADE,
        related_name='errores_detalle'
    )
    fila = models.IntegerField()
    columna = models.CharField(max_length=100, blank=True)
    valor = models.CharField(max_length=500, blank=True)
    mensaje = models.TextField()
    
    class Meta:
        verbose_name = 'Error de Importación'
        verbose_name_plural = 'Errores de Importación'
        ordering = ['fila']
    
    def __str__(self):
        return f"Fila {self.fila}: {self.mensaje[:50]}"
