from django.contrib import admin
from .models import Pedido, ItemPedido


class ItemPedidoInline(admin.TabularInline):
    model = ItemPedido
    extra = 0
    readonly_fields = ('subtotal',)


@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = ('id', 'cliente', 'estado', 'total', 'created_at')
    list_filter = ('estado', 'created_at')
    search_fields = ('cliente__nombre', 'id')
    inlines = [ItemPedidoInline]
    readonly_fields = ('subtotal', 'total', 'created_at', 'updated_at')
    date_hierarchy = 'created_at'
