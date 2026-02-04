# Data Files Directory

This directory contains Excel/CSV files for automatic data import during deployment.

## Files to Place Here:

1. **clientes.xlsx** - Client data with columns:
   - Usuario (required)
   - Nombre (required)
   - Contraseña
   - Email
   - Contacto
   - Tipo de cliente
   - Provincia
   - Domicilio
   - Telefonos
   - CUIT/DNI
   - Descuento
   - Cond.IVA

2. **productos.xlsx** - Product data with columns:
   - SKU (required)
   - Nombre (required)
   - Precio (required)
   - Marca
   - Rubro
   - Subrubro
   - Descripción
   - Stock
   - Activo

3. **abrazaderas.xlsx** - Clamp products (parsed automatically):
   - Same columns as productos.xlsx
   - Parser extracts diameter, type, material from product name
   - Creates filterable attributes automatically

## Usage:

These files are automatically imported during deployment via `railway-start.sh`.

To import manually:
```bash
python manage.py import_clientes data/clientes.xlsx --skip-if-exists
python manage.py import_productos data/productos.xlsx --skip-if-exists
python manage.py import_productos data/abrazaderas.xlsx --skip-if-exists
```

The `--skip-if-exists` flag prevents re-importing if data already exists.
