import os


SETTINGS_BY_ENV = {
    "development": "fits.settings_development",
    "staging": "fits.settings_staging",
    "production": "fits.settings_production",
    "test": "tests.test_settings",
}


def resolve_settings_module(default="fits.settings"):
    explicit_module = os.environ.get("DJANGO_SETTINGS_MODULE")
    if explicit_module:
        return explicit_module

    environment = os.environ.get("DJANGO_ENV", "development").strip().lower()
    return SETTINGS_BY_ENV.get(environment, default)
