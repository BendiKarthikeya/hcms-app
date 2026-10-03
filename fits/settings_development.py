from .settings import *

DEBUG = True

# Enable query logging to see slow queries
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "INFO",
    },
    "loggers": {
        "django.db.backends": {
            "handlers": ["console"],
            "level": "DEBUG",  # Log all SQL queries
            "propagate": False,
        },
    },
}

# Use in-memory cache in development
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "fits-dev-cache",
        "TIMEOUT": 300,
        "OPTIONS": {"MAX_ENTRIES": 10000},
    }
}

# Email (Brevo SMTP) — loaded from .env
import os
EMAIL_BACKEND = "base.backends.ConfiguredEmailBackend"
EMAIL_HOST = os.environ.get("EMAIL_HOST", "smtp-relay.brevo.com")
EMAIL_PORT = int(os.environ.get("EMAIL_PORT", 587))
EMAIL_HOST_USER = os.environ.get("EMAIL_HOST_USER", "")
EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_HOST_PASSWORD", "")
EMAIL_USE_TLS = os.environ.get("EMAIL_USE_TLS", "True") == "True"
DEFAULT_FROM_EMAIL = os.environ.get("DEFAULT_FROM_EMAIL", "contractor1@fits.one")

# Recipient for "Send to Visa Department" onboarding hand-off + portal link base URL
VISA_TEAM_EMAIL = os.environ.get("VISA_TEAM_EMAIL", "")
SITE_URL = os.environ.get("SITE_URL", "https://hcmspro.net")

# Gmail OAuth (Profile -> Integrations -> Connect Gmail)
GMAIL_CLIENT_ID = os.environ.get("GMAIL_CLIENT_ID", "")
GMAIL_CLIENT_SECRET = os.environ.get("GMAIL_CLIENT_SECRET", "")
GMAIL_REDIRECT_URI = os.environ.get(
    "GMAIL_REDIRECT_URI",
    "http://127.0.0.1:8000/integrations/gmail/callback/",
)

# DocuSign eSignature OAuth (Integrations -> Connect DocuSign). Sandbox defaults.
DOCUSIGN_CLIENT_ID = os.environ.get("DOCUSIGN_CLIENT_ID", "")
DOCUSIGN_SECRET = os.environ.get("DOCUSIGN_SECRET", "")
DOCUSIGN_ACCOUNT_ID = os.environ.get("DOCUSIGN_ACCOUNT_ID", "")
DOCUSIGN_OAUTH_BASE = os.environ.get("DOCUSIGN_OAUTH_BASE", "https://account-d.docusign.com")
DOCUSIGN_REDIRECT_URI = os.environ.get(
    "DOCUSIGN_REDIRECT_URI",
    "http://127.0.0.1:8000/integrations/docusign/callback/",
)

# Adobe Acrobat Sign OAuth (Integrations -> Connect Adobe eSign).
# ADOBE_SIGN_OAUTH_BASE is the data-center login host (e.g. https://secure.na1.adobesign.com).
ADOBE_SIGN_CLIENT_ID = os.environ.get("ADOBE_SIGN_CLIENT_ID", "")
ADOBE_SIGN_SECRET = os.environ.get("ADOBE_SIGN_SECRET", "")
ADOBE_SIGN_OAUTH_BASE = os.environ.get("ADOBE_SIGN_OAUTH_BASE", "https://secure.na1.adobesign.com")
ADOBE_SIGN_REDIRECT_URI = os.environ.get(
    "ADOBE_SIGN_REDIRECT_URI",
    "http://127.0.0.1:8000/integrations/adobesign/callback/",
)

# HTTP in dev — allow session cookie over non-HTTPS
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
