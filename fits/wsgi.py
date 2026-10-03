import os
import sqlite3
from pathlib import Path
from django.core.wsgi import get_wsgi_application
from django.core.management import call_command

BASE_DIR = Path(__file__).resolve().parent.parent

if os.environ.get("VERCEL"):
    db_file = Path("/tmp/db.sqlite3")
    seed_file = BASE_DIR / "seed_schema.sql"
    if not db_file.exists() and seed_file.exists():
        try:
            conn = sqlite3.connect(str(db_file))
            with open(seed_file, "r", encoding="utf-8") as f:
                conn.executescript(f.read())
            conn.close()
        except Exception as e:
            print("Vercel DB seed error:", e)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "fits.settings")

application = get_wsgi_application()

if os.environ.get("VERCEL"):
    try:
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1 FROM base_company LIMIT 1")
    except Exception:
        try:
            call_command("migrate", interactive=False)
        except Exception as e:
            print("Auto-migration fallback error:", e)

app = application
