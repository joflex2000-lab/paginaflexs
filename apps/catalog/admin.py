from django.contrib import admin
from .models import Categoria, ConfiguracionFiltro, Producto, DefinicionAtributo, ProductoAtributo


class ConfiguracionFiltroInline(admin.TabularInline):
    model = ConfiguracionFiltro
    extra = 1


class DefinicionAtributoInline(admin.TabularInline):
    model = DefinicionAtributo
    extra = 1
    ordering = ('orden',)


class ProductoAtributoInline(admin.TabularInline):
    model = ProductoAtributo
    extra = 1
    autocomplete_fields = ['definicion']


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'padre', 'orden', 'activa')
    list_filter = ('activa', 'padre')
    search_fields = ('nombre',)
    inlines = [DefinicionAtributoInline, ConfiguracionFiltroInline]


@admin.register(DefinicionAtributo)
class DefinicionAtributoAdmin(admin.ModelAdmin):
    list_display = ('etiqueta', 'nombre', 'categoria', 'tipo', 'orden', 'activo')
    list_filter = ('categoria', 'tipo', 'activo')
    search_fields = ('nombre', 'etiqueta', 'categoria__nombre')
    list_editable = ('orden', 'activo')
    ordering = ('categoria', 'orden')


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ('sku', 'nombre', 'precio', 'stock', 'activo')
    list_filter = ('activo', 'categorias')
    search_fields = ('sku', 'nombre')
    filter_horizontal = ('categorias',)
    list_per_page = 50
    inlines = [ProductoAtributoInline]
