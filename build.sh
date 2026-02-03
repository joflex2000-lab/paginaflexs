#!/usr/bin/env bash
# Build script for Railway
# Only tasks that don't need database connection

set -o errexit  # Exit on error

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Collect static files (doesn't need database)
python manage.py collectstatic --no-input

echo "Build completed successfully!"
