"""
WSGI config for FITS HCMS project.

It exposes the WSGI callable as a module-level variable named ``application``.
"""

import os
import sqlite3
import threading
from pathlib import Path
from fits.settings_selector import resolve_settings_module

os.environ["VERCEL"] = "1"
os.environ.setdefault("DJANGO_SETTINGS_MODULE", resolve_settings_module())

import django

django.setup()

BASE_DIR = Path(__file__).resolve().parent.parent
tmp_db = Path("/tmp/db.sqlite3")
seed_db = BASE_DIR / "seed_db.sqlite3"

if os.environ.get("VERCEL"):
    if not tmp_db.exists() or tmp_db.stat().st_size == 0:
        try:
            tmp_db.parent.mkdir(parents=True, exist_ok=True)
            if seed_db.exists():
                shutil.copyfile(seed_db, tmp_db)
        except Exception as e:
            print(f"Error copying seed_db to /tmp: {e}")

import django

django.setup()

from django.core.wsgi import get_wsgi_application

application = get_wsgi_application()
app = application
