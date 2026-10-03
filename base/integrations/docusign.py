"""DocuSign eSignature OAuth + embedded-signing helpers.

Single-tenant (admin connects one DocuSign account). Credentials come from env:
    DOCUSIGN_CLIENT_ID, DOCUSIGN_SECRET, DOCUSIGN_ACCOUNT_ID,
    DOCUSIGN_OAUTH_BASE (default demo), DOCUSIGN_REDIRECT_URI.

OAuth tokens + the per-account REST base_uri are stored in
``base.models_integrations.DocusignAccount``.

Provider-agnostic interface (mirrors adobesign.py): is_configured,
build_authorize_url, make_state, exchange_code, fetch_userinfo,
refresh_access_token, access_token_for, create_envelope, embedded_sign_url,
download_signed_pdf.
"""

import base64
import logging
import os
import secrets
from datetime import timedelta
from urllib.parse import urlencode

import requests
from django.conf import settings
from django.utils import timezone

logger = logging.getLogger(__name__)

SCOPES = "signature extended"


def _conf(name, default=""):
    return getattr(settings, name, None) or os.environ.get(name, default)


def client_id():
    return _conf("DOCUSIGN_CLIENT_ID")


def client_secret():
    return _conf("DOCUSIGN_SECRET")


def oauth_base():
    return _conf("DOCUSIGN_OAUTH_BASE", "https://account-d.docusign.com").rstrip("/")


def redirect_uri():
    return _conf("DOCUSIGN_REDIRECT_URI", "http://127.0.0.1:8000/integrations/docusign/callback/")


def is_configured() -> bool:
    return bool(client_id() and client_secret())


def make_state() -> str:
    return secrets.token_urlsafe(24)


def build_authorize_url(state: str) -> str:
    params = {
        "response_type": "code",
        "scope": SCOPES,
        "client_id": client_id(),
        "redirect_uri": redirect_uri(),
        "state": state,
    }
    return f"{oauth_base()}/oauth/auth?{urlencode(params)}"


def _basic_auth_header():
    raw = f"{client_id()}:{client_secret()}".encode("ascii")
    return {"Authorization": "Basic " + base64.b64encode(raw).decode("ascii")}


def exchange_code(code: str) -> dict:
    resp = requests.post(
        f"{oauth_base()}/oauth/token",
        headers=_basic_auth_header(),
        data={"grant_type": "authorization_code", "code": code},
        timeout=20,
    )
    resp.raise_for_status()
    return resp.json()


def refresh_access_token(refresh_token: str) -> dict:
    resp = requests.post(
        f"{oauth_base()}/oauth/token",
        headers=_basic_auth_header(),
        data={"grant_type": "refresh_token", "refresh_token": refresh_token},
        timeout=20,
    )
    resp.raise_for_status()
    return resp.json()


def fetch_userinfo(access_token: str) -> dict:
    """Return the default account's {account_id, base_uri, email, name}."""
    resp = requests.get(
        f"{oauth_base()}/oauth/userinfo",
        headers={"Authorization": f"Bearer {access_token}"},
        timeout=20,
    )
    resp.raise_for_status()
    data = resp.json()
    accounts = data.get("accounts", []) or []
    default = next((a for a in accounts if a.get("is_default")), accounts[0] if accounts else {})
    return {
        "account_id": default.get("account_id", ""),
        "base_uri": default.get("base_uri", ""),
        "email": data.get("email", ""),
        "name": data.get("name", ""),
        "sub": data.get("sub", ""),
    }


def access_token_for(acct) -> str:
    """Return a valid access token for a DocusignAccount, refreshing if needed."""
    now = timezone.now()
    if acct.access_token and acct.token_expires_at and acct.token_expires_at > now + timedelta(seconds=60):
        return acct.access_token
    if not acct.refresh_token:
        raise RuntimeError("DocuSign not connected (no refresh token); reconnect required.")
    data = refresh_access_token(acct.refresh_token)
    acct.access_token = data["access_token"]
    if data.get("refresh_token"):
        acct.refresh_token = data["refresh_token"]
    if data.get("expires_in"):
        acct.token_expires_at = now + timedelta(seconds=int(data["expires_in"]))
    acct.save(update_fields=["access_token", "refresh_token", "token_expires_at", "updated_at"])
    return acct.access_token


def _rest_base(acct):
    base = (acct.base_uri or "").rstrip("/")
    return f"{base}/restapi/v2.1/accounts/{acct.account_id}"


def create_envelope(acct, pdf_bytes: bytes, signer_email: str, signer_name: str, client_user_id: str) -> str:
    """Create a sent envelope with one embedded (captive) signer. Returns envelopeId."""
    token = access_token_for(acct)
    doc_b64 = base64.b64encode(pdf_bytes).decode("ascii")
    payload = {
        "emailSubject": "Please sign this document",
        "documents": [{
            "documentBase64": doc_b64,
            "name": "Document",
            "fileExtension": "pdf",
            "documentId": "1",
        }],
        "recipients": {
            "signers": [{
                "email": signer_email,
                "name": signer_name or signer_email,
                "recipientId": "1",
                "clientUserId": str(client_user_id),
                "tabs": {
                    # Anchor to the invisible "/sn1/" marker the PDF templates place
                    # at their signature line; if a document has no marker the signer
                    # gets free-form signing instead of a hard error.
                    "signHereTabs": [{
                        "anchorString": "/sn1/",
                        "anchorUnits": "pixels",
                        "anchorXOffset": "0",
                        "anchorYOffset": "-20",
                        "anchorIgnoreIfNotPresent": "true",
                    }]
                },
            }]
        },
        "status": "sent",
    }
    resp = requests.post(
        f"{_rest_base(acct)}/envelopes",
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
        json=payload,
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()["envelopeId"]


def embedded_sign_url(acct, envelope_id: str, signer_email: str, signer_name: str,
                      client_user_id: str, return_url: str) -> str:
    token = access_token_for(acct)
    payload = {
        "returnUrl": return_url,
        "authenticationMethod": "none",
        "email": signer_email,
        "userName": signer_name or signer_email,
        "clientUserId": str(client_user_id),
        "recipientId": "1",
    }
    resp = requests.post(
        f"{_rest_base(acct)}/envelopes/{envelope_id}/views/recipient",
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
        json=payload,
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()["url"]


def _user_guid(acct, token: str) -> str:
    """The connected user's DocuSign user id (userinfo `sub`)."""
    resp = requests.get(
        f"{oauth_base()}/oauth/userinfo",
        headers={"Authorization": f"Bearer {token}"},
        timeout=20,
    )
    resp.raise_for_status()
    return resp.json().get("sub", "")


def list_signatures(acct) -> list:
    """List the connected user's saved signatures in their DocuSign profile."""
    token = access_token_for(acct)
    uid = _user_guid(acct, token)
    resp = requests.get(
        f"{_rest_base(acct)}/users/{uid}/signatures",
        headers={"Authorization": f"Bearer {token}"},
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json().get("userSignatures", []) or []


def user_signature_image(acct, signature_id: str):
    """Return (bytes, content_type) of one saved signature from the user's profile."""
    token = access_token_for(acct)
    uid = _user_guid(acct, token)
    resp = requests.get(
        f"{_rest_base(acct)}/users/{uid}/signatures/{signature_id}/signature_image",
        headers={"Authorization": f"Bearer {token}"},
        params={"include_chrome": "false"},
        timeout=30,
    )
    resp.raise_for_status()
    return resp.content, resp.headers.get("Content-Type", "image/gif").split(";")[0].strip()


def download_signature_image(acct, envelope_id: str, recipient_id: str = "1"):
    """Return (bytes, content_type) of the recipient's adopted signature image
    from a completed envelope (the bare signature, not the signed page)."""
    token = access_token_for(acct)
    resp = requests.get(
        f"{_rest_base(acct)}/envelopes/{envelope_id}/recipients/{recipient_id}/signature_image",
        headers={"Authorization": f"Bearer {token}"},
        timeout=30,
    )
    resp.raise_for_status()
    return resp.content, resp.headers.get("Content-Type", "image/gif").split(";")[0].strip()


def download_signed_pdf(acct, envelope_id: str) -> bytes:
    token = access_token_for(acct)
    resp = requests.get(
        f"{_rest_base(acct)}/envelopes/{envelope_id}/documents/combined",
        headers={"Authorization": f"Bearer {token}"},
        timeout=30,
    )
    resp.raise_for_status()
    return resp.content
