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

application = get_wsgi_application()

tmp_db = Path("/tmp/db.sqlite3")
if os.environ.get("VERCEL"):
    if not tmp_db.exists() or tmp_db.stat().st_size == 0:
        try:
            from django.core.management import call_command
            call_command("migrate", interactive=False)
        except Exception as e:
            print(f"Failed auto-migration on Vercel /tmp/db.sqlite3: {e}")

app = application
