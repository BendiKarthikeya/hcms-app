"""Adobe Acrobat Sign (REST v6) OAuth + embedded-signing helpers.

Single-tenant (admin connects one Adobe Sign account). Credentials from env:
    ADOBE_SIGN_CLIENT_ID, ADOBE_SIGN_SECRET,
    ADOBE_SIGN_OAUTH_BASE (data-center login host, e.g. https://secure.na1.adobesign.com),
    ADOBE_SIGN_REDIRECT_URI.

OAuth tokens + the per-account ``api_access_point`` are stored in
``base.models_integrations.AdobeSignAccount``.

Provider-agnostic interface (mirrors docusign.py): is_configured,
build_authorize_url, make_state, exchange_code, refresh_access_token,
access_token_for, create_envelope, embedded_sign_url, download_signed_pdf.
"""

import logging
import os
import secrets
from datetime import timedelta
from urllib.parse import urlencode

import requests
from django.conf import settings
from django.utils import timezone

logger = logging.getLogger(__name__)

# Acrobat Sign OAuth scopes (modifier defaults to 'self').
SCOPES = "agreement_write agreement_send agreement_read user_login"


def _conf(name, default=""):
    return getattr(settings, name, None) or os.environ.get(name, default)


def client_id():
    return _conf("ADOBE_SIGN_CLIENT_ID")


def client_secret():
    return _conf("ADOBE_SIGN_SECRET")


def oauth_base():
    return _conf("ADOBE_SIGN_OAUTH_BASE", "https://secure.na1.adobesign.com").rstrip("/")


def redirect_uri():
    return _conf("ADOBE_SIGN_REDIRECT_URI", "http://127.0.0.1:8000/integrations/adobesign/callback/")


def is_configured() -> bool:
    return bool(client_id() and client_secret())


def make_state() -> str:
    return secrets.token_urlsafe(24)


def build_authorize_url(state: str) -> str:
    params = {
        "response_type": "code",
        "client_id": client_id(),
        "redirect_uri": redirect_uri(),
        "scope": SCOPES,
        "state": state,
    }
    return f"{oauth_base()}/public/oauth/v2?{urlencode(params)}"


def exchange_code(code: str) -> dict:
    """Returns {access_token, refresh_token, api_access_point, expires_in, ...}."""
    resp = requests.post(
        f"{oauth_base()}/oauth/v2/token",
        data={
            "grant_type": "authorization_code",
            "code": code,
            "client_id": client_id(),
            "client_secret": client_secret(),
            "redirect_uri": redirect_uri(),
        },
        timeout=20,
    )
    resp.raise_for_status()
    return resp.json()


def refresh_access_token(refresh_token: str) -> dict:
    resp = requests.post(
        f"{oauth_base()}/oauth/v2/refresh",
        data={
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
            "client_id": client_id(),
            "client_secret": client_secret(),
        },
        timeout=20,
    )
    resp.raise_for_status()
    return resp.json()


def access_token_for(acct) -> str:
    now = timezone.now()
    if acct.access_token and acct.token_expires_at and acct.token_expires_at > now + timedelta(seconds=60):
        return acct.access_token
    if not acct.refresh_token:
        raise RuntimeError("Adobe Sign not connected (no refresh token); reconnect required.")
    data = refresh_access_token(acct.refresh_token)
    acct.access_token = data["access_token"]
    if data.get("expires_in"):
        acct.token_expires_at = now + timedelta(seconds=int(data["expires_in"]))
    acct.save(update_fields=["access_token", "token_expires_at", "updated_at"])
    return acct.access_token


def _api(acct):
    return (acct.api_access_point or "").rstrip("/")


def _upload_transient_document(acct, token: str, pdf_bytes: bytes) -> str:
    resp = requests.post(
        f"{_api(acct)}/api/rest/v6/transientDocuments",
        headers={"Authorization": f"Bearer {token}"},
        files={"File": ("document.pdf", pdf_bytes, "application/pdf")},
        data={"File-Name": "document.pdf", "Mime-Type": "application/pdf"},
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()["transientDocumentId"]


def create_envelope(acct, pdf_bytes: bytes, signer_email: str, signer_name: str,
                    client_user_id: str, return_url: str = "") -> str:
    """Create an in-process agreement with one signer. Returns the agreement id."""
    token = access_token_for(acct)
    transient_id = _upload_transient_document(acct, token, pdf_bytes)
    payload = {
        "fileInfos": [{"transientDocumentId": transient_id}],
        "name": "Please sign this document",
        "participantSetsInfo": [{
            "memberInfos": [{"email": signer_email}],
            "order": 1,
            "role": "SIGNER",
        }],
        "signatureType": "ESIGN",
        "state": "IN_PROCESS",
    }
    if return_url:
        payload["postSignOption"] = {"redirectDelay": 0, "redirectUrl": return_url}
    resp = requests.post(
        f"{_api(acct)}/api/rest/v6/agreements",
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
        json=payload,
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()["id"]


def embedded_sign_url(acct, agreement_id: str, signer_email: str = "", signer_name: str = "",
                      client_user_id: str = "", return_url: str = "") -> str:
    """Fetch the embedded e-sign URL for the agreement's current signer."""
    token = access_token_for(acct)
    resp = requests.get(
        f"{_api(acct)}/api/rest/v6/agreements/{agreement_id}/signingUrls",
        headers={"Authorization": f"Bearer {token}"},
        timeout=30,
    )
    resp.raise_for_status()
    sets = resp.json().get("signingUrlSetInfos", []) or []
    if sets and sets[0].get("signingUrls"):
        return sets[0]["signingUrls"][0]["esignUrl"]
    raise RuntimeError("Adobe Sign returned no signing URL for this agreement.")


def download_signed_pdf(acct, agreement_id: str) -> bytes:
    token = access_token_for(acct)
    resp = requests.get(
        f"{_api(acct)}/api/rest/v6/agreements/{agreement_id}/combinedDocument",
        headers={"Authorization": f"Bearer {token}"},
        timeout=30,
    )
    resp.raise_for_status()
    return resp.content
