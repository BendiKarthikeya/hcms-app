"""Gmail OAuth2 + send-via-API helpers.

Single-tenant: credentials come from env vars
    GMAIL_CLIENT_ID, GMAIL_CLIENT_SECRET, GMAIL_REDIRECT_URI.

Per-user OAuth tokens are stored in MailboxIntegration.
"""

import base64
import json
import logging
import os
import secrets
from datetime import datetime, timedelta
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from urllib.parse import urlencode

import requests
from django.conf import settings
from django.utils import timezone

logger = logging.getLogger(__name__)

AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
TOKEN_URL = "https://oauth2.googleapis.com/token"
USERINFO_URL = "https://www.googleapis.com/oauth2/v2/userinfo"
SEND_URL = "https://gmail.googleapis.com/gmail/v1/users/me/messages/send"
REVOKE_URL = "https://oauth2.googleapis.com/revoke"
SCOPES = "https://www.googleapis.com/auth/gmail.send https://www.googleapis.com/auth/userinfo.email https://www.googleapis.com/auth/userinfo.profile"


def _conf(name, default=""):
    return getattr(settings, name, os.environ.get(name, default))


def client_id():
    return _conf("GMAIL_CLIENT_ID")


def client_secret():
    return _conf("GMAIL_CLIENT_SECRET")


def redirect_uri():
    return _conf("GMAIL_REDIRECT_URI", "https://hcmspro.net/integrations/gmail/callback/")


def is_configured() -> bool:
    return bool(client_id() and client_secret())


def build_authorize_url(state: str, redirect_uri_override: str = "") -> str:
    params = {
        "client_id": client_id(),
        "response_type": "code",
        "redirect_uri": redirect_uri_override or redirect_uri(),
        "scope": SCOPES,
        "access_type": "offline",
        "prompt": "consent",
        "include_granted_scopes": "true",
        "state": state,
    }
    return f"{AUTH_URL}?{urlencode(params)}"


def make_state() -> str:
    return secrets.token_urlsafe(24)


def exchange_code(code: str, redirect_uri_override: str = "") -> dict:
    """Exchange auth code for tokens. Raises on failure."""
    resp = requests.post(
        TOKEN_URL,
        data={
            "grant_type": "authorization_code",
            "code": code,
            "client_id": client_id(),
            "client_secret": client_secret(),
            "redirect_uri": redirect_uri_override or redirect_uri(),
        },
        timeout=15,
    )
    resp.raise_for_status()
    return resp.json()


def fetch_userinfo(access_token: str) -> dict:
    resp = requests.get(
        USERINFO_URL,
        headers={"Authorization": f"Bearer {access_token}"},
        timeout=15,
    )
    resp.raise_for_status()
    return resp.json()


def refresh_access_token(refresh_token: str) -> dict:
    resp = requests.post(
        TOKEN_URL,
        data={
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
            "client_id": client_id(),
            "client_secret": client_secret(),
        },
        timeout=15,
    )
    resp.raise_for_status()
    return resp.json()


def revoke_token(token: str) -> bool:
    try:
        r = requests.post(REVOKE_URL, params={"token": token}, timeout=10)
        return r.ok
    except Exception:
        return False


def _b64url(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode("ascii").rstrip("=")


def _build_mime(from_addr: str, from_name: str, to: str, subject: str, html: str, text: str = "") -> bytes:
    msg = MIMEMultipart("alternative")
    msg["From"] = f'"{from_name}" <{from_addr}>' if from_name else from_addr
    msg["To"] = to
    msg["Subject"] = subject
    if not text:
        text = "This message contains HTML content."
    msg.attach(MIMEText(text, "plain", "utf-8"))
    msg.attach(MIMEText(html or text, "html", "utf-8"))
    return msg.as_bytes()


def _ensure_fresh_token(integration) -> str:
    """Return a valid access token, refreshing if expired/expiring soon."""
    now = timezone.now()
    if integration.access_token and integration.token_expires_at and integration.token_expires_at > now + timedelta(seconds=60):
        return integration.access_token
    if not integration.refresh_token:
        raise RuntimeError("No refresh_token stored; user must reconnect Gmail.")
    data = refresh_access_token(integration.refresh_token)
    integration.access_token = data["access_token"]
    if data.get("expires_in"):
        integration.token_expires_at = now + timedelta(seconds=int(data["expires_in"]))
    integration.save(update_fields=["access_token", "token_expires_at", "updated_at"])
    return integration.access_token


def send_via_gmail(integration, *, to: str, subject: str, html: str, text: str = "", from_name: str = "") -> bool:
    """Send an email through the user's connected Gmail. Returns True on success."""
    if not integration or not integration.is_active:
        return False
    try:
        access = _ensure_fresh_token(integration)
        mime = _build_mime(
            from_addr=integration.email_address,
            from_name=from_name or integration.display_name or integration.email_address,
            to=to,
            subject=subject,
            html=html,
            text=text,
        )
        body = {"raw": _b64url(mime)}
        resp = requests.post(
            SEND_URL,
            headers={"Authorization": f"Bearer {access}", "Content-Type": "application/json"},
            data=json.dumps(body),
            timeout=20,
        )
        if resp.status_code == 401:
            # token went stale mid-flight; refresh once and retry
            data = refresh_access_token(integration.refresh_token)
            integration.access_token = data["access_token"]
            if data.get("expires_in"):
                integration.token_expires_at = timezone.now() + timedelta(seconds=int(data["expires_in"]))
            integration.save(update_fields=["access_token", "token_expires_at", "updated_at"])
            resp = requests.post(
                SEND_URL,
                headers={"Authorization": f"Bearer {integration.access_token}", "Content-Type": "application/json"},
                data=json.dumps(body),
                timeout=20,
            )
        resp.raise_for_status()
        integration.last_used_at = timezone.now()
        integration.last_error = ""
        integration.save(update_fields=["last_used_at", "last_error", "updated_at"])
        return True
    except Exception as exc:
        logger.exception("Gmail send failed for user=%s", integration.user_id)
        integration.last_error = str(exc)[:500]
        integration.save(update_fields=["last_error", "updated_at"])
        return False


def get_active_gmail(user):
    from base.models_integrations import MailboxIntegration

    return MailboxIntegration.objects.filter(user=user, provider="gmail", is_active=True).first()
