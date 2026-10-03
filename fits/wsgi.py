"""
WSGI config for FITS HCMS project.

It exposes the WSGI callable as a module-level variable named ``application``.
"""

import os
import shutil
from pathlib import Path
from django.core.wsgi import get_wsgi_application
from fits.settings_selector import resolve_settings_module

os.environ["VERCEL"] = "1"
os.environ.setdefault("DJANGO_SETTINGS_MODULE", resolve_settings_module())

tmp_db = Path("/tmp/db.sqlite3")
if os.environ.get("VERCEL"):
    try:
        tmp_db.parent.mkdir(parents=True, exist_ok=True)
        if not tmp_db.exists():
            tmp_db.touch()
    except Exception as e:
        print(f"Error touching /tmp/db.sqlite3: {e}")

import django
django.setup()

if os.environ.get("VERCEL"):
    try:
        if tmp_db.exists() and tmp_db.stat().st_size == 0:
            from django.db import connection
            with connection.cursor() as cursor:
                cursor.execute("PRAGMA journal_mode = OFF;")
                cursor.execute("PRAGMA synchronous = OFF;")
            from django.core.management import call_command
            call_command("migrate", interactive=False, verbosity=0)
    except Exception as e:
        print(f"Auto-migration error on /tmp/db.sqlite3: {e}")

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
app = application
