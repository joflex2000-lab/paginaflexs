from django.contrib.auth.models import AbstractUser
from django.db import models


class Usuario(AbstractUser):
    """
    Usuario personalizado con rol (admin o cliente).
    Extiende el modelo de usuario de Django.
    """
    
    class Rol(models.TextChoices):
        ADMIN = 'admin', 'Administrador'
        CLIENTE = 'cliente', 'Cliente'
    
    rol = models.CharField(
        max_length=10,
        choices=Rol.choices,
        default=Rol.CLIENTE,
        verbose_name='Rol'
    )
    
    class Meta:
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'
    
    def __str__(self):
        return f"{self.username} ({self.get_rol_display()})"
    
    @property
    def es_admin(self):
        return self.rol == self.Rol.ADMIN or self.is_superuser
    
    @property
    def es_cliente(self):
        return self.rol == self.Rol.CLIENTE


class Cliente(models.Model):
    """
    Perfil extendido del cliente con datos comerciales.
    """
    
    class CondicionIVA(models.TextChoices):
        RESPONSABLE_INSCRIPTO = 'RI', 'Responsable Inscripto'
        MONOTRIBUTISTA = 'MO', 'Monotributista'
        EXENTO = 'EX', 'Exento'
        CONSUMIDOR_FINAL = 'CF', 'Consumidor Final'
    
    usuario = models.OneToOneField(
        Usuario,
        on_delete=models.CASCADE,
        related_name='cliente',
        verbose_name='Usuario'
    )
    nombre = models.CharField(max_length=200, verbose_name='Nombre/Razón Social')
    contacto = models.CharField(max_length=200, blank=True, verbose_name='Contacto')
    tipo_cliente = models.CharField(max_length=100, blank=True, verbose_name='Tipo de Cliente')
    provincia = models.CharField(max_length=100, blank=True, verbose_name='Provincia')
    domicilio = models.CharField(max_length=300, blank=True, verbose_name='Domicilio')
    telefonos = models.CharField(max_length=200, blank=True, verbose_name='Teléfonos')
    cuit_dni = models.CharField(max_length=20, blank=True, verbose_name='CUIT/DNI')
    descuento = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        verbose_name='Descuento (%)',
        help_text='Porcentaje de descuento aplicado a todos los productos'
    )
    condicion_iva = models.CharField(
        max_length=2,
        choices=CondicionIVA.choices,
        default=CondicionIVA.CONSUMIDOR_FINAL,
        verbose_name='Condición IVA'
    )
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de creación')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Última actualización')
    
    class Meta:
        verbose_name = 'Cliente'
        verbose_name_plural = 'Clientes'
        ordering = ['nombre']
    
    def __str__(self):
        return self.nombre
