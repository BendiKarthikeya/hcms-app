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
schema_sql = BASE_DIR / "seed_schema.sql"

if os.environ.get("VERCEL"):
    if not tmp_db.exists() or tmp_db.stat().st_size == 0:
        try:
            tmp_db.parent.mkdir(parents=True, exist_ok=True)
            with sqlite3.connect(str(tmp_db)) as conn:
                conn.execute("PRAGMA journal_mode = OFF;")
                conn.execute("PRAGMA synchronous = OFF;")
                if schema_sql.exists():
                    conn.executescript(schema_sql.read_text(encoding="utf-8"))
        except Exception as e:
            print(f"Error seeding /tmp/db.sqlite3: {e}")

import django

django.setup()

from django.core.wsgi import get_wsgi_application

application = get_wsgi_application()
app = application
