
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'paginaflexs.settings')
django.setup()

from apps.catalog.models import DefinicionAtributo, Categoria

def reorder_attributes():
    try:
        categoria = Categoria.objects.get(nombre='ABRAZADERAS')
        print(f"Found category: {categoria.nombre}")
        
        # New Plan: Grouped Levels
        # 1. Tipo
        # 2. Medida
        # 3. Detalles (Ancho, Largo, Forma) -> Displayed together
        # 4. Material -> Last step
        
        updates = {
            'tipo_fabricacion': 1,
            'medida_pulgadas': 2,
            'ancho': 3,
            'largo': 3,
            'forma': 3,
            'material': 4,
            # Move others to end to prevent blocking
            'linea': 99,
            'terminacion': 99,
            'marca': 99
        }
        
        for name, order in updates.items():
            try:
                defn = DefinicionAtributo.objects.get(categoria=categoria, nombre=name)
                defn.orden = order
                defn.save()
                print(f"Updated {name} -> order {order}")
            except DefinicionAtributo.DoesNotExist:
                print(f"Attribute {name} not found, skipping.")
                
        print("Reorder complete.")
        
    except Categoria.DoesNotExist:
        print("Category 'Abrazaderas' not found.")

if __name__ == '__main__':
    reorder_attributes()
