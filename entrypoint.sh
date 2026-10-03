#!/bin/bash
set -e

echo "Running database migrations..."
python3 manage.py migrate --noinput --fake-initial

echo "Starting gunicorn on port ${PORT:-8080}..."
exec gunicorn --bind 0.0.0.0:${PORT:-8080} --workers 1 --timeout 120 fits.wsgi:application
