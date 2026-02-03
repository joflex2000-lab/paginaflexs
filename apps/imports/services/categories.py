"""
Category Importer - Importador de categorías desde Excel/CSV.
"""
from apps.catalog.models import Categoria
from .base import BaseImporter


class CategoryImporter(BaseImporter):
    """Importador de categorías."""
    
    TIPO = 'categorias'
    COLUMNAS_REQUERIDAS = ['Nombre']
    COLUMNAS_OPCIONALES = []
    
    def procesar_fila(self, fila, dry_run=False):
        """Procesa una fila de categoría."""
        nombre = self.get_valor(fila, 'Nombre', '').strip()
        if not nombre:
            raise ValueError("Nombre es requerido")
        
        # Verificar si existe
        existe = Categoria.objects.filter(nombre__iexact=nombre, padre__isnull=True).exists()
        
        if existe:
            accion = 'saltar'  # No duplicar
        else:
            accion = 'crear'
        
        if dry_run:
            return (accion, None)
        
        # Ejecutar
        if existe:
            categoria = Categoria.objects.get(nombre__iexact=nombre, padre__isnull=True)
        else:
            categoria = Categoria.objects.create(
                nombre=nombre,
                activa=True
            )
        
        return (accion, categoria)
