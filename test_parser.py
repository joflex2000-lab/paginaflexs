
import os
import sys
import django

# Setup Django environment
sys.path.append('C:\\Users\\Brian\\Desktop\\PAGINAFLEX')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'paginaflexs.settings')
django.setup()

from apps.imports.parsers.abrazaderas import AbrazaderaParser

examples = [
    "ABRAZADERA TREFILADA DE 1/2 X 85 X 260 CURVA",
    "ABRAZADERA TREFILADA DE 5/8 X 100 X 300 PLANA",
    "ABRAZADERA LAMINADA DE 3/4 X 1 X 10 /S/CURVA",
    "ABRAZADERA SIMPLE DE 1/2" # Should trigger fallback
]

print("--- Testing AbrazaderaParser ---")
for text in examples:
    print(f"\nInput: '{text}'")
    result = AbrazaderaParser.parsear(text)
    print("Atributos:", result['atributos'])
    if result['warnings']:
        print("Warnings:", result['warnings'])
