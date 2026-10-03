"""
init.py
"""

import importlib.util

from fits import (
    fits_apps,
    fits_context_processors,
    fits_middlewares,
    fits_settings,
)

if all(
    importlib.util.find_spec(module_name) is not None
    for module_name in ("rest_framework", "rest_framework_simplejwt", "drf_yasg")
):
    from fits import rest_conf  # noqa: F401
