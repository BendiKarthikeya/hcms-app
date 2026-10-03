"""
WSGI config for FITS HCMS project.

It exposes the WSGI callable as a module-level variable named ``application``.
"""

import os
import shutil
from pathlib import Path
from django.core.wsgi import get_wsgi_application
from fits.settings_selector import resolve_settings_module

os.environ.setdefault("DJANGO_SETTINGS_MODULE", resolve_settings_module())

BASE_DIR = Path(__file__).resolve().parent.parent
tmp_db = Path("/tmp/db.sqlite3")
src_db = BASE_DIR / "db.sqlite3"

# On Vercel, ensure SQLite database exists in writable /tmp directory
if os.environ.get("VERCEL") and src_db.exists() and (not tmp_db.exists() or tmp_db.stat().st_size == 0):
    try:
        shutil.copyfile(src_db, tmp_db)
    except Exception as e:
        print(f"Failed to copy DB to /tmp: {e}")

application = get_wsgi_application()
app = application
