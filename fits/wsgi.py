import os
import sqlite3
from pathlib import Path
from django.core.wsgi import get_wsgi_application

BASE_DIR = Path(__file__).resolve().parent.parent

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "fits.settings")

_db_initialized = False


def is_db_ready():
    global _db_initialized
    if _db_initialized:
        return True
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
    _db_initialized = True
    return True


_django_app = get_wsgi_application()


def application(environ, start_response):
    try:
        is_db_ready()
    except Exception as e:
        print("Lazy DB init exception:", e)
    return _django_app(environ, start_response)


app = application
