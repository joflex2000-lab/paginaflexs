from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Usuario, Cliente


@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    list_display = ('username', 'email', 'rol', 'is_active', 'date_joined')
    list_filter = ('rol', 'is_active', 'is_staff')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    
    fieldsets = UserAdmin.fieldsets + (
        ('Rol', {'fields': ('rol',)}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Rol', {'fields': ('rol',)}),
    )


@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'usuario', 'tipo_cliente', 'provincia', 'descuento', 'condicion_iva')
    list_filter = ('tipo_cliente', 'provincia', 'condicion_iva')
    search_fields = ('nombre', 'usuario__username', 'cuit_dni', 'telefonos')
    raw_id_fields = ('usuario',)
