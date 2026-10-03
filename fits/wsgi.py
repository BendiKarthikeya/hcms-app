"""
WSGI config for FITS HCMS project.

It exposes the WSGI callable as a module-level variable named ``application``.
"""

import os
import sqlite3
from pathlib import Path
from fits.settings_selector import resolve_settings_module

os.environ["VERCEL"] = "1"
os.environ.setdefault("DJANGO_SETTINGS_MODULE", resolve_settings_module())

tmp_db = Path("/tmp/db.sqlite3")


def needs_migration(path):
    try:
        if not path.exists():
            return True
        with sqlite3.connect(str(path)) as conn:
            cur = conn.cursor()
            cur.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='base_company';"
            )
            return cur.fetchone() is None
    except Exception:
        return True


if os.environ.get("VERCEL"):
    try:
        tmp_db.parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(str(tmp_db)) as conn:
            conn.execute("PRAGMA journal_mode = OFF;")
            conn.execute("PRAGMA synchronous = OFF;")
    except Exception as e:
        print(f"Error initializing /tmp/db.sqlite3: {e}")

import django

django.setup()

if os.environ.get("VERCEL"):
    if needs_migration(tmp_db):
        try:
            from django.core.management import call_command

            call_command("migrate", interactive=False, verbosity=0)
        except Exception as e:
            print(f"Auto-migration error on /tmp/db.sqlite3: {e}")

from django.core.wsgi import get_wsgi_application

application = get_wsgi_application()
app = application
