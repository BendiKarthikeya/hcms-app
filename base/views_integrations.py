"""Profile -> Integrations views (Gmail OAuth, mailbox connect/disconnect)."""

import logging
from datetime import timedelta

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core import signing
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_http_methods

from base.integrations import gmail
from base.models_integrations import MailboxIntegration

logger = logging.getLogger(__name__)

_STATE_COOKIE = "gmail_oauth_state"
_STATE_MAX_AGE = 600  # 10 minutes

_UI_INTEGRATIONS = "/ui/integrations/"


def _callback_uri(request):
    """Build the redirect URI from the current request so it works on any domain."""
    return request.build_absolute_uri(reverse("integrations-gmail-callback"))


@login_required
def integrations_home(request):
    """Profile -> Integrations landing page."""
    gmail_integ = MailboxIntegration.objects.filter(provider="gmail", is_active=True).first()
    ctx = {
        "gmail": gmail_integ,
        "gmail_configured": gmail.is_configured(),
        "gmail_redirect_uri": _callback_uri(request),
    }
    return render(request, "base/integrations/integrations_home.html", ctx)


@login_required
def gmail_connect(request):
    """Start the Gmail OAuth flow."""
    if not request.user.is_superuser:
        messages.error(request, "Only administrators can connect a Gmail account.")
        return redirect("integrations-home")
    if not gmail.is_configured():
        messages.error(request, "Gmail integration is not configured. Contact your administrator (set GMAIL_CLIENT_ID / GMAIL_CLIENT_SECRET).")
        return redirect("integrations-home")
    state = gmail.make_state()
    callback_uri = _callback_uri(request)
    signed = signing.dumps(state)
    response = redirect(gmail.build_authorize_url(state, redirect_uri_override=callback_uri))
    is_secure = request.is_secure()
    response.set_cookie(
        _STATE_COOKIE, signed,
        max_age=_STATE_MAX_AGE, httponly=True,
        samesite="None" if is_secure else "Lax",
        secure=is_secure,
    )
    return response


@login_required
def gmail_callback(request):
    """OAuth redirect target. Exchanges code → tokens, persists, then back to integrations page."""
    err = request.GET.get("error")
    if err:
        messages.error(request, f"Gmail authorization failed: {err}")
        return redirect("integrations-home")

    state = request.GET.get("state")
    signed = request.COOKIES.get(_STATE_COOKIE)
    try:
        expected = signing.loads(signed, max_age=_STATE_MAX_AGE) if signed else None
    except (signing.BadSignature, signing.SignatureExpired):
        expected = None

    if not state or state != expected:
        messages.error(
            request,
            "OAuth state mismatch — your session may have expired. Please try connecting Gmail again.",
        )
        return redirect("integrations-home")

    code = request.GET.get("code")
    if not code:
        messages.error(request, "Gmail authorization did not return a code.")
        return redirect("integrations-home")

    callback_uri = _callback_uri(request)
    try:
        tokens = gmail.exchange_code(code, redirect_uri_override=callback_uri)
        access_token = tokens.get("access_token")
        refresh_token = tokens.get("refresh_token", "")
        expires_in = int(tokens.get("expires_in", 0) or 0)
        scope = tokens.get("scope", "")

        info = gmail.fetch_userinfo(access_token)
        email_address = info.get("email", "")
        display_name = info.get("name", "")

        integ, _ = MailboxIntegration.objects.update_or_create(
            user=request.user,
            provider="gmail",
            defaults={
                "email_address": email_address,
                "display_name": display_name,
                "access_token": access_token,
                # Don't overwrite an existing refresh_token with empty (Google omits it on re-consent)
                "refresh_token": refresh_token or MailboxIntegration.objects.filter(provider="gmail").values_list("refresh_token", flat=True).first() or "",
                "token_expires_at": timezone.now() + timedelta(seconds=expires_in) if expires_in else None,
                "scope": scope,
                "is_active": True,
                "last_error": "",
            },
        )
        messages.success(request, f"Connected Gmail account: {integ.email_address}")
    except Exception as exc:
        logger.exception("Gmail OAuth callback failed")
        messages.error(request, f"Failed to connect Gmail: {exc}")

    response = redirect("integrations-home")
    response.delete_cookie(_STATE_COOKIE)
    return response


@login_required
@require_http_methods(["POST"])
def gmail_disconnect(request):
    if not request.user.is_superuser:
        messages.error(request, "Only administrators can disconnect a Gmail account.")
        return redirect("integrations-home")
    integ = MailboxIntegration.objects.filter(provider="gmail").first()
    if integ:
        if integ.refresh_token:
            gmail.revoke_token(integ.refresh_token)
        integ.delete()
        messages.success(request, "Gmail account disconnected.")
    return redirect("integrations-home")


@login_required
@require_http_methods(["POST"])
def gmail_send_test(request):
    integ = MailboxIntegration.objects.filter(user=request.user, provider="gmail", is_active=True).first()
    if not integ:
        messages.error(request, "No active Gmail integration to test.")
        return redirect("integrations-home")
    to = request.POST.get("to") or integ.email_address
    ok = gmail.send_via_gmail(
        integ,
        to=to,
        subject="FITS HCMS – Gmail integration test",
        html="<p>This is a test email from FITS HCMS.</p><p>If you can read this, your Gmail integration is working.</p>",
        text="This is a test email from FITS HCMS. Your Gmail integration is working.",
    )
    if ok:
        messages.success(request, f"Test email sent to {to}.")
    else:
        messages.error(request, f"Test email failed: {integ.last_error or 'unknown error'}")
    return redirect("integrations-home")


# ═══════════════════════════════════════════════════════════════════════════
# DocuSign eSignature + Adobe Acrobat Sign — OAuth connect / callback / disconnect
# ═══════════════════════════════════════════════════════════════════════════

def _start_oauth(request, helper, cookie_name, label):
    """Shared OAuth kickoff for DocuSign / Adobe Sign. Returns an HttpResponse.

    Any signed-in user may connect their own account — connections are
    per-user and each signer e-signs through their own."""
    if not helper.is_configured():
        messages.error(request, f"{label} is not configured (missing API credentials).")
        return redirect(_UI_INTEGRATIONS)
    state = helper.make_state()
    response = redirect(helper.build_authorize_url(state))
    is_secure = request.is_secure()
    response.set_cookie(
        cookie_name, signing.dumps(state),
        max_age=_STATE_MAX_AGE, httponly=True,
        samesite="None" if is_secure else "Lax", secure=is_secure,
    )
    return response


def _validate_state(request, cookie_name):
    state = request.GET.get("state")
    signed = request.COOKIES.get(cookie_name)
    try:
        expected = signing.loads(signed, max_age=_STATE_MAX_AGE) if signed else None
    except (signing.BadSignature, signing.SignatureExpired):
        expected = None
    return bool(state and state == expected)


# ── DocuSign ────────────────────────────────────────────────────────────────
_DS_COOKIE = "docusign_oauth_state"


@login_required
def docusign_connect(request):
    from base.integrations import docusign
    return _start_oauth(request, docusign, _DS_COOKIE, "DocuSign")


@login_required
def docusign_callback(request):
    from base.integrations import docusign
    from base.models_integrations import DocusignAccount

    if request.GET.get("error"):
        messages.error(request, f"DocuSign authorization failed: {request.GET['error']}")
        return redirect(_UI_INTEGRATIONS)
    if not _validate_state(request, _DS_COOKIE):
        messages.error(request, "OAuth state mismatch — please try connecting DocuSign again.")
        return redirect(_UI_INTEGRATIONS)
    code = request.GET.get("code")
    if not code:
        messages.error(request, "DocuSign authorization did not return a code.")
        return redirect(_UI_INTEGRATIONS)
    try:
        tokens = docusign.exchange_code(code)
        access_token = tokens.get("access_token")
        info = docusign.fetch_userinfo(access_token)
        expires_in = int(tokens.get("expires_in", 0) or 0)
        DocusignAccount.objects.update_or_create(
            user=request.user,
            defaults={
                "account_id": info.get("account_id", ""),
                "base_uri": info.get("base_uri", ""),
                "email_address": info.get("email", ""),
                "display_name": info.get("name", ""),
                "access_token": access_token,
                "refresh_token": tokens.get("refresh_token", ""),
                "token_expires_at": timezone.now() + timedelta(seconds=expires_in) if expires_in else None,
                "scope": tokens.get("scope", ""),
                "is_active": True,
                "last_error": "",
            },
        )
        messages.success(request, f"Connected DocuSign account: {info.get('email','')}")
    except Exception as exc:
        logger.exception("DocuSign OAuth callback failed")
        messages.error(request, f"Failed to connect DocuSign: {exc}")
    response = redirect(_UI_INTEGRATIONS)
    response.delete_cookie(_DS_COOKIE)
    return response


@login_required
def docusign_disconnect(request):
    from base.models_integrations import DocusignAccount
    DocusignAccount.objects.filter(user=request.user).delete()
    messages.success(request, "Your DocuSign account was disconnected.")
    return redirect(_UI_INTEGRATIONS)


# ── Adobe Acrobat Sign ───────────────────────────────────────────────────────
_AS_COOKIE = "adobesign_oauth_state"


@login_required
def adobesign_connect(request):
    from base.integrations import adobesign
    return _start_oauth(request, adobesign, _AS_COOKIE, "Adobe Acrobat Sign")


@login_required
def adobesign_callback(request):
    from base.integrations import adobesign
    from base.models_integrations import AdobeSignAccount

    if request.GET.get("error"):
        messages.error(request, f"Adobe Sign authorization failed: {request.GET['error']}")
        return redirect(_UI_INTEGRATIONS)
    if not _validate_state(request, _AS_COOKIE):
        messages.error(request, "OAuth state mismatch — please try connecting Adobe Sign again.")
        return redirect(_UI_INTEGRATIONS)
    code = request.GET.get("code")
    if not code:
        messages.error(request, "Adobe Sign authorization did not return a code.")
        return redirect(_UI_INTEGRATIONS)
    try:
        tokens = adobesign.exchange_code(code)
        expires_in = int(tokens.get("expires_in", 0) or 0)
        AdobeSignAccount.objects.update_or_create(
            user=request.user,
            defaults={
                "api_access_point": tokens.get("api_access_point", ""),
                "access_token": tokens.get("access_token"),
                "refresh_token": tokens.get("refresh_token", ""),
                "token_expires_at": timezone.now() + timedelta(seconds=expires_in) if expires_in else None,
                "scope": adobesign.SCOPES,
                "is_active": True,
                "last_error": "",
            },
        )
        messages.success(request, "Connected Adobe Acrobat Sign account.")
    except Exception as exc:
        logger.exception("Adobe Sign OAuth callback failed")
        messages.error(request, f"Failed to connect Adobe Sign: {exc}")
    response = redirect(_UI_INTEGRATIONS)
    response.delete_cookie(_AS_COOKIE)
    return response


@login_required
def adobesign_disconnect(request):
    from base.models_integrations import AdobeSignAccount
    AdobeSignAccount.objects.filter(user=request.user).delete()
    messages.success(request, "Your Adobe Sign account was disconnected.")
    return redirect(_UI_INTEGRATIONS)
