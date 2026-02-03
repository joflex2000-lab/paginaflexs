#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Fix template syntax errors in pedidos detalle.html"""

import re

file_path = r'c:\Users\Brian\Desktop\PAGINAFLEX\templates\panel\pedidos\detalle.html'

# Read file
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Fix all == operators without spaces
content = content.replace("pedido.estado=='pendiente'", "pedido.estado == 'pendiente'")
content = content.replace("pedido.estado=='confirmado'", "pedido.estado == 'confirmado'")
content = content.replace("pedido.estado=='en_proceso'", "pedido.estado == 'en_proceso'")
content = content.replace("pedido.estado=='enviado'", "pedido.estado == 'enviado'")
content = content.replace("pedido.estado=='entregado'", "pedido.estado == 'entregado'")
content = content.replace("pedido.estado=='cancelado'", "pedido.estado == 'cancelado'")

# Fix total price display (join broken lines)
content = re.sub(
    r'\$\{\{\s*\r?\n\s*pedido\.total\|floatformat:2\s*\}\}',
    '${{ pedido.total|floatformat:2 }}',
    content
)

# Write back
with open(file_path, 'w', encoding='utf-8', newline='') as f:
    f.write(content)

print("✅ Template fixed successfully!")
print("Fixed items:")
print("  - All pedido.estado == comparisons (added spaces)")
print("  - Total price display (joined into one line)")
