"""
Client Importer - Importador de clientes desde Excel/CSV.
"""
import re
from django.contrib.auth.hashers import make_password
from apps.accounts.models import Usuario, Cliente
from .base import BaseImporter


class ClientImporter(BaseImporter):
    """Importador de clientes."""
    
    TIPO = 'clientes'
    COLUMNAS_REQUERIDAS = ['Usuario', 'Nombre']
    COLUMNAS_OPCIONALES = [
        'Contraseña', 'Email', 'Contacto', 'Tipo de cliente',
        'Provincia', 'Domicilio', 'Telefonos', 'CUIT/DNI',
        'Descuento', 'Cond.IVA'
    ]
    
    def __init__(self, archivo, usuario=None, opciones=None):
        super().__init__(archivo, usuario, opciones)
        self.actualizar_passwords = opciones.get('actualizar_passwords', False) if opciones else False
    
    def procesar_fila(self, fila, dry_run=False):
        """Procesa una fila de cliente."""
        # Obtener valores
        username = self.get_valor(fila, 'Usuario', '').strip()
        if not username:
            raise ValueError("Usuario es requerido")
        
        nombre = self.get_valor(fila, 'Nombre', '').strip()
        if not nombre:
            raise ValueError("Nombre es requerido")
        
        password = self.get_valor(fila, 'Contraseña', '')
        email = self.get_valor(fila, 'Email', '').strip()
        contacto = self.get_valor(fila, 'Contacto', '')
        tipo_cliente = self.get_valor(fila, 'Tipo de cliente', '')
        provincia = self.get_valor(fila, 'Provincia', '')
        domicilio = self.get_valor(fila, 'Domicilio', '')
        telefonos = str(self.get_valor(fila, 'Telefonos', ''))
        cuit_dni = self.get_valor(fila, 'CUIT/DNI', '')
        condicion_iva = self.get_valor(fila, 'Cond.IVA', 'CF')
        
        # Normalizar descuento (10, 0.10, 10% -> 10.0)
        descuento_raw = self.get_valor(fila, 'Descuento', '0')
        descuento = self._normalizar_descuento(descuento_raw)
        
        # Validar email si viene
        if email and not self._validar_email(email):
            raise ValueError(f"Email inválido: {email}")
        
        # Normalizar condición IVA
        condicion_iva = self._normalizar_condicion_iva(condicion_iva)
        
        # Verificar si existe
        try:
            usuario_obj = Usuario.objects.get(username=username)
            accion = 'actualizar'
        except Usuario.DoesNotExist:
            usuario_obj = None
            accion = 'crear'
        
        if dry_run:
            return (accion, None)
        
        # Ejecutar
        if usuario_obj:
            # Update usuario
            if email:
                usuario_obj.email = email
            if self.actualizar_passwords and password:
                usuario_obj.password = make_password(password)
            usuario_obj.save()
            
            # Update o crear cliente
            try:
                cliente = usuario_obj.cliente
            except Cliente.DoesNotExist:
                cliente = Cliente(usuario=usuario_obj)
            
            cliente.nombre = nombre
            cliente.contacto = contacto
            cliente.tipo_cliente = tipo_cliente
            cliente.provincia = provincia
            cliente.domicilio = domicilio
            cliente.telefonos = telefonos
            cliente.cuit_dni = cuit_dni
            cliente.descuento = descuento
            cliente.condicion_iva = condicion_iva
            cliente.save()
        else:
            # Create usuario
            usuario_obj = Usuario.objects.create(
                username=username,
                email=email,
                password=make_password(password) if password else make_password(username),
                rol='cliente'
            )
            
            # Create cliente
            Cliente.objects.create(
                usuario=usuario_obj,
                nombre=nombre,
                contacto=contacto,
                tipo_cliente=tipo_cliente,
                provincia=provincia,
                domicilio=domicilio,
                telefonos=telefonos,
                cuit_dni=cuit_dni,
                descuento=descuento,
                condicion_iva=condicion_iva
            )
        
        return (accion, usuario_obj)
    
    def _normalizar_descuento(self, valor):
        """Normaliza el descuento a porcentaje (ej: 10 para 10%)."""
        if not valor or str(valor).strip() == '':
            return 0
        
        try:
            valor_str = str(valor).replace('%', '').replace(',', '.').strip()
            descuento = float(valor_str)
            
            # Si es menor a 1, asumir que está en formato decimal (0.10 = 10%)
            if 0 < descuento < 1:
                descuento = descuento * 100
            
            return min(max(descuento, 0), 100)  # Limitar entre 0 y 100
        except (ValueError, TypeError):
            return 0
    
    def _validar_email(self, email):
        """Valida formato de email."""
        patron = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(patron, email) is not None
    
    def _normalizar_condicion_iva(self, valor):
        """Normaliza la condición IVA a código."""
        if not valor:
            return 'CF'
        
        valor_upper = str(valor).upper().strip()
        
        if 'INSCRIPTO' in valor_upper or valor_upper == 'RI':
            return 'RI'
        elif 'MONOTRIBUTO' in valor_upper or valor_upper == 'MO':
            return 'MO'
        elif 'EXENTO' in valor_upper or valor_upper == 'EX':
            return 'EX'
        else:
            return 'CF'  # Default: Consumidor Final
