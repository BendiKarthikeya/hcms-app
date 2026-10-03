import os
import sys
from pathlib import Path

# Add project root directory to python path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from fits.wsgi import application

app = application
