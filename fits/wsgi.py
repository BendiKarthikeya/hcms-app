import os
import sqlite3
from pathlib import Path
from django.core.wsgi import get_wsgi_application

BASE_DIR = Path(__file__).resolve().parent.parent

if os.environ.get("VERCEL"):
    db_file = Path("/tmp/db.sqlite3")
    seed_file = BASE_DIR / "seed_schema.sql"
    if not db_file.exists() and seed_file.exists():
        try:
            conn = sqlite3.connect(str(db_file))
            with open(seed_file, "r", encoding="utf-8") as f:
                sql_script = f.read()
            conn.executescript(sql_script)
            conn.close()
        except Exception as e:
            print("Vercel DB seed error:", e)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "fits.settings")

application = get_wsgi_application()
app = application
