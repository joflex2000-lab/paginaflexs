#!/usr/bin/env bash
# Startup script for Railway
# Runs migrations and creates superuser before starting the server

set -o errexit

echo "Running migrations..."
python manage.py migrate --no-input

echo "Creating superuser if needed..."
python manage.py shell << EOF
from django.contrib.auth import get_user_model
import os

User = get_user_model()
username = os.environ.get('DJANGO_SUPERUSER_USERNAME', 'admin')
email = os.environ.get('DJANGO_SUPERUSER_EMAIL', 'admin@example.com')
password = os.environ.get('DJANGO_SUPERUSER_PASSWORD', 'changeme123')

if not User.objects.filter(username=username).exists():
    User.objects.create_superuser(username=username, email=email, password=password)
    print(f'Superuser {username} created successfully')
else:
    print(f'Superuser {username} already exists')
EOF

echo "Importing initial data..."
# Import clients if file exists and database is empty
if [ -f "data/clientes.xlsx" ]; then
    echo "Importing clients from data/clientes.xlsx..."
    python manage.py import_clientes data/clientes.xlsx --skip-if-exists
else
    echo "No client data file found (data/clientes.xlsx)"
fi

# Import products if file exists and database is empty
if [ -f "data/productos.xlsx" ]; then
    echo "Importing products from data/productos.xlsx..."
    python manage.py import_productos data/productos.xlsx --skip-if-exists
else
    echo "No product data file found (data/productos.xlsx)"
fi

echo "Starting Gunicorn..."
gunicorn paginaflexs.wsgi:application
