#!/usr/bin/env bash
# Startup script for Render/Railway
# Runs migrations and creates superuser before starting the server
# NOTE: Data import is done manually via panel due to Render timeout limits

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

echo "Starting Gunicorn..."
gunicorn paginaflexs.wsgi:application
