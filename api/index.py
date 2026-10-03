import os
import sys
import traceback
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

os.environ["VERCEL"] = "1"

try:
    from fits.wsgi import application
    _app = application
except Exception as e:
    _startup_error = traceback.format_exc()
    _app = None

def handler(environ, start_response):
    if _app is None:
        start_response("500 Internal Server Error", [("Content-Type", "text/plain")])
        return [f"STARTUP ERROR:\n{_startup_error}".encode("utf-8")]
    try:
        return _app(environ, start_response)
    except Exception as e:
        err = traceback.format_exc()
        start_response("500 Internal Server Error", [("Content-Type", "text/plain")])
        return [f"RUNTIME ERROR:\n{err}".encode("utf-8")]

app = handler
