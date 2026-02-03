
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'paginaflexs.settings')
django.setup()

from apps.catalog.models import Categoria, DefinicionAtributo

def list_categories():
    cats = Categoria.objects.all()
    print(f"Total categories: {cats.count()}")
    for c in cats:
        print(f"ID: {c.id} | Name: '{c.nombre}'")
        defins = DefinicionAtributo.objects.filter(categoria=c)
        if defins.exists():
            print("  Attributes:")
            for d in defins.order_by('orden'):
                print(f"    - {d.nombre} (Order: {d.orden})")

if __name__ == '__main__':
    list_categories()
